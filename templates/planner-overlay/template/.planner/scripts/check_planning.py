#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema==4.25.1",
#   "PyYAML==6.0.3",
# ]
# ///
"""Read-only structural checker for planner native records.

This program validates local records, references, content-bound approvals and
evidence fields. It never chooses work, mutates records, runs verification
commands, contacts a model or interprets arbitrary external frameworks.
Unsupported or external content is reported for agent/human review.

Exit codes:
  0  deterministic checks completed without errors
  1  a proven structural or approval invariant failed
  2  unreadable configuration, unsupported schema or invalid invocation
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import yaml
from jsonschema import Draft202012Validator
from yaml.constructor import ConstructorError

CHECKER_VERSION = "0.1.0"
REPORT_VERSION = 1
RECORD_KINDS = ("strategy", "requirement", "milestone", "task", "decision", "change")
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
PLACEHOLDER_RE = re.compile(r"(?i)^(tbd|todo|replace me|replace-me)$")
EXTERNAL_REF_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""

    def construct_mapping(self, node, deep=False):  # noqa: FBT001,FBT002
        if not isinstance(node, yaml.MappingNode):
            raise ConstructorError(
                None, None, "expected a mapping node", node.start_mark
            )
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "mapping keys must be scalar/hashable",
                    key_node.start_mark,
                ) from None
            if duplicate:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


@dataclass
class Finding:
    rule: str
    severity: str
    locator: str
    message: str

    def as_dict(self) -> dict:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "locator": self.locator,
            "message": self.message,
        }


@dataclass
class Record:
    path: Path
    rel: str
    data: dict
    kind: str
    id: str
    scope: dict
    execution: dict

    @property
    def state(self) -> str:
        return str(self.execution.get("state", ""))


@dataclass
class Adopted:
    id: str
    kind: str
    owner: str
    ref: str
    locator: str
    format: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    coverage: dict = field(default_factory=dict)
    project: dict = field(default_factory=dict)
    exit_code: int = 0

    def add(self, rule: str, severity: str, locator: str, message: str) -> None:
        self.findings.append(Finding(rule, severity, locator, message))

    def error(self, rule: str, locator: str, message: str) -> None:
        self.add(rule, "error", locator, message)

    def warning(self, rule: str, locator: str, message: str) -> None:
        self.add(rule, "warning", locator, message)

    def manual(self, rule: str, locator: str, message: str) -> None:
        self.add(rule, "manual_review", locator, message)

    def counts(self) -> dict:
        result = {"error": 0, "warning": 0, "manual_review": 0}
        for finding in self.findings:
            result[finding.severity] = result.get(finding.severity, 0) + 1
        return result


def canonical_scope(scope: dict) -> str:
    return json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def scope_digest(scope: dict) -> str:
    return hashlib.sha256(canonical_scope(scope).encode("utf-8")).hexdigest()


def load_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.load(handle, Loader=UniqueKeyLoader)  # noqa: S506 - SafeLoader subclass


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter, body) or (None, text) when no frontmatter is present."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            raw = "".join(lines[1:index])
            body = "".join(lines[index + 1 :])
            return yaml.load(raw, Loader=UniqueKeyLoader), body  # noqa: S506
    raise ValueError("frontmatter starts with --- but has no closing ---")


def safe_relative(root: Path, ref: str) -> tuple[Path | None, str | None]:
    """Resolve a project-relative reference without escaping the project root."""
    if not ref or ref.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", ref):
        return None, "absolute paths are not allowed"
    try:
        candidate = (root / ref).resolve()
    except (OSError, RuntimeError) as exc:
        return None, f"path cannot be resolved: {exc}"
    root_resolved = root.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError:
        return None, "path escapes the configured project root"
    return candidate, None


def is_external_ref(ref: str) -> bool:
    if EXTERNAL_REF_RE.match(ref):
        return True
    parsed = urlparse(ref)
    return bool(parsed.scheme and parsed.scheme not in {"", "file"})


def path_part(ref: str) -> str:
    return ref.split("#", 1)[0]


class PlannerCheck:
    def __init__(self, project: Path, source_revision: str | None) -> None:
        self.root = project.resolve()
        self.source_revision = source_revision
        self.report = Report()
        self.config: dict = {}
        self.config_path = self.root / "planning" / "planner.yaml"
        self.schema_dir = Path(__file__).resolve().parent.parent / "schemas"
        self.record_schema: dict = {}
        self.project_schema: dict = {}
        self.records: dict[str, Record] = {}
        self.records_by_kind: dict[str, list[Record]] = {kind: [] for kind in RECORD_KINDS}
        self.embedded: dict[str, dict] = {}
        self.adopted: dict[str, Adopted] = {}
        self.aliases: dict[str, str] = {}
        self.alias_notes: dict[str, str] = {}
        self.discovered_files: set[Path] = set()
        self.unparsed_markdown: list[str] = []
        self.evidence_index: dict[str, tuple[Record, dict]] = {}
        self.authority_files: dict[Path, list[dict]] = {}
        self.approval_cache: dict[str, bool] = {}
        self.identity_reviewed: set[str] = set()

    # ------------------------------------------------------------------ load
    def locator(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def load_schemas(self) -> bool:
        try:
            self.record_schema = json.loads(
                (self.schema_dir / "record.schema.json").read_text(encoding="utf-8")
            )
            self.project_schema = json.loads(
                (self.schema_dir / "project.schema.json").read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            self.report.error(
                "SCHEMA_UNAVAILABLE",
                self.locator(self.schema_dir),
                f"cannot load planner schemas: {exc}",
            )
            self.report.exit_code = 2
            return False
        return True

    def load_config(self) -> bool:
        locator = self.locator(self.config_path)
        if not self.config_path.is_file():
            self.report.error(
                "CONFIG_MISSING",
                locator,
                "planning/planner.yaml is missing; run INIT before checking planning",
            )
            self.report.exit_code = 2
            return False
        try:
            data = load_yaml(self.config_path)
        except (OSError, yaml.YAMLError, ValueError) as exc:
            self.report.error("CONFIG_UNREADABLE", locator, f"cannot parse YAML: {exc}")
            self.report.exit_code = 2
            return False
        if not isinstance(data, dict):
            self.report.error("CONFIG_UNREADABLE", locator, "configuration must be a mapping")
            self.report.exit_code = 2
            return False
        validator = Draft202012Validator(self.project_schema)
        errors = sorted(validator.iter_errors(data), key=lambda err: list(err.path))
        if errors:
            for error in errors:
                where = ".".join(str(part) for part in error.path) or "<root>"
                self.report.error(
                    "CONFIG_SCHEMA",
                    f"{locator}#{where}",
                    error.message,
                )
            self.report.exit_code = 2
            return False
        self.config = data
        self.report.project = {
            "project_id": data.get("project_id"),
            "name": data.get("name"),
            "category": data.get("category"),
            "root": str(self.root),
        }
        return True

    # ----------------------------------------------------------- authorities
    def check_config_semantics(self) -> None:
        locator = self.locator(self.config_path)
        roles = set(self.config.get("roles", {}))
        content_root, problem = safe_relative(self.root, str(self.config.get("content_root", "")))
        if problem:
            self.report.error("UNSAFE_CONTENT_ROOT", locator, problem)
        elif content_root is None or not content_root.exists():
            self.report.warning(
                "CONTENT_ROOT_MISSING",
                locator,
                f"content root {self.config.get('content_root')!r} does not exist yet",
            )

        if str(self.config.get("project_id")) == "replace-me" or str(
            self.config.get("name")
        ).strip().lower() == "replace me":
            self.report.warning(
                "PLACEHOLDER_CONFIG",
                locator,
                "project identity is still the blank-asset placeholder",
            )

        seen: set[tuple[str, str, str]] = set()
        seen_roots: dict[tuple[str, str], dict] = {}
        collection_roots: list[tuple[str, Path]] = []
        for authority in self.config.get("authorities", []):
            kind = authority.get("kind")
            owner = authority.get("owner")
            if owner not in roles:
                self.report.error(
                    "UNKNOWN_AUTHORITY_OWNER",
                    locator,
                    f"authority {kind!r} uses owner {owner!r}, which is not a configured role",
                )
            if "root" in authority:
                key = (kind, owner, authority["root"])
                if key in seen:
                    self.report.error(
                        "DUPLICATE_AUTHORITY",
                        locator,
                        f"duplicate authority binding for {kind!r} at {authority['root']!r}",
                    )
                seen.add(key)
                root_key = (kind, authority["root"])
                if root_key in seen_roots:
                    self.report.error(
                        "DUPLICATE_AUTHORITY",
                        locator,
                        f"authority {kind!r} is bound to {authority['root']!r} more than once",
                    )
                seen_roots[root_key] = authority
                resolved, problem = safe_relative(self.root, authority["root"])
                if problem:
                    self.report.error(
                        "UNSAFE_AUTHORITY_ROOT",
                        locator,
                        f"authority {kind!r}: {problem}",
                    )
                elif resolved is not None and kind not in {"roadmap", "evidence"}:
                    collection_roots.append((kind, resolved))
            else:
                if is_external_ref(authority["ref"]):
                    if authority.get("format") != "issue":
                        self.report.error(
                            "UNSAFE_AUTHORITY_REF",
                            locator,
                            f"adopted {authority.get('id')!r} uses an external URI but "
                            f"format {authority.get('format')!r}; use format 'issue' or a "
                            "local path",
                        )
                else:
                    resolved, problem = safe_relative(self.root, authority["ref"])
                    if problem:
                        self.report.error(
                            "UNSAFE_AUTHORITY_REF",
                            locator,
                            f"adopted {authority.get('id')!r}: {problem}",
                        )

        for index, (kind_a, root_a) in enumerate(collection_roots):
            for kind_b, root_b in collection_roots[index + 1 :]:
                if root_a == root_b:
                    continue
                if root_a in root_b.parents or root_b in root_a.parents:
                    self.report.error(
                        "OVERLAPPING_AUTHORITY_ROOTS",
                        locator,
                        f"{kind_a} root {root_a} and {kind_b} root {root_b} overlap; every "
                        "concept must have one unambiguous authority",
                    )

        aliases = self.config.get("aliases") or []
        for alias in aliases:
            alias_id = alias.get("id")
            target = alias.get("target")
            if alias_id in self.aliases:
                self.report.error(
                    "DUPLICATE_ALIAS",
                    locator,
                    f"alias {alias_id!r} is declared more than once",
                )
            self.aliases[alias_id] = target
            if alias.get("note"):
                self.alias_notes[alias_id] = alias["note"]

    def authority_paths(self) -> list[tuple[dict, Path | None, str | None]]:
        result = []
        for authority in self.config.get("authorities", []):
            if "root" in authority:
                resolved, problem = safe_relative(self.root, authority["root"])
                result.append((authority, resolved, problem))
            elif is_external_ref(authority["ref"]):
                result.append((authority, None, "external"))
            else:
                resolved, problem = safe_relative(self.root, authority["ref"])
                result.append((authority, resolved, problem))
        return result

    # -------------------------------------------------------------- discover
    def discover(self) -> None:
        roots: dict[Path, list[dict]] = {}
        explicit_native: list[tuple[dict, Path]] = []
        for authority, path, problem in self.authority_paths():
            if problem == "external" and "ref" in authority:
                if authority.get("format") == "issue":
                    adopted = Adopted(
                        id=authority["id"],
                        kind=authority["kind"],
                        owner=authority["owner"],
                        ref=authority["ref"],
                        locator=authority.get("locator", ""),
                        format="issue",
                    )
                    if adopted.id in self.adopted:
                        self.report.error(
                            "DUPLICATE_ADOPTED_ID",
                            authority["ref"],
                            f"adopted record {adopted.id} is declared more than once",
                        )
                    self.adopted[adopted.id] = adopted
                    self.report.manual(
                        "EXTERNAL_AUTHORITY_UNVERIFIED",
                        authority["ref"],
                        f"issue record {adopted.id} is mutable and was not fetched; require a "
                        "dated export/content identity and a fresh read before readiness",
                    )
                continue
            if problem or path is None:
                continue
            if "root" in authority:
                kind = authority["kind"]
                if not path.exists():
                    if kind in {"roadmap", "evidence"}:
                        self.report.warning(
                            "VIEW_MISSING",
                            self.locator(path),
                            f"configured {kind} path does not exist yet",
                        )
                    else:
                        self.report.warning(
                            "AUTHORITY_ROOT_MISSING",
                            self.locator(path),
                            f"configured {kind} authority root does not exist yet",
                        )
                    continue
                if kind in {"roadmap", "evidence"}:
                    continue
                roots.setdefault(path, []).append(authority)
            else:
                if not path.exists():
                    self.report.error(
                        "ADOPTED_SOURCE_MISSING",
                        self.locator(path),
                        f"adopted {authority['kind']} record {authority['id']} has no readable source",
                    )
                    continue
                if authority["format"] == "native":
                    explicit_native.append((authority, path))
                else:
                    adopted = Adopted(
                        id=authority["id"],
                        kind=authority["kind"],
                        owner=authority["owner"],
                        ref=authority["ref"],
                        locator=authority.get("locator", ""),
                        format=authority["format"],
                    )
                    if adopted.id in self.adopted:
                        self.report.error(
                            "DUPLICATE_ADOPTED_ID",
                            self.locator(path),
                            f"adopted record {adopted.id} is declared more than once",
                        )
                    self.adopted[adopted.id] = adopted
                    self.report.manual(
                        "EXTERNAL_AUTHORITY_UNPARSED",
                        self.locator(path),
                        f"{adopted.format} record {adopted.id} is authoritative but was not "
                        "structurally parsed; confirm its revision and locator during review",
                    )

        files: dict[Path, list[dict]] = {}
        for root_path, authorities in roots.items():
            if root_path.is_file():
                candidates = [root_path]
            else:
                candidates = sorted(root_path.rglob("*.md"))
            for candidate in candidates:
                if candidate.is_symlink():
                    self.report.warning(
                        "SYMLINK_SKIPPED",
                        self.locator(candidate),
                        "symlinked record paths are not followed; use a real project-relative file",
                    )
                    continue
                if not candidate.is_file():
                    continue
                rel = self.locator(candidate)
                resolved, problem = safe_relative(self.root, rel)
                if problem or resolved is None:
                    self.report.error(
                        "UNSAFE_RECORD_PATH", rel, problem or "path cannot be resolved"
                    )
                    continue
                files.setdefault(candidate.resolve(), []).extend(authorities)
        self.authority_files = files

        for candidate, authorities in sorted(files.items(), key=lambda item: str(item[0])):
            self.load_record_file(candidate, authorities)

        for authority, path in explicit_native:
            self.load_record_file(path.resolve(), [authority])
            record = self.records.get(authority["id"])
            if (
                record is None
                or record.path.resolve() != path.resolve()
                or record.kind != authority["kind"]
            ):
                self.report.error(
                    "ADOPTED_NATIVE_MISMATCH",
                    self.locator(path),
                    f"explicit native authority {authority['id']} did not produce a matching "
                    f"{authority['kind']} native record",
                )

        for adopted in self.adopted.values():
            if adopted.id in self.records:
                self.report.error(
                    "ID_COLLISION",
                    adopted.ref,
                    f"adopted record {adopted.id} collides with a native record",
                )

        for authority, path, problem in self.authority_paths():
            if problem and path is not None:
                self.report.error(
                    "UNSAFE_AUTHORITY",
                    self.config_path.as_posix(),
                    f"authority {authority.get('kind')}: {problem}",
                )

    def load_record_file(self, path: Path, authorities: list[dict]) -> None:
        rel = self.locator(path)
        if path in self.discovered_files:
            return
        self.discovered_files.add(path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            self.report.error("RECORD_UNREADABLE", rel, f"cannot read file: {exc}")
            return
        try:
            data, _body = split_frontmatter(text)
        except (yaml.YAMLError, ValueError) as exc:
            self.report.error("FRONTMATTER_INVALID", rel, f"cannot parse frontmatter: {exc}")
            return
        if data is None:
            self.unparsed_markdown.append(rel)
            self.report.manual(
                "UNPARSED_MARKDOWN",
                rel,
                "Markdown in a configured native authority has no frontmatter; "
                "confirm whether it is a record, a view or background material",
            )
            return
        if not isinstance(data, dict):
            self.report.error("FRONTMATTER_INVALID", rel, "frontmatter must be a mapping")
            return
        if "schema_version" not in data and "kind" not in data:
            self.unparsed_markdown.append(rel)
            self.report.manual(
                "UNPARSED_MARKDOWN",
                rel,
                "frontmatter is not a planner record; confirm the record's authority",
            )
            return
        schema_version = data.get("schema_version")
        if schema_version != 1:
            self.report.error(
                "UNSUPPORTED_SCHEMA",
                rel,
                f"unsupported native record schema_version {schema_version!r}; v0.1 supports 1",
            )
            self.report.exit_code = 2
            return
        validator = Draft202012Validator(self.record_schema)
        errors = sorted(validator.iter_errors(data), key=lambda err: list(err.path))
        for error in errors:
            where = ".".join(str(part) for part in error.path) or "<root>"
            self.report.error("RECORD_SCHEMA", f"{rel}#{where}", error.message)
        kind = data.get("kind")
        record_id = data.get("id")
        if not isinstance(kind, str) or not isinstance(record_id, str):
            return
        expected_kinds = {authority["kind"] for authority in authorities}
        if kind not in expected_kinds:
            self.report.error(
                "RECORD_OUTSIDE_AUTHORITY",
                rel,
                f"record kind {kind!r} is not authorized by its configured authority "
                f"({sorted(expected_kinds)})",
            )
            return
        if not ID_RE.match(record_id):
            return
        if record_id in self.records:
            self.report.error(
                "DUPLICATE_ID",
                rel,
                f"record ID {record_id} already exists at {self.records[record_id].rel}",
            )
            return
        record = Record(
            path=path,
            rel=rel,
            data=data,
            kind=kind,
            id=record_id,
            scope=data.get("scope") if isinstance(data.get("scope"), dict) else {},
            execution=data.get("execution") if isinstance(data.get("execution"), dict) else {},
        )
        self.records[record_id] = record
        self.records_by_kind.setdefault(kind, []).append(record)

        owner = data.get("owner")
        if owner not in set(self.config.get("roles", {})):
            self.report.error(
                "UNKNOWN_OWNER",
                rel,
                f"owner {owner!r} is not a configured role",
            )
        if record_id.endswith("-000"):
            self.report.warning(
                "PLACEHOLDER_RECORD",
                rel,
                f"identifier {record_id} is a blank-asset placeholder; replace it before use",
            )
            if record.state in {"approved", "active", "achieved", "ready", "accepted", "applied"}:
                self.report.error(
                    "PLACEHOLDER_APPROVED",
                    rel,
                    f"placeholder record {record_id} cannot be {record.state!r}",
                )

    # ------------------------------------------------------------- indexing
    def index_embedded(self) -> None:
        for strategy in self.records_by_kind.get("strategy", []):
            objectives = strategy.scope.get("objectives")
            if not isinstance(objectives, list):
                continue
            for objective in objectives:
                if not isinstance(objective, dict):
                    continue
                self.add_embedded(objective.get("id"), "objective", strategy)
                for outcome in objective.get("outcomes") or []:
                    if isinstance(outcome, dict):
                        self.add_embedded(outcome.get("id"), "outcome", strategy)

    def add_embedded(self, embedded_id: object, kind: str, owner: Record) -> None:
        if not isinstance(embedded_id, str) or not ID_RE.match(embedded_id):
            return
        if embedded_id in self.records or embedded_id in self.embedded:
            self.report.error(
                "DUPLICATE_ID",
                owner.rel,
                f"embedded {kind} ID {embedded_id} is not unique",
            )
            return
        self.embedded[embedded_id] = {"kind": kind, "owner": owner}

    def index_aliases(self) -> None:
        for alias_id, target in self.aliases.items():
            if alias_id in self.records or alias_id in self.embedded or alias_id in self.adopted:
                self.report.error(
                    "DUPLICATE_ID",
                    self.locator(self.config_path),
                    f"alias {alias_id} collides with an existing canonical or adopted ID",
                )
            if target is None:
                continue
            if (
                target not in self.records
                and target not in self.embedded
                and target not in self.adopted
                and target not in self.aliases
            ):
                self.report.error(
                    "DANGLING_ALIAS",
                    self.locator(self.config_path),
                    f"alias {alias_id} targets unknown record {target}",
                )

        reported_cycles: set[tuple[str, ...]] = set()
        for alias_id in self.aliases:
            seen: list[str] = []
            current = alias_id
            while current in self.aliases:
                if current in seen:
                    cycle = tuple(sorted(seen[seen.index(current) :]))
                    if cycle not in reported_cycles:
                        reported_cycles.add(cycle)
                        self.report.error(
                            "ALIAS_CYCLE",
                            self.locator(self.config_path),
                            "alias cycle: " + " -> ".join(seen + [current]),
                        )
                    break
                seen.append(current)
                current = self.aliases[current]

    def resolve(self, ref: object) -> tuple[str, object] | None:
        if not isinstance(ref, str):
            return None
        visited: set[str] = set()
        while ref in self.aliases:
            if ref in visited:
                return None
            visited.add(ref)
            ref = self.aliases[ref]
        if ref in self.records:
            return "record", self.records[ref]
        if ref in self.embedded:
            return "embedded", self.embedded[ref]
        if ref in self.adopted:
            return "adopted", self.adopted[ref]
        return None

    def ref_kind(self, resolved: tuple[str, object]) -> str:
        category, value = resolved
        if category == "record":
            return value.kind
        if category == "embedded":
            return value["kind"]
        return value.kind

    def check_ref(
        self,
        ref: object,
        expected: set[str],
        locator: str,
        *,
        rule: str = "REFERENCE",
        allow_external: bool = False,
    ) -> tuple[str, object] | None:
        resolved = self.resolve(ref)
        if resolved is None:
            if allow_external and isinstance(ref, str) and is_external_ref(ref):
                self.report.manual(
                    "EXTERNAL_REFERENCE_UNRESOLVED",
                    locator,
                    f"external reference {ref!r} cannot be resolved structurally",
                )
                return None
            self.report.error(
                f"{rule}_DANGLING",
                locator,
                f"reference {ref!r} does not resolve to a configured record",
            )
            return None
        actual = self.ref_kind(resolved)
        if expected and actual not in expected:
            self.report.error(
                f"{rule}_TYPE",
                locator,
                f"reference {ref!r} resolves to {actual!r}, expected {sorted(expected)}",
            )
        if resolved[0] == "adopted":
            self.report.manual(
                "EXTERNAL_REFERENCE_UNVERIFIED",
                locator,
                f"reference {ref!r} points to an adopted {actual} source; its content and "
                "revision require review",
            )
        return resolved

    # ------------------------------------------------------------ references
    def check_references(self) -> None:
        for record in self.records.values():
            self.check_record_references(record)

    def check_record_references(self, record: Record) -> None:
        scope = record.scope
        loc = record.rel
        if record.kind == "strategy":
            self.check_embedded_criteria(record)
        elif record.kind == "requirement":
            for ref in scope.get("objectives") or []:
                self.check_ref(ref, {"objective", "outcome"}, loc)
            for ref in scope.get("supersedes") or []:
                self.check_ref(ref, {"requirement"}, loc)
            self.check_criteria_and_verification(record, "acceptance")
        elif record.kind == "milestone":
            for ref in scope.get("objectives") or []:
                self.check_ref(ref, {"objective"}, loc)
            for ref in scope.get("outcomes") or []:
                self.check_ref(ref, {"outcome"}, loc)
            for ref in scope.get("requirements") or []:
                self.check_ref(ref, {"requirement"}, loc)
            package_ids = set()
            for package in scope.get("packages") or []:
                package_id = package.get("id") if isinstance(package, dict) else None
                if package_id in package_ids:
                    self.report.error(
                        "DUPLICATE_PACKAGE_ID",
                        loc,
                        f"package ID {package_id} is repeated in one milestone",
                    )
                package_ids.add(package_id)
            for dependency in scope.get("depends_on") or []:
                self.check_dependency(dependency, loc, record.id)
            self.check_criteria_and_verification(record, "exit_criteria")
        elif record.kind == "task":
            self.check_ref(scope.get("objective"), {"objective", "outcome"}, loc)
            milestone_resolved = self.check_ref(
                scope.get("milestone"), {"milestone"}, loc
            )
            for ref in scope.get("requirements") or []:
                self.check_ref(ref, {"requirement"}, loc)
            if scope.get("package"):
                if milestone_resolved and milestone_resolved[0] == "record":
                    milestone = milestone_resolved[1]
                    packages = {
                        pkg.get("id")
                        for pkg in (milestone.scope.get("packages") or [])
                        if isinstance(pkg, dict)
                    }
                    if scope["package"] not in packages:
                        self.report.error(
                            "INVALID_PACKAGE",
                            loc,
                            f"package {scope['package']!r} is not defined by parent milestone "
                            f"{milestone.id}",
                        )
                else:
                    self.report.manual(
                        "PACKAGE_PARENT_UNVERIFIED",
                        loc,
                        f"package {scope['package']!r} cannot be verified against an adopted "
                        "or unresolved milestone",
                    )
            for dependency in scope.get("depends_on") or []:
                self.check_dependency(dependency, loc, record.id)
            for context in scope.get("context") or []:
                if not isinstance(context, dict):
                    continue
                ref = str(context.get("ref", ""))
                if is_external_ref(ref) or ref.startswith(("gh:", "issue:", "openspec:")):
                    self.report.manual(
                        "EXTERNAL_CONTEXT",
                        loc,
                        f"context {ref!r} is external; confirm its revision before readiness",
                    )
                    continue
                target, problem = safe_relative(self.root, path_part(ref))
                if problem:
                    self.report.error(
                        "UNSAFE_CONTEXT_PATH",
                        loc,
                        f"context {ref!r}: {problem}",
                    )
                elif target is not None and not target.exists():
                    self.report.error(
                        "MISSING_CONTEXT",
                        loc,
                        f"context {ref!r} does not exist",
                    )
                else:
                    revision = str(context.get("revision", "")).strip()
                    if (
                        self.source_revision
                        and revision
                        and revision not in {self.source_revision, "working-tree", "HEAD"}
                    ):
                        self.report.warning(
                            "CONTEXT_REVISION_STALE",
                            loc,
                            f"context {ref!r} revision {revision!r} differs from the requested "
                            f"source revision {self.source_revision!r}",
                        )
            self.check_criteria_and_verification(record, "acceptance")
        elif record.kind == "decision":
            for target in scope.get("targets") or []:
                if not isinstance(target, dict):
                    continue
                target_id = target.get("record")
                target_resolved = self.check_ref(target_id, set(), loc)
                if target_resolved and target_resolved[0] == "record":
                    expected = scope_digest(target_resolved[1].scope)
                    if target.get("scope_sha256") != expected:
                        self.report.warning(
                            "DECISION_TARGET_DRIFT",
                            loc,
                            f"decision target {target_id} records a different scope digest "
                            "than the current record; the historical approval may be stale",
                        )
            for ref in scope.get("supersedes") or []:
                self.check_ref(ref, {"decision"}, loc)
            delegation = scope.get("delegation")
            if isinstance(delegation, dict):
                for ref in delegation.get("covers") or []:
                    self.check_ref(
                        ref, {"task", "milestone", "objective", "requirement"}, loc
                    )
                self.report.manual(
                    "DELEGATED_AUTHORIZATION",
                    loc,
                    "bounded delegation is prose; conformance requires human review, not "
                    "machine proof",
                )
        elif record.kind == "change":
            for ref in scope.get("affected") or []:
                self.check_ref(ref, set(), loc)
            state = record.state
            disposition = record.execution.get("disposition_decision")
            if state == "applied" and not record.execution.get("applied_revision"):
                self.report.error(
                    "CHANGE_APPLIED_REVISION_MISSING",
                    loc,
                    "applied change must record the applied_revision",
                )
            if state in {"rejected", "deferred"} and not record.scope.get("revisit_trigger"):
                self.report.error(
                    "CHANGE_REVISIT_TRIGGER_MISSING",
                    loc,
                    f"change state {state!r} must retain a revisit trigger",
                )
            if state in {"approved", "rejected", "deferred", "applied"}:
                if not disposition:
                    self.report.error(
                        "CHANGE_DISPOSITION_MISSING",
                        loc,
                        f"change state {state!r} requires a disposition decision reference",
                    )
                else:
                    resolved = self.check_ref(disposition, {"decision"}, loc)
                    if resolved and resolved[0] == "record":
                        decision = resolved[1]
                        if decision.state != "accepted":
                            self.report.error(
                                "CHANGE_DISPOSITION_NOT_ACCEPTED",
                                loc,
                                f"disposition decision {decision.id} is {decision.state!r}, "
                                "not 'accepted'",
                            )
                        else:
                            self.validate_decision_provenance(
                                decision, "CHANGE_DISPOSITION"
                            )
                        matching = [
                            target
                            for target in decision.scope.get("targets") or []
                            if isinstance(target, dict) and target.get("record") == record.id
                        ]
                        if not matching or all(
                            target.get("scope_sha256") != scope_digest(record.scope)
                            for target in matching
                        ):
                            self.report.error(
                                "CHANGE_APPROVAL_STALE",
                                loc,
                                f"change state {state!r} is not bound to the exact current "
                                f"change scope by {decision.id}",
                            )

    def check_dependency(self, dependency: object, locator: str, record_id: str) -> None:
        if isinstance(dependency, str):
            resolved = self.check_ref(dependency, {"task", "milestone"}, locator)
            if resolved and resolved[0] == "record" and resolved[1].id == record_id:
                self.report.error(
                    "SELF_DEPENDENCY", locator, f"record {record_id} depends on itself"
                )
            return
        if isinstance(dependency, dict):
            evidence_ref = str(dependency.get("evidence_ref", ""))
            if not evidence_ref:
                return
            if evidence_ref in self.evidence_index:
                record, evidence = self.evidence_index[evidence_ref]
                criterion = str(dependency.get("criterion", ""))
                if criterion not in (evidence.get("criteria") or []):
                    self.report.error(
                        "GATE_EVIDENCE_CRITERION",
                        locator,
                        f"gate evidence {evidence_ref} does not cite the required criterion "
                        f"{criterion!r}",
                    )
                if evidence.get("result") != "pass":
                    self.report.warning(
                        "GATE_EVIDENCE_NOT_PASS",
                        locator,
                        f"gate evidence {evidence_ref} result is {evidence.get('result')!r}",
                    )
                return
            target, problem = safe_relative(self.root, path_part(evidence_ref))
            if problem is None and target is not None and target.exists():
                self.report.manual(
                    "GATE_EVIDENCE_MANUAL",
                    locator,
                    f"gate evidence {evidence_ref!r} exists but has no structured result",
                )
            else:
                self.report.error(
                    "GATE_EVIDENCE_MISSING",
                    locator,
                    f"gate evidence {evidence_ref!r} cannot be found",
                )

    def check_embedded_criteria(self, record: Record) -> None:
        for objective in record.scope.get("objectives") or []:
            if not isinstance(objective, dict):
                continue
            for outcome in objective.get("outcomes") or []:
                if not isinstance(outcome, dict):
                    continue
                for key in ("description", "baseline", "target_or_rubric", "verification", "review_horizon"):
                    value = outcome.get(key)
                    if isinstance(value, str) and PLACEHOLDER_RE.match(value.strip()):
                        self.report.warning(
                            "PLACEHOLDER_VALUE",
                            record.rel,
                            f"{outcome.get('id')}.{key} still contains placeholder text",
                        )
                baseline = str(outcome.get("baseline", "")).strip().lower()
                if baseline in {"", "unknown"}:
                    self.report.warning(
                        "BASELINE_UNKNOWN",
                        record.rel,
                        f"{outcome.get('id')} has no measured baseline; record why it is unknown",
                    )

    def criteria_ids(self, record: Record) -> set[str]:
        if record.kind in {"requirement"}:
            entries = record.scope.get("acceptance") or []
        elif record.kind in {"milestone"}:
            entries = record.scope.get("exit_criteria") or []
        elif record.kind == "task":
            entries = record.scope.get("acceptance") or []
        else:
            entries = []
        result = set()
        for entry in entries:
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                result.add(entry["id"])
        return result

    def check_reviewer(self, reviewer: object, locator: str) -> None:
        if not isinstance(reviewer, str) or not reviewer.strip():
            return
        roles = self.config.get("roles", {})
        known = set(roles) | {str(value) for value in roles.values()}
        if reviewer not in known:
            self.report.warning(
                "UNKNOWN_REVIEWER",
                locator,
                f"reviewer {reviewer!r} is not a configured role key or role name",
            )

    def check_criteria_and_verification(self, record: Record, key: str) -> None:
        entries = record.scope.get(key) or []
        seen: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            criterion_id = entry.get("id")
            if criterion_id in seen:
                self.report.error(
                    "DUPLICATE_CRITERION",
                    record.rel,
                    f"criterion ID {criterion_id} is repeated",
                )
            seen.add(criterion_id)
            statement = entry.get("statement")
            if isinstance(statement, str) and PLACEHOLDER_RE.match(statement.strip()):
                self.report.warning(
                    "PLACEHOLDER_VALUE",
                    record.rel,
                    f"criterion {criterion_id} still contains placeholder text",
                )
        covered: set[str] = set()
        for verification in record.scope.get("verification") or []:
            if not isinstance(verification, dict):
                continue
            self.check_reviewer(verification.get("reviewer"), record.rel)
            for criterion in verification.get("criteria") or []:
                if criterion not in seen:
                    self.report.error(
                        "VERIFICATION_UNKNOWN_CRITERION",
                        record.rel,
                        f"verification references unknown criterion {criterion}",
                    )
                covered.add(criterion)
        missing = seen - covered
        for criterion in sorted(missing):
            self.report.error(
                "CRITERION_UNVERIFIED",
                record.rel,
                f"criterion {criterion} has no verification mapping",
            )

    # --------------------------------------------------------------- state
    def approval_entries(self, record: Record) -> list:
        if record.kind == "task":
            entries = record.scope.get("approvals")
        else:
            entries = record.execution.get("approvals")
        return entries if isinstance(entries, list) else []

    def valid_date(self, value: object) -> bool:
        if not isinstance(value, str) or not DATE_RE.match(value):
            return False
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
        return True

    def validate_decision_provenance(self, decision: Record, prefix: str) -> bool:
        actor = str(decision.execution.get("actor", "")).strip()
        source = str(decision.execution.get("approval_source", "")).strip()
        decided_at = decision.execution.get("decided_at")
        if not actor or not source or not self.valid_date(decided_at):
            self.report.error(
                f"{prefix}_PROVENANCE_INCOMPLETE",
                decision.rel,
                "accepted decision requires a human actor, ISO calendar date and approval_source",
            )
            self.report.manual(
                "APPROVAL_IDENTITY_UNVERIFIED",
                decision.rel,
                "the checker cannot authenticate the recorded human actor or consent",
            )
            return False
        if decision.id not in self.identity_reviewed:
            self.identity_reviewed.add(decision.id)
            self.report.manual(
                "APPROVAL_IDENTITY_UNVERIFIED",
                decision.rel,
                "actor, date and approval source are recorded, but the checker cannot "
                "authenticate identity or consent; verify through human/Git review",
            )
        return True

    def check_states(self) -> None:
        for record in self.records.values():
            if self.approval_entries(record):
                self.verify_approvals(record)
        for decision in self.records_by_kind.get("decision", []):
            if decision.state == "accepted":
                self.validate_decision_provenance(decision, "APPROVAL")
        for ref in self.config.get("task_order") or []:
            resolved = self.resolve(ref)
            if resolved is None or self.ref_kind(resolved) != "task":
                self.report.error(
                    "TASK_ORDER_UNKNOWN",
                    self.locator(self.config_path),
                    f"task_order entry {ref!r} does not resolve to a task",
                )
        active_milestones = [
            record
            for record in self.records_by_kind.get("milestone", [])
            if record.state == "active"
        ]
        if len(active_milestones) > 1:
            self.report.error(
                "MULTIPLE_ACTIVE_MILESTONES",
                self.locator(self.config_path),
                "more than one milestone is active: "
                + ", ".join(record.id for record in active_milestones),
            )
        current = self.config.get("current_milestone")
        if current:
            resolved = self.resolve(current)
            if resolved is not None and resolved[0] == "adopted":
                if self.ref_kind(resolved) != "milestone":
                    self.report.error(
                        "CURRENT_MILESTONE_UNKNOWN",
                        self.locator(self.config_path),
                        f"current_milestone {current!r} is not a milestone",
                    )
                else:
                    self.report.manual(
                        "CURRENT_MILESTONE_EXTERNAL",
                        self.locator(self.config_path),
                        "current milestone is adopted; confirm its active state and approval "
                        "before relying on it",
                    )
            elif resolved is None or resolved[0] != "record" or self.ref_kind(resolved) != "milestone":
                self.report.error(
                    "CURRENT_MILESTONE_UNKNOWN",
                    self.locator(self.config_path),
                    f"current_milestone {current!r} does not resolve to a milestone",
                )
            elif resolved[1].state != "active":
                self.report.error(
                    "CURRENT_MILESTONE_NOT_ACTIVE",
                    self.locator(self.config_path),
                    f"current_milestone {current} is {resolved[1].state!r}, not 'active'",
                )
            elif len(active_milestones) == 1 and active_milestones[0].id != current:
                self.report.error(
                    "CURRENT_MILESTONE_MISMATCH",
                    self.locator(self.config_path),
                    f"current_milestone is {current} but {active_milestones[0].id} is active",
                )
        elif len(active_milestones) == 1:
            self.report.warning(
                "CURRENT_MILESTONE_UNSET",
                self.locator(self.config_path),
                f"{active_milestones[0].id} is active but current_milestone is not set",
            )

        for record in self.records.values():
            if record.state == "blocked" and not record.execution.get("blockers"):
                self.report.error(
                    "BLOCKED_WITHOUT_REASON",
                    record.rel,
                    "blocked state requires at least one blocker",
                )
            if record.state == "cancelled" and not (
                record.execution.get("blockers") or record.execution.get("progress_notes")
            ):
                self.report.error(
                    "CANCELLED_WITHOUT_REASON",
                    record.rel,
                    "cancelled state requires a reason in blockers or progress_notes",
                )

        self.check_strategy_states()
        self.check_requirement_states()
        self.check_milestone_states()
        self.check_task_states()

    def check_strategy_states(self) -> None:
        for strategy in self.records_by_kind.get("strategy", []):
            objectives = []
            outcomes = []
            for objective in strategy.scope.get("objectives") or []:
                if not isinstance(objective, dict):
                    continue
                objectives.append(objective.get("id"))
                for outcome in objective.get("outcomes") or []:
                    if isinstance(outcome, dict):
                        outcomes.append(outcome.get("id"))
            items = strategy.execution.get("items")
            if not isinstance(items, dict):
                items = {}
            for embedded_id in objectives + outcomes:
                if embedded_id not in items:
                    self.report.error(
                        "STRATEGY_ITEM_STATE_MISSING",
                        strategy.rel,
                        f"{embedded_id} has no execution state in strategy items",
                    )
            for embedded_id, item in items.items():
                if embedded_id not in objectives + outcomes:
                    self.report.error(
                        "STRATEGY_ITEM_UNKNOWN",
                        strategy.rel,
                        f"strategy item {embedded_id!r} does not match an embedded objective "
                        "or outcome",
                    )
                if not isinstance(item, dict):
                    continue
                if item.get("state") == "achieved":
                    evidence = item.get("evidence") or []
                    if not any(
                        isinstance(entry, dict) and entry.get("result") == "pass"
                        for entry in evidence
                    ):
                        self.report.error(
                            "OUTCOME_EVIDENCE_MISSING",
                            strategy.rel,
                            f"{embedded_id} is achieved without passing outcome evidence",
                        )
                if item.get("state") in {"proposed", "active"} and PLACEHOLDER_RE.match(
                    str(item.get("note", "")).strip()
                ):
                    self.report.warning(
                        "PLACEHOLDER_VALUE",
                        strategy.rel,
                        f"{embedded_id} still contains placeholder text",
                    )

    def check_requirement_states(self) -> None:
        for requirement in self.records_by_kind.get("requirement", []):
            if requirement.state not in {"approved", "retired"}:
                continue
            self.verify_approvals(requirement)
            if requirement.state == "retired":
                continue
            if not self.requirement_objectives_active(requirement):
                self.report.error(
                    "REQUIREMENT_OBJECTIVE_NOT_ACTIVE",
                    requirement.rel,
                    "an approved requirement must link to an approved active objective",
                )

    def objective_is_active(self, ref: object, locator: str) -> bool:
        resolved = self.resolve(ref)
        if resolved is None:
            self.report.error(
                "OBJECTIVE_UNRESOLVED", locator, f"objective {ref!r} cannot be resolved"
            )
            return False
        if resolved[0] == "adopted":
            self.report.manual(
                "ADOPTED_OBJECTIVE_UNVERIFIED",
                locator,
                f"objective {ref!r} is external; confirm its approval and active state",
            )
            return False
        if resolved[0] != "embedded" or self.ref_kind(resolved) not in {"objective", "outcome"}:
            self.report.error(
                "OBJECTIVE_TYPE", locator, f"reference {ref!r} is not an objective or outcome"
            )
            return False
        owner: Record = resolved[1]["owner"]
        item = (owner.execution.get("items") or {}).get(ref)
        if owner.state != "approved":
            return False
        if not self.verify_approvals(owner):
            return False
        return isinstance(item, dict) and item.get("state") in {"active", "achieved"}

    def requirement_objectives_active(self, requirement: Record) -> bool:
        for ref in requirement.scope.get("objectives") or []:
            resolved = self.resolve(ref)
            if resolved is None:
                return False
            if resolved[0] != "embedded":
                self.report.manual(
                    "ADOPTED_OBJECTIVE_UNVERIFIED",
                    requirement.rel,
                    f"objective {ref} is external; its strategic state requires review",
                )
                continue
            owner: Record = resolved[1]["owner"]
            item = (owner.execution.get("items") or {}).get(ref)
            if owner.state != "approved" or not isinstance(item, dict):
                return False
            if not self.verify_approvals(owner):
                return False
            if item.get("state") not in {"active", "achieved"}:
                return False
        return True

    def check_milestone_states(self) -> None:
        for milestone in self.records_by_kind.get("milestone", []):
            if milestone.state in {"approved", "active", "achieved"}:
                self.verify_approvals(milestone)
            if milestone.state in {"active", "achieved"}:
                for ref in milestone.scope.get("objectives") or []:
                    resolved = self.resolve(ref)
                    if resolved and resolved[0] == "adopted":
                        self.report.manual(
                            "MILESTONE_OBJECTIVE_EXTERNAL",
                            milestone.rel,
                            f"{ref} is an adopted objective; confirm its approval and active state",
                        )
                        continue
                    if not self.objective_is_active(ref, milestone.rel):
                        self.report.error(
                            "MILESTONE_OBJECTIVE_NOT_ACTIVE",
                            milestone.rel,
                            f"{milestone.state} milestone requires an active approved objective; "
                            f"{ref} is not active",
                        )
                for ref in milestone.scope.get("requirements") or []:
                    resolved = self.resolve(ref)
                    if resolved and resolved[0] == "record":
                        if resolved[1].kind == "requirement" and resolved[1].state != "approved":
                            self.report.error(
                                "MILESTONE_REQUIREMENT_NOT_APPROVED",
                                milestone.rel,
                                f"{milestone.state} milestone cites requirement {ref} in state "
                                f"{resolved[1].state!r}",
                            )
                for dependency in milestone.scope.get("depends_on") or []:
                    satisfied, reason = self.dependency_satisfied(dependency)
                    if not satisfied:
                        level = self.report.error if milestone.state == "active" else self.report.warning
                        level(
                            "MILESTONE_DEPENDENCY_UNSATISFIED",
                            milestone.rel,
                            f"dependency {dependency} is not satisfied: {reason}",
                        )
            if milestone.state == "achieved":
                self.require_evidence(
                    milestone,
                    self.criteria_ids(milestone),
                    rule="MILESTONE_EVIDENCE",
                )

    def verify_approvals(self, record: Record) -> bool:
        """Verify content-bound approval references. Returns True when authorized."""
        if record.id in self.approval_cache:
            return self.approval_cache[record.id]
        result = self._verify_approvals(record)
        self.approval_cache[record.id] = result
        return result

    def _verify_approvals(self, record: Record) -> bool:
        approvals = self.approval_entries(record)
        if not isinstance(approvals, list) or not approvals:
            if record.state in {
                "approved",
                "active",
                "achieved",
                "ready",
                "in_progress",
                "review",
                "done",
            }:
                self.report.error(
                    "APPROVAL_MISSING",
                    record.rel,
                    f"state {record.state!r} requires a valid approval reference",
                )
            return False
        current = scope_digest(record.scope)
        authorized = False
        for approval in approvals:
            if not isinstance(approval, dict):
                continue
            decision_ref = approval.get("decision")
            resolved = self.resolve(decision_ref)
            if resolved is None or resolved[0] != "record" or self.ref_kind(resolved) != "decision":
                self.report.error(
                    "APPROVAL_DECISION_UNKNOWN",
                    record.rel,
                    f"approval references {decision_ref!r}, which is not a decision record",
                )
                continue
            decision: Record = resolved[1]
            if decision.state != "accepted":
                self.report.error(
                    "APPROVAL_DECISION_NOT_ACCEPTED",
                    record.rel,
                    f"approval decision {decision.id} is {decision.state!r}, not 'accepted'",
                )
                continue
            if not self.validate_decision_provenance(decision, "APPROVAL"):
                continue
            targets = decision.scope.get("targets") or []
            matching = [
                target
                for target in targets
                if isinstance(target, dict) and target.get("record") == record.id
            ]
            if not matching:
                delegation = decision.scope.get("delegation")
                delegated = False
                if isinstance(delegation, dict) and record.kind == "task":
                    covers = set(delegation.get("covers") or [])
                    task_context = {
                        record.id,
                        record.scope.get("milestone"),
                        record.scope.get("objective"),
                        *(record.scope.get("requirements") or []),
                    }
                    delegated = bool(task_context & covers)
                if delegated:
                    self.report.manual(
                        "APPROVAL_DELEGATED",
                        record.rel,
                        f"{record.id} relies on bounded delegation in {decision.id}; review the "
                        "conformance rationale and stop conditions manually",
                    )
                    authorized = True
                else:
                    self.report.error(
                        "APPROVAL_TARGET_MISSING",
                        record.rel,
                        f"decision {decision.id} has no target binding for {record.id}",
                    )
                continue
            if all(target.get("scope_sha256") != current for target in matching):
                self.report.error(
                    "APPROVAL_STALE",
                    record.rel,
                    f"decision {decision.id} approved a different scope digest for {record.id}; "
                    "re-approve the exact current scope",
                )
                continue
            authorized = True
        return authorized

    def require_evidence(self, record: Record, criteria: set[str], *, rule: str) -> None:
        evidence = [
            entry
            for entry in record.execution.get("evidence") or []
            if isinstance(entry, dict)
        ]
        for criterion in sorted(criteria):
            matching = [
                entry
                for entry in evidence
                if criterion in (entry.get("criteria") or [])
            ]
            if not matching:
                self.report.error(
                    f"{rule}_MISSING",
                    record.rel,
                    f"no evidence covers criterion {criterion}",
                )
                continue
            if any(entry.get("result") == "fail" for entry in matching):
                self.report.error(
                    f"{rule}_FAILED",
                    record.rel,
                    f"failing evidence exists for criterion {criterion}; the state is not "
                    "achievable without re-evaluation",
                )
            elif not any(entry.get("result") == "pass" for entry in matching):
                self.report.error(
                    f"{rule}_INCONCLUSIVE",
                    record.rel,
                    f"evidence for criterion {criterion} is inconclusive; a done/achieved "
                    "state requires reviewed passing evidence or re-evaluation",
                )

    def dependency_satisfied(self, dependency: object) -> tuple[bool, str]:
        if isinstance(dependency, str):
            resolved = self.resolve(dependency)
            if resolved is None:
                return False, "unresolved reference"
            if resolved[0] == "adopted":
                return False, "adopted dependency cannot be verified structurally"
            record: Record = resolved[1]
            if record.kind == "task":
                return record.state == "done", f"task state is {record.state!r}"
            if record.kind == "milestone":
                return record.state == "achieved", f"milestone state is {record.state!r}"
            return False, f"dependency kind {record.kind!r} is not a task or milestone"
        if isinstance(dependency, dict):
            evidence_ref = str(dependency.get("evidence_ref", ""))
            criterion = str(dependency.get("criterion", ""))
            if evidence_ref in self.evidence_index:
                _record, evidence = self.evidence_index[evidence_ref]
                if criterion not in (evidence.get("criteria") or []):
                    return False, "gate evidence does not cite the required criterion"
                if evidence.get("result") == "pass":
                    return True, "gate evidence passed"
                return False, f"gate evidence result is {evidence.get('result')!r}"
            return False, "gate evidence is not a structured passing record"
        return False, "invalid dependency"

    def check_task_states(self) -> None:
        for task in self.records_by_kind.get("task", []):
            state = task.state
            if state not in {
                "ready",
                "in_progress",
                "review",
                "done",
                "blocked",
            }:
                continue
            authorized = self.verify_approvals(task)
            if state not in {"ready", "in_progress", "review", "done"}:
                continue
            if not authorized:
                self.report.error(
                    "TASK_NOT_AUTHORIZED",
                    task.rel,
                    "task has no valid content-bound authorization for its exact scope",
                )
            objective_ref = task.scope.get("objective")
            objective_resolved = self.resolve(objective_ref)
            if objective_resolved and objective_resolved[0] == "adopted":
                self.report.manual(
                    "TASK_OBJECTIVE_EXTERNAL",
                    task.rel,
                    f"objective {objective_ref!r} is adopted; confirm its approval and active state",
                )
            elif not self.objective_is_active(objective_ref, task.rel):
                self.report.error(
                    "TASK_OBJECTIVE_NOT_ACTIVE",
                    task.rel,
                    f"task state {state!r} requires an active approved objective; "
                    f"{objective_ref!r} is not active",
                )
            milestone_resolved = self.resolve(task.scope.get("milestone"))
            if milestone_resolved is not None and milestone_resolved[0] == "adopted":
                self.report.manual(
                    "TASK_MILESTONE_EXTERNAL",
                    task.rel,
                    "parent milestone is adopted; confirm its active state and approval",
                )
            elif milestone_resolved is None or milestone_resolved[0] != "record":
                self.report.error(
                    "TASK_MILESTONE_UNRESOLVED",
                    task.rel,
                    "task milestone does not resolve to a native milestone",
                )
            else:
                milestone: Record = milestone_resolved[1]
                if state == "ready" and milestone.state != "active":
                    self.report.error(
                        "TASK_MILESTONE_NOT_ACTIVE",
                        task.rel,
                        f"ready task requires an active milestone; {milestone.id} is "
                        f"{milestone.state!r}",
                    )
                if milestone.state not in {"active", "achieved"}:
                    self.report.error(
                        "TASK_MILESTONE_NOT_STARTED",
                        task.rel,
                        f"task state {state!r} requires an active or achieved milestone; "
                        f"{milestone.id} is {milestone.state!r}",
                    )
                if not self.verify_approvals(milestone):
                    self.report.error(
                        "TASK_MILESTONE_NOT_AUTHORIZED",
                        task.rel,
                        f"parent milestone {milestone.id} has no valid content-bound approval",
                    )
            for ref in task.scope.get("requirements") or []:
                resolved = self.resolve(ref)
                if resolved and resolved[0] == "record":
                    requirement: Record = resolved[1]
                    if requirement.kind == "requirement" and requirement.state != "approved":
                        self.report.error(
                            "TASK_REQUIREMENT_NOT_APPROVED",
                            task.rel,
                            f"task cites requirement {ref} in state {requirement.state!r}",
                        )
                    elif requirement.kind == "requirement" and not self.verify_approvals(
                        requirement
                    ):
                        self.report.error(
                            "TASK_REQUIREMENT_NOT_AUTHORIZED",
                            task.rel,
                            f"requirement {ref} has no valid content-bound approval",
                        )
                elif resolved and resolved[0] == "adopted":
                    self.report.manual(
                        "TASK_REQUIREMENT_EXTERNAL",
                        task.rel,
                        f"task cites adopted requirement {ref}; confirm its approval separately",
                    )
            for dependency in task.scope.get("depends_on") or []:
                if isinstance(dependency, str):
                    resolved = self.resolve(dependency)
                    if resolved and resolved[0] == "adopted":
                        self.report.manual(
                            "DEPENDENCY_EXTERNAL_UNVERIFIED",
                            task.rel,
                            f"dependency {dependency!r} is adopted; confirm satisfaction and "
                            "source freshness",
                        )
                        continue
                satisfied, reason = self.dependency_satisfied(dependency)
                if not satisfied:
                    self.report.error(
                        "TASK_DEPENDENCY_UNSATISFIED",
                        task.rel,
                        f"dependency {dependency} is not satisfied: {reason}",
                    )
            for authorization in task.execution.get("authorization") or []:
                resolved = self.resolve(authorization)
                if resolved is None or resolved[0] != "record" or self.ref_kind(resolved) != "decision":
                    self.report.error(
                        "AUTHORIZATION_UNKNOWN",
                        task.rel,
                        f"authorization entry {authorization!r} is not a decision record",
                    )
                elif resolved[1].state != "accepted":
                    self.report.error(
                        "AUTHORIZATION_NOT_ACCEPTED",
                        task.rel,
                        f"authorization decision {authorization!r} is {resolved[1].state!r}",
                    )
            if task.execution.get("blockers"):
                self.report.error(
                    "TASK_READY_WITH_BLOCKER",
                    task.rel,
                    f"task state {state!r} still has blockers",
                )
            if state == "done":
                self.require_evidence(
                    task, self.criteria_ids(task), rule="TASK_DONE_EVIDENCE"
                )
            elif state == "review":
                evidence = [
                    entry
                    for entry in task.execution.get("evidence") or []
                    if isinstance(entry, dict)
                ]
                if not evidence:
                    self.report.error(
                        "TASK_REVIEW_WITHOUT_EVIDENCE",
                        task.rel,
                        "review state means outputs/evidence are available; none are recorded",
                    )
            self.check_task_placeholders(task, state)

    def check_task_placeholders(self, task: Record, state: str) -> None:
        mandatory = (
            "title",
            "objective",
            "rationale",
            "milestone",
            "requirements",
            "include",
            "exclude",
            "deliverables",
            "acceptance",
            "verification",
            "priority",
            "size",
        )
        for key in mandatory:
            value = task.scope.get(key)
            if isinstance(value, str) and PLACEHOLDER_RE.match(value.strip()):
                if state in {"ready", "in_progress", "review", "done"}:
                    self.report.error(
                        "READY_TASK_PLACEHOLDER",
                        task.rel,
                        f"mandatory field {key!r} still contains placeholder text",
                    )
                else:
                    self.report.warning(
                        "PLACEHOLDER_VALUE",
                        task.rel,
                        f"mandatory field {key!r} still contains placeholder text",
                    )

    # -------------------------------------------------------------- evidence
    def index_evidence(self) -> None:
        for record in self.records.values():
            self.index_record_evidence(record)
            if record.kind == "strategy":
                items = record.execution.get("items")
                if isinstance(items, dict):
                    for item in items.values():
                        if isinstance(item, dict):
                            for evidence in item.get("evidence") or []:
                                if isinstance(evidence, dict):
                                    self.add_evidence(record, evidence, external=True)

    def index_record_evidence(self, record: Record) -> None:
        for evidence in record.execution.get("evidence") or []:
            if isinstance(evidence, dict):
                self.add_evidence(record, evidence, external=False)

    def add_evidence(self, record: Record, evidence: dict, *, external: bool) -> None:
        evidence_id = evidence.get("id")
        if not isinstance(evidence_id, str):
            return
        if evidence_id in self.evidence_index:
            self.report.error(
                "DUPLICATE_EVIDENCE_ID",
                record.rel,
                f"evidence ID {evidence_id} is not unique",
            )
        self.evidence_index[evidence_id] = (record, evidence)
        self.check_reviewer(evidence.get("reviewer"), record.rel)
        criteria = evidence.get("criteria") or []
        known = self.criteria_ids(record)
        if external:
            known = set()
        for criterion in criteria:
            if known and criterion not in known:
                self.report.error(
                    "EVIDENCE_UNKNOWN_CRITERION",
                    record.rel,
                    f"evidence {evidence_id} cites unknown criterion {criterion}",
                )
        observer = evidence.get("observed_at")
        if not self.valid_date(observer):
            self.report.error(
                "EVIDENCE_DATE_INVALID",
                record.rel,
                f"evidence {evidence_id} observed_at must be a real YYYY-MM-DD calendar date",
            )
        subject = evidence.get("subject_revision")
        if (
            self.source_revision
            and isinstance(subject, str)
            and subject not in {self.source_revision, "working-tree"}
        ):
            self.report.warning(
                "EVIDENCE_REVISION_STALE",
                record.rel,
                f"evidence {evidence_id} subject revision {subject!r} differs from the "
                f"requested source revision {self.source_revision!r}",
            )

    def check_evidence_claims(self) -> None:
        for milestone in self.records_by_kind.get("milestone", []):
            if milestone.state == "achieved":
                continue
            for evidence in milestone.execution.get("evidence") or []:
                if not isinstance(evidence, dict):
                    continue
                if evidence.get("result") == "pass":
                    covered = set(evidence.get("criteria") or [])
                    if covered and covered >= self.criteria_ids(milestone):
                        self.report.manual(
                            "MILESTONE_ACHIEVEMENT_REVIEW",
                            milestone.rel,
                            "passing evidence covers all exit criteria, but milestone "
                            "achievement still requires the Product Owner's decision",
                        )

    def canonical_id(self, ref: object) -> object:
        resolved = self.resolve(ref)
        if resolved is None:
            return ref
        if resolved[0] == "record":
            return resolved[1].id
        return ref

    def check_reverse_coverage(self) -> None:
        requirements_referenced = set()
        for milestone in self.records_by_kind.get("milestone", []):
            milestone_requirements = {
                self.canonical_id(ref) for ref in milestone.scope.get("requirements") or []
            }
            requirements_referenced.update(milestone_requirements)
            for task_id in self.tasks_for_milestone(milestone.id):
                task = self.records[task_id]
                outside = {
                    self.canonical_id(ref) for ref in task.scope.get("requirements") or []
                } - milestone_requirements
                for ref in sorted(outside):
                    self.report.warning(
                        "TASK_REQUIREMENT_OUTSIDE_MILESTONE",
                        task.rel,
                        f"task cites {ref}, which is not listed by parent milestone "
                        f"{milestone.id}",
                    )
        for requirement in self.records_by_kind.get("requirement", []):
            if requirement.state == "approved" and requirement.id not in requirements_referenced:
                self.report.warning(
                    "REQUIREMENT_NOT_DECOMPOSED",
                    requirement.rel,
                    "approved requirement is not referenced by any milestone; confirm whether "
                    "it is intentionally unplanned",
                )

        covered_objectives = set()
        for requirement in self.records_by_kind.get("requirement", []):
            if requirement.state == "approved":
                covered_objectives.update(
                    self.canonical_id(ref)
                    for ref in requirement.scope.get("objectives") or []
                )
        for embedded_id, embedded in self.embedded.items():
            if embedded["kind"] == "objective" and embedded_id not in covered_objectives:
                self.report.warning(
                    "OBJECTIVE_UNCOVERED",
                    embedded["owner"].rel,
                    f"objective {embedded_id} has no approved requirement",
                )

    def tasks_for_milestone(self, milestone_id: str) -> list[str]:
        return [
            task.id
            for task in self.records_by_kind.get("task", [])
            if self.canonical_id(task.scope.get("milestone")) == milestone_id
        ]

    # --------------------------------------------------------------- cycles
    def check_cycles(self) -> None:
        graph: dict[str, list[str]] = {}
        for record in list(self.records_by_kind.get("task", [])) + list(
            self.records_by_kind.get("milestone", [])
        ):
            edges: list[str] = []
            for dependency in record.scope.get("depends_on") or []:
                if isinstance(dependency, str):
                    resolved = self.resolve(dependency)
                    if resolved and resolved[0] == "record" and self.ref_kind(resolved) in {
                        "task",
                        "milestone",
                    }:
                        edges.append(resolved[1].id)
            graph[record.id] = edges

        visiting: set[str] = set()
        visited: set[str] = set()
        reported: set[tuple[str, ...]] = set()

        def visit(node: str, stack: list[str]) -> None:
            if node in visiting:
                index = stack.index(node) if node in stack else 0
                cycle = tuple(sorted(stack[index:] + [node]))
                if cycle not in reported:
                    reported.add(cycle)
                    self.report.error(
                        "DEPENDENCY_CYCLE",
                        self.records[node].rel if node in self.records else node,
                        "dependency cycle: " + " -> ".join(stack[index:] + [node]),
                    )
                return
            if node in visited or node not in graph:
                return
            visiting.add(node)
            stack.append(node)
            for neighbour in graph[node]:
                visit(neighbour, stack)
            stack.pop()
            visiting.remove(node)
            visited.add(node)

        for node in sorted(graph):
            visit(node, [])

    # ------------------------------------------------------------- coverage
    GLOBAL_READINESS_ERRORS = {
        "DUPLICATE_ID",
        "DUPLICATE_ALIAS",
        "DUPLICATE_AUTHORITY",
        "DUPLICATE_ADOPTED_ID",
        "OVERLAPPING_AUTHORITY_ROOTS",
        "UNSAFE_AUTHORITY",
        "UNSAFE_AUTHORITY_ROOT",
        "UNSAFE_AUTHORITY_REF",
        "UNSAFE_CONTENT_ROOT",
        "UNKNOWN_AUTHORITY_OWNER",
        "MULTIPLE_ACTIVE_MILESTONES",
        "CURRENT_MILESTONE_UNKNOWN",
        "CURRENT_MILESTONE_NOT_ACTIVE",
        "CURRENT_MILESTONE_MISMATCH",
        "DEPENDENCY_CYCLE",
        "TASK_ORDER_UNKNOWN",
        "UNSUPPORTED_SCHEMA",
    }
    GLOBAL_READINESS_WARNINGS = {"CURRENT_MILESTONE_UNSET", "PLACEHOLDER_CONFIG"}
    RELATED_READINESS_WARNINGS = {
        "TASK_REQUIREMENT_OUTSIDE_MILESTONE",
        "REQUIREMENT_NOT_DECOMPOSED",
        "OBJECTIVE_UNCOVERED",
        "UNKNOWN_REVIEWER",
        "PLACEHOLDER_VALUE",
        "CONTEXT_REVISION_STALE",
    }
    READINESS_REVIEW_RULES = {
        "EXTERNAL_AUTHORITY_UNPARSED",
        "EXTERNAL_AUTHORITY_UNVERIFIED",
        "EXTERNAL_REFERENCE_UNVERIFIED",
        "EXTERNAL_CONTEXT",
        "ADOPTED_OBJECTIVE_UNVERIFIED",
        "MILESTONE_OBJECTIVE_EXTERNAL",
        "PACKAGE_PARENT_UNVERIFIED",
        "APPROVAL_DELEGATED",
        "TASK_REQUIREMENT_EXTERNAL",
        "TASK_MILESTONE_EXTERNAL",
        "TASK_OBJECTIVE_EXTERNAL",
        "DEPENDENCY_EXTERNAL_UNVERIFIED",
    }

    def task_context_locators(self, task: Record) -> set[str]:
        """Native records whose findings affect this task's readiness."""
        locators: set[str] = set()
        seen: set[str] = set()

        def add_embedded(owner: Record) -> None:
            add_record(owner)

        def add_record(record: Record | None) -> None:
            if record is None or record.id in seen:
                return
            seen.add(record.id)
            locators.add(record.rel)
            if record.kind in {"task", "milestone"}:
                for ref in record.scope.get("requirements") or []:
                    resolved = self.resolve(ref)
                    if resolved and resolved[0] == "record":
                        add_record(resolved[1])
                for ref in (
                    [record.scope.get("milestone")]
                    if record.kind == "task"
                    else []
                ):
                    resolved = self.resolve(ref)
                    if resolved and resolved[0] == "record":
                        add_record(resolved[1])
                if record.kind == "task":
                    resolved = self.resolve(record.scope.get("objective"))
                    if resolved and resolved[0] == "embedded":
                        add_embedded(resolved[1]["owner"])
                for ref in record.scope.get("objectives") or []:
                    resolved = self.resolve(ref)
                    if resolved and resolved[0] == "embedded":
                        add_embedded(resolved[1]["owner"])
                for dependency in record.scope.get("depends_on") or []:
                    if isinstance(dependency, str):
                        resolved = self.resolve(dependency)
                        if resolved and resolved[0] == "record":
                            add_record(resolved[1])
            elif record.kind == "requirement":
                for ref in record.scope.get("objectives") or []:
                    resolved = self.resolve(ref)
                    if resolved and resolved[0] == "embedded":
                        add_embedded(resolved[1]["owner"])
            for approval in self.approval_entries(record):
                if not isinstance(approval, dict):
                    continue
                resolved = self.resolve(approval.get("decision"))
                if resolved and resolved[0] == "record":
                    add_record(resolved[1])

        add_record(task)
        return locators

    def readiness_findings(self, locators: set[str]) -> list[Finding]:
        result = []
        for finding in self.report.findings:
            if any(
                finding.locator == locator or finding.locator.startswith(locator + "#")
                for locator in locators
            ):
                result.append(finding)
            elif finding.locator == self.locator(self.config_path):
                result.append(finding)
        return result

    def build_coverage(self) -> None:
        readiness = {}
        criteria_total = 0
        criteria_passed = 0
        for task in self.records_by_kind.get("task", []):
            task_criteria = self.criteria_ids(task)
            evidence = [
                entry
                for entry in task.execution.get("evidence") or []
                if isinstance(entry, dict)
            ]
            passed = {
                criterion
                for criterion in task_criteria
                if any(
                    criterion in (entry.get("criteria") or [])
                    and entry.get("result") == "pass"
                    for entry in evidence
                )
            }
            criteria_total += len(task_criteria)
            criteria_passed += len(passed)
            blockers: set[str] = set()
            review: set[str] = set()
            if task.state != "ready":
                blockers.add(f"state is {task.state!r}")
            if task.execution.get("blockers"):
                blockers.add("blockers present")

            config_locator = self.locator(self.config_path)
            for finding in self.report.findings:
                if finding.locator == config_locator:
                    if finding.rule in self.GLOBAL_READINESS_ERRORS and finding.severity == "error":
                        blockers.add(f"global: {finding.rule}")
                    elif (
                        finding.rule in self.GLOBAL_READINESS_WARNINGS
                        and finding.severity == "warning"
                    ):
                        blockers.add(f"global: {finding.rule}")
                    continue
                if (
                    finding.severity == "error"
                    and finding.rule in self.GLOBAL_READINESS_ERRORS
                ):
                    blockers.add(f"global: {finding.rule}")

            context = self.task_context_locators(task)
            for finding in self.readiness_findings(context):
                if finding.locator == config_locator:
                    continue
                if finding.severity == "error":
                    blockers.add(finding.rule)
                elif (
                    finding.severity == "warning"
                    and finding.rule in self.RELATED_READINESS_WARNINGS
                ):
                    blockers.add(finding.rule)
                elif (
                    finding.severity == "manual_review"
                    and finding.rule in self.READINESS_REVIEW_RULES
                ):
                    review.add(finding.rule)

            readiness[task.id] = {
                "state": task.state,
                "ready": task.state == "ready" and not blockers and not review,
                "review_required": task.state == "ready" and not blockers and bool(review),
                "blockers": sorted(blockers),
                "manual_review": sorted(review),
                "reasons": sorted(blockers | review),
            }
        coverage = {
            "records_by_kind": {
                kind: len(records) for kind, records in self.records_by_kind.items()
            },
            "adopted_records": len(self.adopted),
            "aliases": len(self.aliases),
            "unparsed_markdown": len(self.unparsed_markdown),
            "evidence_entries": len(self.evidence_index),
            "task_criteria": criteria_total,
            "task_criteria_with_passing_evidence": criteria_passed,
            "ready_tasks": sorted(
                task_id for task_id, value in readiness.items() if value["ready"]
            ),
            "review_required_tasks": sorted(
                task_id
                for task_id, value in readiness.items()
                if value.get("review_required")
            ),
            "task_readiness": readiness,
        }
        self.report.coverage = coverage

    def global_manual_review(self) -> None:
        self.report.manual(
            "SEMANTIC_REVIEW_REQUIRED",
            self.locator(self.config_path),
            "structural checks cannot prove semantic contradictions, strategic relevance, "
            "source freshness or human identity; perform AUDIT review",
        )
        if any(
            finding.rule == "EVIDENCE_REVISION_STALE"
            for finding in self.report.findings
        ):
            self.report.manual(
                "EVIDENCE_EFFECTIVENESS",
                self.locator(self.config_path),
                "evidence structure does not prove that a method was appropriate or actually run",
            )

    # ----------------------------------------------------------------- run
    def run(self) -> Report:
        if not self.load_schemas():
            return self.report
        if not self.load_config():
            return self.report
        self.check_config_semantics()
        self.discover()
        self.index_embedded()
        self.index_aliases()
        self.index_evidence()
        self.check_references()
        self.check_states()
        self.check_evidence_claims()
        self.check_reverse_coverage()
        self.check_cycles()
        self.build_coverage()
        self.global_manual_review()
        self.report.findings = list(
            {
                (
                    finding.rule,
                    finding.severity,
                    finding.locator,
                    finding.message,
                ): finding
                for finding in self.report.findings
            }.values()
        )
        counts = self.report.counts()
        if counts["error"]:
            self.report.exit_code = max(self.report.exit_code, 1)
        return self.report


