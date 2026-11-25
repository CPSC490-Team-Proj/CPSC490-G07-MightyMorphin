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

## How to test

```bash
cd prototype
pip install pytest              # once
python -m pytest tests -q       # 4 tests
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
