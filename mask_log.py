#!/usr/bin/env python3
"""
Build the publishable, de-identified copy of ASSIGNMENT_LOG.md.

Replacing group numbers with codes is not enough: once the final assignment is
known, any per-group detail can be traced back through the assigned task.
The published copy therefore contains no group identifiers at all, and no
per-group preferences or outcomes; it keeps only aggregates.

Markup in ASSIGNMENT_LOG.md:
    <!-- private -->
    ...full detail, removed from the published copy...
    <!-- /private -->
    <!-- public
    ...de-identified replacement, shown only in the published copy...
    -->

The script refuses to write the output if anything that looks like a group
identifier or a per-group table row is left.

Usage: python3 mask_log.py
"""
import re
import sys

SRC = "ASSIGNMENT_LOG.md"
DST = "ASSIGNMENT_LOG_masked.md"

PRIVATE = re.compile(r"<!-- private -->.*?<!-- /private -->\n?", re.S)
PUBLIC = re.compile(r"<!-- public\n(.*?)\n-->", re.S)
COMMENT = re.compile(r"<!--.*?-->\n?", re.S)

NOTE = ("> **Published copy.** Group numbers and all per-group preferences and "
        "results are removed, so nothing here can be traced back to a group, "
        "even with the final assignment at hand. The full log is kept privately "
        "by the course organiser.")

# Task numbers may appear only in these group-independent statements
ALLOWED_TASK_MENTIONS = ["Task 11's sample list", "Task 20 lists"]

CHECKS = {
    "group number": re.compile(r"\b[Gg]roups?\s*[\(#\[]?\s*\d"),
    "per-group table row": re.compile(r"^\|\s*\[?\d+\]?\s*\|", re.M),
    "task number": re.compile(r"\b[Tt]asks?\s+\(?\d"),
    "task list": re.compile(r"\b\d+\s*/\s*\d+\b"),
    "leftover markup": re.compile(r"<!--|-->"),
}


def build(text):
    text = PRIVATE.sub("", text)
    text = PUBLIC.sub(lambda m: m.group(1), text)
    text = COMMENT.sub("", text)
    lines = text.split("\n")
    lines[1:1] = ["", NOTE]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines))


def problems(text):
    found = []
    for line in text.split("\n"):
        check_line = line
        for ok in ALLOWED_TASK_MENTIONS:
            check_line = check_line.replace(ok, "")
        for name, pattern in CHECKS.items():
            if pattern.search(check_line):
                found.append(f"{name}: {line}")
    return found


def main():
    with open(SRC) as f:
        text = build(f.read())
    found = problems(text)
    if found:
        sys.exit("Not written; possible identifying content:\n  " + "\n  ".join(found))
    with open(DST, "w") as f:
        f.write(text)
    print(f"Written {DST!r}")


if __name__ == "__main__":
    main()
