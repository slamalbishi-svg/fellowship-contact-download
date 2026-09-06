# Fellowship Contact Download — Admin Notes

Internal build/reference notes. Not part of the public page.

## Source of truth

- **Official source CSV**: `Google_Contacts_زمالة_المشاركة_المجتمعية_2026م_V13.csv`
  (the file the requester referred to as "V13(1)" — verified byte-for-byte
  identical to the file used throughout this build; no separate "(1)" file
  exists or was ever used).
- **SHA-256**: `180a7a17e71c291a85d9ee7525beb5885834246f38df27acf18d82625c29d450`
- **Size**: 28,030 bytes
- **Contacts**: 50 rows (49 with a phone number, 1 without — مشاري فهد الجويره,
  which has no phone in the source and none was invented)
- Shipped in this package unchanged as `files/fellowship-contacts.csv`.
- **There is no separately-approved VCF.** `files/fellowship-contacts.vcf` is
  generated entirely from this CSV by `tools/build_vcf.py`.

## Regenerating the VCF

```bash
cd tools
python3 build_vcf.py
```

Defaults to reading `../files/fellowship-contacts.csv` and writing
`../files/fellowship-contacts.vcf`. Pass explicit paths as two arguments to
use a different source. Rerun this any time `files/fellowship-contacts.csv`
is replaced with a new approved version.

## Data-handling rules baked into the build

1. **One CSV row → one VCARD.** No merging, dropping, renaming, or inventing
   contacts. 50 CSV rows in → 50 VCARDs out, always.
2. **Names** (`Name`, `Given Name`, `Additional Name`, `Family Name`) are
   copied verbatim into `FN` / `N`.
3. **Phone normalization** — the only transformation applied to any field:
   the source stores mobile numbers as `966XXXXXXXXX.0` (an Excel/CSV export
   artifact). The build strips the trailing `.0` and adds a leading `+`.
   No digit is ever added, removed, or changed. A contact with no phone gets
   no `TEL` line — never a placeholder.
4. **Notes / الملاحظات** are preserved verbatim and in full inside `NOTE`,
   including multiline content. They are **not** parsed into `ORG` / `TITLE`
   / `ADR` / `EMAIL` / `URL`, because the source CSV has no such columns and
   the free-text formatting of organization/title/address inside the Notes
   field is inconsistent row-to-row (some rows label it "الجهة:" / "المسمى
   الوظيفي:", others don't, or omit it entirely). Guessing a structured split
   from that would risk misattributing information that was never approved
   in structured form — so it stays exactly as approved, inside `NOTE`.

## Validation performed on this build

- CSV contacts: 50. VCF VCARDs: 50 (exact match).
- Contacts with phone: 49. Without: 1 (expected, not an error).
- No duplicate names. No duplicate phone numbers. No malformed phone numbers
  (all normalize to `+966` followed by 9 digits).
- Field-by-field comparison of all 50 contacts: `FN`, phone digits, and the
  complete `NOTE` text match the source CSV exactly — zero mismatches.
- Multiline notes (e.g. 15-line entries) round-trip exactly.
- Whole CSV file decodes cleanly as UTF-8.
- `file(1)` identifies the output as "vCard visiting card, version 3.0".
- No absolute local machine paths (`/Users/`, `/Downloads/`, `file://`,
  `localhost`, etc.) appear anywhere in `index.html`, `assets/`, `files/`,
  or `tools/build_vcf.py` — every reference is a relative path
  (`files/fellowship-contacts.vcf`, `assets/styles.css`, etc.), so the page
  works unmodified on any static HTTPS host.

## Design

The visual design (colors, typography, logos, layout, cards, icons,
animation) matches the approved Fellowship networking video and is locked.
Do not change it without new approval.

## Deployment reminders

- Not yet deployed. No QR code has been touched.
- When deploying, if the host allows setting MIME types, serving
  `files/fellowship-contacts.vcf` as `text/vcard` is ideal for the phone's
  contact-import flow, but plain static hosting works fine as-is.
- Do not modify `fellowship_directors_cut.html`, any video scene, or the
  existing QR code from this project.
