# QUBCloud-FraudGuard — Screening Service (Python / Flask)

This is **the brain** of the QUBCloud-FraudGuard app. It is the only part that
actually decides whether a transaction is suspicious. It runs **one simple
check**: if a transaction's amount is over a limit (the *threshold*), flag it.

It is **stateless** — it saves nothing to a database or disk. Give it the same
input and it always returns the same answer.

> The app is made of three separate repositories. The web page calls **both
> backend services directly** — there is no "middle man" in between:
>
> ```
>                       ┌──▶ screening-service  (THIS repo — decides OK / SUSPICIOUS)
>   frontend (web page) ┤
>                       └──▶ country-tally-service  (counts by country)
> ```
>
> This service runs and is tested **completely on its own** — it does not depend
> on the other two.

---

## What it does

You send it transactions written as `amount-card-country` (e.g. `5000-1234-UK`),
separated by commas, and it returns a decision for each one:

- **OK** — the amount is within the limit.
- **SUSPICIOUS** — the amount is over the threshold.
- **ERROR** — the transaction was written wrongly (it never crashes; it just
  reports the bad one and carries on with the rest).

---

## The endpoints (web addresses it answers)

### `GET /screen?items=<comma-separated transactions>`

The root path `/` is an alias for `/screen`, so `GET /?items=...` returns the
same result.

```
GET /screen?items=5000-1234-UK,50000-9999-UK,200-4321-US,800-0000-CN
```

Returns JSON — one decision per transaction, plus two totals:

```json
{
  "results": [
    { "transaction": "5000-1234-UK",  "decision": "OK" },
    { "transaction": "50000-9999-UK", "decision": "SUSPICIOUS", "reason": "amount over threshold" },
    { "transaction": "200-4321-US",   "decision": "OK" },
    { "transaction": "800-0000-CN",   "decision": "OK" }
  ],
  "total_checked": 4,
  "flagged": 1
}
```

### `GET /health`

Returns `{"status": "ok"}` — a simple "am I alive?" check.

---

## Settings (environment variables)

Read when the service starts, so nothing is hard-coded:

| Setting     | Default | What it does                                   |
|-------------|---------|------------------------------------------------|
| `THRESHOLD` | `10000` | Amounts **strictly greater** than this are SUSPICIOUS. |
| `PORT`      | `8070`  | The port the service listens on.               |

---

## How to build and run it (Docker)

From inside this repository:

```bash
# 1. Build the image
docker build -t screening-service .

# 2. Run it (port 8070, limit set to 10000)
docker run -d --name screening-service -p 8070:8070 \
  -e THRESHOLD=10000 screening-service

# 3. Try it
curl "http://localhost:8070/health"
curl "http://localhost:8070/screen?items=5000-1234-UK,50000-9999-UK"
```

Stop and remove it when done:

```bash
docker rm -f screening-service
```

---

## The code (what each file is)

| File                  | What it does                                              |
|-----------------------|----------------------------------------------------------|
| `screening.py`        | The actual fraud check — the important logic.             |
| `app.py`              | Wraps the check in a Flask web service (the endpoints).   |
| `test_screening.py`   | Automated tests for the check.                            |
| `requirements.txt`    | The Python libraries this service needs.                  |
| `Dockerfile`          | How to build the container image.                         |


---

## Running the tests

```bash
# Inside the Python image, without installing anything on your computer:
docker run --rm -v "$PWD":/app -w /app python:3.12-slim \
  sh -c "pip install -q -r requirements.txt && python -m pytest -q"
```

(If you have Python installed locally, `pip install -r requirements.txt` then
`python -m pytest -q` also works.)

The tests cover: a normal batch, the threshold boundary, empty input, and a
malformed transaction.

---

## Note for students

This service has **exactly one check** on purpose. Adding more checks (a
banned-card list, a country rule, card reputation, etc.) is **your task** in the
assignment — see the `NOTE (For Task A)` comment in `screening.py`.
