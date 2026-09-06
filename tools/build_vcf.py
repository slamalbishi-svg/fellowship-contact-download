#!/usr/bin/env python3
"""Generate fellowship-contacts.vcf (vCard 3.0) from fellowship-contacts.csv.

Usage:
    python3 build_vcf.py [path/to/source.csv] [path/to/output.vcf]

Defaults to ../files/fellowship-contacts.csv and ../files/fellowship-contacts.vcf
relative to this script, i.e. run from inside tools/ with no arguments to
regenerate the file already shipped in the project.

Rules (must not be changed without re-approval of the data):
  - One CSV row -> exactly one VCARD. No rows are merged, dropped, or invented.
  - Name fields (Name, Given Name, Additional Name, Family Name) are copied
    verbatim into FN / N.
  - Phone numbers are normalized ONLY to fix an Excel export artifact where
    "966XXXXXXXXX" was stored as "966XXXXXXXXX.0": the trailing ".0" is
    stripped and a leading "+" is added. No digit is added, removed, or
    changed otherwise. A contact with no phone number gets no TEL line.
  - The full Notes field (organization, activity, job title, address, etc.,
    however it happens to be formatted in the source) is preserved verbatim,
    in full, inside NOTE. It is never parsed into ORG/TITLE/ADR/EMAIL/URL,
    because the source does not provide those as separate columns and the
    free-text formatting is inconsistent between rows -- guessing a
    structured split would risk misattributing information that was never
    approved in that structured form.
"""
import csv
import re
import sys
from pathlib import Path


def esc(s):
    if s is None:
        return ""
    s = s.replace("\\", "\\\\")
    s = s.replace(";", "\\;")
    s = s.replace(",", "\\,")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\n", "\\n")
    return s


def fold(line):
    """vCard 3.0 line folding at 75 octets, UTF-8-safe, CRLF continuation."""
    data = line.encode("utf-8")
    if len(data) <= 75:
        return line + "\r\n"
    result = b""
    first = True
    i = 0
    while i < len(data):
        limit = 75 if first else 74  # 74 + 1 leading space = 75
        piece = data[i:i + limit]
        while True:
            try:
                piece.decode("utf-8")
                break
            except UnicodeDecodeError:
                piece = piece[:-1]
        result += piece if first else b"\r\n " + piece
        first = False
        i += len(piece)
    return result.decode("utf-8") + "\r\n"


def normalize_phone(raw):
    if not raw or not raw.strip():
        return None
    v = raw.strip()
    v = re.sub(r"\.0$", "", v)
    if not v.startswith("+"):
        v = "+" + v
    return v


def build(src_path, out_path):
    with open(src_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    no_phone = 0
    with open(out_path, "w", encoding="utf-8", newline="") as out:
        for row in rows:
            name = (row.get("Name") or "").strip()
            given = (row.get("Given Name") or "").strip()
            additional = (row.get("Additional Name") or "").strip()
            family = (row.get("Family Name") or "").strip()
            phone = normalize_phone(row.get("Phone 1 - Value") or "")
            notes = row.get("Notes") or ""

            out.write(fold("BEGIN:VCARD"))
            out.write(fold("VERSION:3.0"))
            out.write(fold(f"N:{esc(family)};{esc(given)};{esc(additional)};;"))
            out.write(fold(f"FN:{esc(name)}"))
            if phone:
                out.write(fold(f"TEL;TYPE=CELL:{phone}"))
            else:
                no_phone += 1
            if notes.strip():
                out.write(fold(f"NOTE:{esc(notes)}"))
            out.write(fold("END:VCARD"))

    return len(rows), no_phone


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else here / ".." / "files" / "fellowship-contacts.csv"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else here / ".." / "files" / "fellowship-contacts.vcf"

    total, missing_phone = build(src, out)
    print(f"Source CSV : {src}")
    print(f"Output VCF : {out}")
    print(f"Contacts written : {total}")
    print(f"Contacts without phone : {missing_phone}")
