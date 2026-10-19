# QUBCloud-FraudGuard — Screening Service (Python / Flask)

# fgscreeningservice40270840

The fast half of QUBCloud-FraudGuard's screening. It runs the cheap, local checks on a batch of transactions and returns a decision for each.

Part of [QUBCloud-FraudGuard](https://github.com/QUBFraudGuard).

## Checks

| Check | Flags a transaction when |
| --- | --- |
| Amount | The amount is over the threshold |
| Blocklist | The card is on the blocklist |
| Country | The country is on the restricted list |

Checks run in order and stop at the first match. Each decision is `OK`, `SUSPICIOUS` or `ERROR` (malformed input), with a reason. The slow external reputation check lives in its own service, [fgreputationservice](https://github.com/QUBFraudGuard/fgreputationservice40270840), so it can scale or fail independently.

## API

```
GET /screen?items=5000-1234-UK,50000-9999-UK
```

```json
{
  "results": [
    { "transaction": "5000-1234-UK", "decision": "OK" },
    { "transaction": "50000-9999-UK", "decision": "SUSPICIOUS", "reason": "amount over threshold" }
  ],
  "total_checked": 2,
  "flagged": 1
}
```

`GET /health` returns the service status.

## Design

- **Stateless:** every request is handled from its own input. Blocklists are hardcoded and loaded once at startup.
- **Input validation is centralised** in the orchestrator rather than repeated in each check.

## Testing

31 pytest tests cover each check's decision boundaries and failure modes, the orchestrator (malformed input, stop at first match, mixed batches), and the reputation check with its external lookup mocked. GitLab CI runs them on every push.

```bash
pip install -r requirements.txt
python -m pytest -q
```

## Run it

```bash
git clone https://github.com/QUBFraudGuard/fgscreeningservice40270840.git
cd fgscreeningservice40270840
docker build -t fgscreeningservice40270840 .
docker run -p 8070:8070 fgscreeningservice40270840
```


