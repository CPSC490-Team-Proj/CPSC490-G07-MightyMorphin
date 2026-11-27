# Prototype

Proof-of-concept code for 〈project title〉. **Prototype v0 is due Sep 27** with
the proposal, and it grows every sprint; the Week-8 in-class check demos from
this folder.

This example implements the login slice behind story
[#3](../../../issues/3) and task [#5](../../../issues/5) — deliberately tiny,
because a prototype exists to answer one risky question, not to be the
product. **Replace it with yours** and keep the shape: a small module, a test
per acceptance criterion, and run instructions below that work on a machine
that has never seen your project.

## How to run

```bash
cd prototype
python login.py                 # smoke run: prints a truncated session token
```

**Page 3 validation screen (#88):**

```bash
cd prototype
python3 -m venv ~/.venvs/materials-db && source ~/.venvs/materials-db/bin/activate
# Windows: py -m venv %USERPROFILE%\.venvs\materials-db, then %USERPROFILE%\.venvs\materials-db\Scripts\activate
pip install -r requirements.txt
uvicorn validation.app:create_app --factory
```

Then open http://127.0.0.1:8000/ and stop the server with Ctrl+C. Keep the
virtual environment **outside the repository** (as above): the harness's secret
scan (G5) reads every file in the repo folder, including a `.venv` inside it, and
reports false alarms in the installed packages. The demo
script and the list of mocked services are in
[Page 3 validation prototype (#88)](#page-3-validation-prototype-88) below.

## How to test

```bash
cd prototype
pip install -r requirements.txt pytest   # once
python -m pytest -q             # login example + page 3 tests
```

CI runs exactly these tests on every pull request (job **Prototype build &
tests**). If you use Node instead of Python, put a `package.json` here with a
`test` script and CI will detect and run that instead.

## What it proves

That credentials can be checked and a session token issued, with unknown-user
and wrong-password failures indistinguishable to the caller — the riskiest
assumption in 〈the epic this belongs to〉.

## Status

| Sprint | Increment |
|---|---|
| v0 (Sep 27) | login check + 4 tests (this example) |
| Sprint 1 | 〈what you added〉 |


## Page 5 analysis prototype (#95)

From the repository root, run `python3 -m http.server 8000 --directory prototype`
and open `http://localhost:8000/ui-tabs/analysis.html`. Node.js 18+ runs the
dependency-free behavioral checks: `node --test prototype/ui-tabs/analysis.test.js`.
The existing login example above is unrelated to analysis and remains unchanged.

This screen uses synthetic records only, with values, units, dates and approval
states in `ui-tabs/analysis.js`. Snowflake, API authorization, Microsoft SSO,
document access, audit logging and export are mocked or unavailable. It performs
no network data retrieval or storage and makes no specification/compliance claims.
Plain HTML/JavaScript follows the existing prototype style; it does not settle
the production React/Vue decision.

Select at least two compatible approved values for comparison or trend; range
supports one value. Use the property/view controls to change the table and chart.
Record 3 demonstrates incompatible units, record 4 a missing strength, and record
5 an unapproved record. Clear the selection to see an empty state. Toggle
Simulate service failure to test retry without losing selection. No conversion
is performed; the table retains the underlying numeric value without display
rounding. JavaScript numbers have normal floating-point limitations, so the
production decimal precision contract remains an integration requirement.

The Materials page now forwards selected IDs using `?ids=1,2`. Only fixture IDs
1–5 resolve; unknown incoming IDs are reported instead of invented data. The
Page 4 demo's display labels are separate fixtures; shared-record integration
with the Materials owner is still required. Trend uses source dates; table rows
identify the record for each point. Backend permission enforcement, production
validation, persistent data, manager-only auditing and export require follow-up.

## Page 3 validation prototype (#88)

Wireframe page 3, "Validate extracted information", with a working backend. It
follows the page 3 sequence diagram
([#87](https://github.com/CPSC490-Team-Proj/CPSC490-G07-MightyMorphin/issues/87),
`docs/design/sequence-validation/`): load a pending or flagged record beside its
source PDF, save corrections as a draft, resolve flags, and approve. Every rule
is enforced by the backend, and each write is one transaction.

### Run it

Needs Python 3.12 or newer (CI uses 3.12). From the repository root:

```bash
cd prototype
python3 -m venv ~/.venvs/materials-db             # Windows: py -m venv %USERPROFILE%\.venvs\materials-db
source ~/.venvs/materials-db/bin/activate         # Windows: %USERPROFILE%\.venvs\materials-db\Scripts\activate
pip install -r requirements.txt
uvicorn validation.app:create_app --factory
```

Open http://127.0.0.1:8000/ (it redirects to `/ui-tabs/validation.html`). The
interactive API documentation is at http://127.0.0.1:8000/docs. The demo
data is rebuilt from fixtures on every start and by **Reset demo data**.
Settings are in `.env.example` (one optional setting, no secrets). The app
refuses a non-empty data folder that it did not create (one without its marker
file). In its own folder it deletes and rebuilds only the database file and the
`s3/` subfolder.

### Test it

```bash
cd prototype
pip install -r requirements.txt pytest
python -m pytest -q
```

`tests/test_validation.py` holds the page 3 tests. Each test name starts with
`test_acN_`, where N is the position (1–9) of the #88 acceptance criterion it
checks. CI runs them in the **Prototype build &
tests** job.

### Demo script

| Record | Shows |
|---|---|
| #1 `vendor-coc-001.pdf`, Flagged | The wireframe example: tensile strength has low confidence, elongation is missing. Click **Approve record**: refused with both flags listed. Type `18` for elongation, tick **Checked against PDF** on tensile strength, **Save draft**, then **Approve record**. |
| #2 `vendor-test-report-002.pdf`, Pending | No flags, so it can be approved directly. Type `abc` or `5000` in a value and **Save draft** to see the automatic checks reject it (HTTP 422, nothing saved). |
| #3 `vendor-coc-003.pdf`, Flagged | Its PDF copy is missing from storage: the preview shows the problem and **Approve record** is disabled. The backend also refuses it (HTTP 409). |
| #4 `vendor-coc-004.pdf`, Approved | Opens read-only; draft and approve requests return HTTP 409. |

A draft never changes the review status (as in the sequence diagram); only
approval does. Storage failure: click **Simulate storage failure on next write**, then save a
draft, or approve a record that is ready (for example #2). The write fails inside its transaction (HTTP 503), is rolled back, and the
record keeps its values and its Pending or Flagged status. Retrying works.

### Code layout

The files follow the participants in the sequence diagram.

| Path | Diagram participant | Stand-in for |
|---|---|---|
| `ui-tabs/validation.html`, `validation.js` | Web UI (page 3) | Front-end framework (React or Vue, deferred) |
| `validation/app.py` | Backend API | FastAPI, provisional under #78 |
| `validation/checks.py` | Automatic checks | Required fields, number format, unit and plausible range |
| `validation/store.py` | Snowflake | SQLite, using the ER diagram's table and column names |
| `validation/documents.py` | AWS S3 (proposed) | A local folder; SHA-256 checksum per PDF |
| `validation/fixtures.py` | (none) | Synthetic records and generated PDFs |

### What is mocked or not built

- **Edwards Microsoft SSO** is mocked as one fixed "Demo Reviewer". There are no
  roles or permissions, so the Manager audit-event endpoint
  (`/manager/records/{id}/audit-events`) has no access control.
- **Snowflake** is replaced by SQLite. Only the tables page 3 needs are created.
  `SOURCE_DOCUMENT.filename` is added because the ER diagram has no file name column.
- **AWS S3** is replaced by a folder under `.data/`. The load response gives the
  screen a PDF address (`/records/{id}/pdf`) instead of the PDF itself, and the
  backend re-checks the checksum when serving it. Streaming versus a short-lived
  S3 link is still undecided.
- **OCR extraction** is mocked: the fixture values and their confidence numbers
  stand in for the three OCR passes. Aggregating confidence, and the about-90%
  threshold, are not implemented.
- **Data is synthetic.** Material IDs, lots, vendors and values are invented,
  and each generated PDF is stamped "SYNTHETIC SAMPLE - NOT A REAL CERTIFICATE".
  The plausible ranges in `checks.py` are broad sanity limits, not material
  specifications.
- **Not built:** rejecting a record, Re-extract / replace (the button is
  disabled), highlighting where a value appears in the PDF, two reviewers
  editing one draft at once, and the page 2 queue handoff (use the record
  picker). Units are not converted, so only each property's standard unit is
  accepted.
- `GET /materials` returns approved records only. It is the data that search
  (page 4) and analysis (page 5) should read. Those pages still use their own
  fixtures, so an approval here does not appear in them yet.
- `/demo/reset`, `/demo/fail-next-write` and `/demo/state` exist only for the demo.
- **Not secured:** writes must be JSON requests, which blocks plain cross-site
  form posts, but there is no login, CSRF token or rate limit. Run it on
  127.0.0.1 only.
- The **Materials** and **Analysis** tabs open the existing page 4 and page 5
  prototypes. Those pages have no link back to page 3; use the browser's Back
  button. The Analysis page's "Upload shell" link does not work under this server.

### Source-document traceability (#109)

Every material record keeps a permanent link to the PDF it was extracted from:

- `SOURCE_DOCUMENT` stores the S3 object key (unique), the checksum and whether
  the document is a CoC or a test report.
- The extraction hand-off, `Store.add_extracted_record`, always links the new
  record to an existing source document. The fixtures use it in place of real OCR.
- Database triggers stop the link from breaking, even for a connection that
  leaves foreign keys off. A record cannot be moved to another document,
  replaced (`REPLACE INTO`) or deleted. A document's id, key, checksum and type
  cannot be edited, and a document cannot be replaced or deleted while records
  point at it. Other document columns, such as the file name, can still change.
  Replacing a PDF is meant to create a new document row, but replacement is not
  built yet. An extracted record must have at least one property value.
- `GET /records/{id}/source` returns a record's source: file name, CoC or test
  report, vendor, S3 key, checksum, and `copy_check` (`ok`, `missing` or
  `checksum mismatch`). `GET /materials` includes each approved record's
  source (without `copy_check`). For a record still under review, page 3 shows
  the stored copy's key under the PDF preview.

`tests/test_source_references.py` checks the four "Definition of done" items
of #109. Each test name starts with `test_dodN_`. The tests show that the
reference is unchanged after rejected edits, corrections, a failed approval
and approval, and that it is still there when the database file is reopened.
It is still SQLite, not Snowflake. Standard Snowflake tables do not enforce
unique or foreign keys and have no triggers, so production needs these rules
in the backend, the extraction service and table privileges (see proposal §4).
