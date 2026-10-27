# Test plan: JSONPlaceholder posts API

## What is under test

[JSONPlaceholder](https://jsonplaceholder.typicode.com) is a free public REST API for practice. The suite covers the `/posts` resource and its related `/comments` route.

It is a *fake* API: write requests (POST, PUT, PATCH, DELETE) return realistic responses but nothing is saved. The tests are written to match that.

## Goals

1. Confirm that valid requests return the right status code, headers and data shape.
2. Confirm that invalid input is handled, and record where it is not.
3. Probe boundaries and unusual input that real users or attackers might send.

## Approach

| Area | What the tests check | Marker |
|---|---|---|
| Reading posts | Status 200, JSON content type, 100 posts, unique IDs, field names and types, filtering by user, nested vs filtered routes return the same comments, response time under 5 seconds | `positive` |
| Writing posts | Create returns 201 and echoes data, PUT replaces, PATCH changes only the given field, DELETE returns 200 | `positive` |
| Invalid input | Unknown IDs (`0`, `-1`, `101`, `abc`, very large) return 404 with an empty body, unknown route returns 404 | `negative` |
| Known issues | Empty payload, wrong data type and update of a missing post should be rejected but are not | `known_bug` |
| Edge cases | Filters with no match, non-numeric filter, `_limit` at 1, 5 and above the total, Unicode and emoji, a 10,000-character title, SQL and script injection strings | `edge` |

## How known issues are handled

Tests for behaviour that is wrong today are marked `xfail` with a bug ID in the reason. They still run every time:

- `XFAIL` means the bug is still there, as expected.
- `XPASS` means the API now behaves correctly, so the marker can be removed.

This keeps the pipeline green while making every known problem visible in the test output.

## Design decisions

- **One shared client** (`tests/api/conftest.py`) holds the base URL, a 10-second timeout and automatic retries on 502, 503 and 504, so a temporary network blip does not fail the run.
- **Base URL from an environment variable** (`API_BASE_URL`), so the same tests can run against another environment.
- **Arrange, act, assert** layout in each test, with one behaviour per test, so a failure points to one cause.
- **Parametrised tests** for lists of similar inputs, so adding a case is one line.

## Out of scope

- Authentication and authorisation: the API has none.
- Load and performance testing beyond a single response-time check.
- Data persistence: the API does not save writes.

## Risks and limits

- The suite depends on a public service. If it is down, tests fail for reasons outside the code. Retries reduce this but cannot remove it.
- Some tests assume writes are not saved, for example that there are always exactly 100 posts. Against a real backend that saves data, those tests would need their own test data set up and cleaned up per run.
