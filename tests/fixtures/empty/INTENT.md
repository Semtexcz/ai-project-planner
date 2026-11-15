# Empty-project acceptance input (scenario A)

Intention supplied to INIT:

> Build a small, maintainable document conversion package. It converts a
> Markdown document to plain text, keeps code fences readable, and reports
> unsupported constructs instead of silently dropping them. The package is a
> library with a command-line entry point; it must not need a server.

Constraints:

- Python 3.11+ is acceptable.
- No network access at conversion time.
- A conversion failure must be explicit.
- No application files exist before INIT.

This fixture contains no planning records. Tests construct the approved
strategy, requirement, milestone and ready task in a disposable repository.