def payload(report: Report) -> dict:
    counts = report.counts()
    return {
        "report_version": REPORT_VERSION,
        "checker": {"name": "check_planning.py", "version": CHECKER_VERSION, "schema_version": 1},
        "project": report.project,
        "result": {
            "ok": counts["error"] == 0 and report.exit_code == 0,
            "exit_code": report.exit_code,
            "errors": counts["error"],
            "warnings": counts["warning"],
            "manual_review_required": counts["manual_review"],
        },
        "coverage": report.coverage,
        "findings": [finding.as_dict() for finding in report.findings],
    }


def text_output(report: Report) -> str:
    lines = ["Planner structural check", "========================"]
    project = report.project
    if project:
        lines.append(
            f"Project: {project.get('name')} ({project.get('project_id')}, "
            f"{project.get('category')})"
        )
        lines.append(f"Root: {project.get('root')}")
    coverage = report.coverage
    if coverage:
        records = coverage.get("records_by_kind", {})
        lines.append(
            "Records: "
            + ", ".join(f"{kind}={count}" for kind, count in records.items() if count)
        )
        lines.append(
            "Coverage: adopted={adopted}, aliases={aliases}, unparsed={unparsed}, "
            "task criteria passed {passed}/{total}, ready tasks {ready}, "
            "review-required tasks {review}".format(
                adopted=coverage.get("adopted_records", 0),
                aliases=coverage.get("aliases", 0),
                unparsed=coverage.get("unparsed_markdown", 0),
                passed=coverage.get("task_criteria_with_passing_evidence", 0),
                total=coverage.get("task_criteria", 0),
                ready=", ".join(coverage.get("ready_tasks", [])) or "none",
                review=", ".join(coverage.get("review_required_tasks", [])) or "none",
            )
        )
    order = {"error": 0, "warning": 1, "manual_review": 2}
    for finding in sorted(
        report.findings, key=lambda item: (order.get(item.severity, 9), item.rule, item.locator)
    ):
        lines.append("")
        lines.append(f"[{finding.severity.upper()}] {finding.rule} at {finding.locator}")
        lines.append(f"  {finding.message}")
    counts = report.counts()
    lines.append("")
    lines.append(
        f"Result: {counts['error']} error(s), {counts['warning']} warning(s), "
        f"{counts['manual_review']} manual review item(s); exit {report.exit_code}"
    )
    if counts["error"] == 0 and report.exit_code == 0:
        lines.append(
            "Deterministic checks completed without errors. This is not a strategic PASS."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only structural checker for planner native records."
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Project root containing planning/planner.yaml (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Report format (default: text)",
    )
    parser.add_argument(
        "--source-revision",
        default=None,
        help="Optional current source revision used to flag stale evidence subject revisions",
    )
    args = parser.parse_args(argv)

    project = Path(args.project)
    if not project.is_dir():
        sys.stderr.write(f"error: project path does not exist: {project}\n")
        return 2

    checker = PlannerCheck(project, args.source_revision)
    report = checker.run()
    if args.format == "json":
        sys.stdout.write(json.dumps(payload(report), indent=2, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(text_output(report) + "\n")
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
