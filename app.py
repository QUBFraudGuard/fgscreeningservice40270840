# ============================================================================
# app.py  —  THE WEB SERVER FOR THE SCREENING SERVICE (Python + Flask)
# ============================================================================
#
# screening.py knows HOW to check a transaction, but it can't talk to the
# internet by itself. This file wraps that logic in a tiny web server using
# Flask, so the web page can ask it questions over HTTP.
#
# It offers two web addresses ("endpoints"):
#     GET /screen?items=...   -> check a batch of transactions, return JSON
#     GET /health             -> say "ok" so we can tell the service is alive
#
# Reminder: this service is STATELESS. It reads the THRESHOLD once when it
# starts and never saves anything to disk.
# ============================================================================

import os  # lets us read environment variables (settings from outside the code)

from flask import Flask, request, jsonify  # the web framework

from screening import screen_batch  # our actual fraud-check logic
from full_screening import screen_batch_full

# Create the Flask web application.
app = Flask(__name__)

# THRESHOLD is the amount limit. We read it from an environment variable so it
# can be changed WITHOUT editing the code. If it isn't set, we default to 10000.
THRESHOLD = float(os.environ.get("THRESHOLD", "10000"))

# The network port this service listens on. Default 8070.
PORT = int(os.environ.get("PORT", "8070"))


@app.after_request
def add_cors_headers(response):
    # The web page runs on a different address (port 8080) from this service,
    # so browsers block the request by default for security. This header tells
    # the browser "it's fine, let them talk to me". (CORS = Cross-Origin
    # Resource Sharing.)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# This function runs for BOTH the root "/" and "/screen". Listing two routes on
# one function means these two addresses behave identically:
#     http://localhost:8070/?items=...        (the root)
#     http://localhost:8070/screen?items=...  (the named endpoint)
@app.route("/", methods=["GET"])
@app.route("/screen", methods=["GET"])
def screen():
    # Read the "items" value from the web address.
    # For  /screen?items=5000-1234-UK,200-4321-US  this gives us that text.
    # If "items" is missing, we use "" (an empty string) instead.
    items = request.args.get("items", "")

    # Hand the text to our checker and get back the results.
    result = screen_batch_full(items, THRESHOLD)

    # jsonify turns our Python dictionary into a proper JSON web response.
    return jsonify(result)


# A simple "are you alive?" endpoint. Handy for testing and for Docker.
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# This block only runs when we start the file directly with `python app.py`.
if __name__ == "__main__":
    # host="0.0.0.0" means "accept connections from anywhere", which is needed
    # so the service is reachable from outside its Docker container.
    app.run(host="0.0.0.0", port=PORT)
