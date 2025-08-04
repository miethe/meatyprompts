#!/usr/bin/env python3
"""
Bootstrap script for configuring a newly created GitHub repository.

This script is intended to be run from the root of the template after
creating a new repository.  It uses the GitHub API (via the `gh`
command-line or `requests` library) to apply labels, branch protections,
enable CodeQL, Dependabot, and mark the repository as a template.

Currently this script is a placeholder; implement integration with the
GitHub API or CLI as needed for your organisation.
"""
import sys


def main() -> int:
    print(
        "bootstrap.py: This script should configure labels, branch protections, and other settings via the GitHub API."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())