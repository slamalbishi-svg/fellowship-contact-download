#!/usr/bin/env python3
"""Generate all VCF outputs from fellowship-contacts.csv.

Usage:
    python3 build_vcf.py [path/to/source.csv]

Defaults to ../files/fellowship-contacts.csv relative to this script.
Run from inside tools/ with no arguments to regenerate everything shipped
in the project from the approved source CSV.

Outputs (all derived from the same CSV, in the same row order):
  - files/contacts/contact-001.vcf ... contact-050.vcf
      One contact per file. This is the primary, reliable iPhone/Android
      import path: the website lets a Fellow pick their own name and add
      just that one card, which both platforms handle without ambiguity.
  - files/fellowship-contacts.vcf
      The old combined, all-50-in-one-file VCF. Kept for archival/testing
      only. Real-device testing showed iOS's inline Safari preview only
      recognizes the first card from a multi-VCARD file, so this is no
      longer linked from the page as the recommended import method.
  - files/fellowship-contacts-individual-vcf.zip
      A convenience archive of all 50 individual files, for anyone who
      wants the whole folder at once. Secondary to the per-contact buttons.
  - assets/contacts-data.js
      A small generated JS data file (window.FELLOWSHIP_CONTACTS = [...])
      that the page reads at runtime to render the searchable contact list
      and wire up each "إضافة إلى جهات الاتصال" button. No fetch/backend
      involved -- it's a plain script include, so it works the same over
      file:// or any static host.

Rules (must not be changed without re-approval of the data):
  - One CSV row -> exactly one VCARD (in every output). No rows are merged,
    dropped, renamed, or invented.
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
import json
import re
import sys
import zipfile
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
    """Write one property per line, CRLF-terminated, deliberately UNFOLDED.

    RFC 2425 line folding is optional, not required. It is intentionally
    NOT used here: real-device testing linked the previous combined VCF's
    failure to import all cards to exactly this kind of ambiguity, and
    unfolded lines remove that entire class of risk. Modern iOS/Android
    parsers handle arbitrarily long single lines without issue.
    """
    return line + "\r\n"


def normalize_phone(raw):
    if not raw or not raw.strip():
        return None
    v = raw.strip()
    v = re.sub(r"\.0$", "", v)
    if not v.startswith("+"):
        v = "+" + v
    return v


def load_rows(src_path):
    with open(src_path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def vcard_for_row(row):
    """Return one complete BEGIN:VCARD..END:VCARD block (CRLF-terminated) for a single CSV row."""
    name = (row.get("Name") or "").strip()
    given = (row.get("Given Name") or "").strip()
    additional = (row.get("Additional Name") or "").strip()
    family = (row.get("Family Name") or "").strip()
    phone = normalize_phone(row.get("Phone 1 - Value") or "")
    notes = row.get("Notes") or ""

    out = []
    out.append(fold("BEGIN:VCARD"))
    out.append(fold("VERSION:3.0"))
    out.append(fold(f"N:{esc(family)};{esc(given)};{esc(additional)};;"))
    out.append(fold(f"FN:{esc(name)}"))
    if phone:
        out.append(fold(f"TEL;TYPE=CELL:{phone}"))
    if notes.strip():
        out.append(fold(f"NOTE:{esc(notes)}"))
    out.append(fold("END:VCARD"))
    return "".join(out), bool(phone)


def build_combined(rows, out_path):
    no_phone = 0
    with open(out_path, "w", encoding="utf-8", newline="") as out:
        for row in rows:
            card, has_phone = vcard_for_row(row)
            out.write(card)
            if not has_phone:
                no_phone += 1
    return no_phone


def build_individuals(rows, contacts_dir):
    contacts_dir.mkdir(parents=True, exist_ok=True)
    # Remove any stale files from a previous run so the folder never
    # accumulates leftovers if the CSV ever shrinks.
    for stale in contacts_dir.glob("contact-*.vcf"):
        stale.unlink()

    filenames = []
    for i, row in enumerate(rows, start=1):
        fname = f"contact-{i:03d}.vcf"
        card, _ = vcard_for_row(row)
        with open(contacts_dir / fname, "w", encoding="utf-8", newline="") as f:
            f.write(card)
        filenames.append(fname)
    return filenames


def build_zip(contacts_dir, filenames, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            zf.write(contacts_dir / fname, arcname=fname)


def build_contacts_data_js(rows, filenames, out_path):
    entries = [
        {"name": (row.get("Name") or "").strip(), "file": f"files/contacts/{fname}"}
        for row, fname in zip(rows, filenames)
    ]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("// Generated by tools/build_vcf.py from fellowship-contacts.csv. Do not edit by hand.\n")
        f.write("window.FELLOWSHIP_CONTACTS = ")
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write(";\n")
    return len(entries)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    project = here / ".."
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else project / "files" / "fellowship-contacts.csv"

    rows = load_rows(src)

    combined_out = project / "files" / "fellowship-contacts.vcf"
    no_phone_combined = build_combined(rows, combined_out)

    contacts_dir = project / "files" / "contacts"
    filenames = build_individuals(rows, contacts_dir)

    zip_out = project / "files" / "fellowship-contacts-individual-vcf.zip"
    build_zip(contacts_dir, filenames, zip_out)

    data_js_out = project / "assets" / "contacts-data.js"
    entry_count = build_contacts_data_js(rows, filenames, data_js_out)

    print(f"Source CSV               : {src}")
    print(f"CSV contacts             : {len(rows)}")
    print(f"Individual VCF files     : {len(filenames)} -> {contacts_dir}")
    print(f"Combined VCF (archival)  : {combined_out} (no-phone count: {no_phone_combined})")
    print(f"ZIP archive              : {zip_out}")
    print(f"Contacts data JS entries : {entry_count} -> {data_js_out}")
