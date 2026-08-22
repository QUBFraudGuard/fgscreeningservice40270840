import os
import requests

REPUTATION_SERVICE_URL = os.environ.get(
    "REPUTATION_SERVICE_URL", "http://reputation.40270840.qpc.qubcloud.uk/"
)
RISK_THRESHOLD = int(os.environ.get("REPUTATION_RISK_THRESHOLD", "70"))

def check(transaction):
    try:
        resp = requests.get(
            REPUTATION_SERVICE_URL,
            params={"card": transaction["card"]},
            timeout=1.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"reputation service call failed: {e}")  # temporary debug logging
        return {"reason": "reputation check unavailable"}

    if data["risk_score"] > RISK_THRESHOLD:
        return {"reason": f"reputation score {data['risk_score']} exceeds threshold"}
    return None