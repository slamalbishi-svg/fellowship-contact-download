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
- **There is no separately-approved VCF.** Every VCF output below is
  generated entirely from this CSV by `tools/build_vcf.py`.

## Individual-contact VCF approach (current, recommended)

Real iPhone testing showed that opening a single combined 50-contact VCF
through Safari's inline download preview only surfaces the *first* card —
iOS's "Add All Contacts" flow is not reliably reachable that way. The fix
is architectural, not a formatting tweak: generate **one VCF per contact**
and let the page's search list drive a per-person "إضافة إلى جهات الاتصال"
download. This is the primary, recommended import method now.

- `files/contacts/contact-001.vcf` … `contact-050.vcf` — one VCARD each, in
  the same order as the CSV. Filenames are plain ASCII by design (per the
  approved spec) to avoid any URL/filesystem encoding issues; the Arabic
  name still appears correctly inside the file (`FN`/`N`) and in the
  browser's suggested save-as name (set via the anchor's `download`
  attribute in `assets/app.js`), and on the page itself.
- `files/fellowship-contacts.vcf` — the old combined 50-in-1 file. Still
  generated for archival/testing, but **not linked anywhere on the page**
  since it can't be presented as a reliable iPhone import method.
- `files/fellowship-contacts-individual-vcf.zip` — a convenience archive of
  all 50 individual files. **Admin/internal use only.** Deliberately NOT
  linked anywhere in `index.html` and not reachable from any button or link
  on the public page — a ZIP download was explicitly ruled out as a
  user-facing option on iPhone. It still gets rebuilt by `build_vcf.py` in
  case it's useful for internal record-keeping, but nothing should ever
  point a Fellow at it.
- `assets/contacts-data.js` — generated data file
  (`window.FELLOWSHIP_CONTACTS = [{name, file}, ...]`) that `assets/app.js`
  reads at runtime to render the searchable list and wire up each download
  button. Plain script include, no fetch/backend involved.

## Regenerating everything

```bash
cd tools
python3 build_vcf.py
```

Defaults to reading `../files/fellowship-contacts.csv`. Pass an explicit
path as the one argument to use a different source. Rerun this any time
`files/fellowship-contacts.csv` is replaced with a new approved version —
it regenerates the individual files, the combined archival file, the ZIP,
and `assets/contacts-data.js` together, so they can never drift out of
sync with each other or with the CSV.

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

- CSV contacts: 50. Individual VCF files: 50, each with exactly one
  BEGIN:VCARD/END:VCARD pair. Combined archival VCF: 50 VCARDs (exact match).
- Contacts with phone: 49. Without: 1 (expected, not an error).
- No duplicate names. No duplicate phone numbers. No malformed phone numbers
  (all normalize to `+966` followed by 9 digits).
- Field-by-field comparison of all 50 individual files against the source
  CSV: `FN`, phone digits, and the complete `NOTE` text match exactly for
  every contact — zero mismatches. Same check re-run against the combined
  archival file with the same result.
- Multiline notes (e.g. 15-line entries) round-trip exactly.
- Whole CSV file decodes cleanly as UTF-8.
- `file(1)` identifies both VCF outputs as "vCard visiting card, version 3.0".
- ZIP archive opens cleanly (`zipfile.testzip()` reports no corrupt member)
  and contains exactly the 50 individual files.
- vCard lines are intentionally **unfolded** (one property per line,
  CRLF-terminated) rather than RFC-2425-folded, to remove an entire class
  of mobile-parser edge cases after real-device testing traced a
  first-card-only import to this kind of ambiguity in the old combined file.
- No absolute local machine paths (`/Users/`, `/Downloads/`, `file://`,
  `localhost`, etc.) appear anywhere in `index.html`, `assets/`, `files/`,
  or `tools/build_vcf.py` — every reference is a relative path
  (`files/contacts/contact-001.vcf`, `assets/styles.css`, etc.), so the page
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
