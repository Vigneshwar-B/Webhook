from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/jira', methods=['POST'])
def jira_webhook():
    try:
        data = request.get_json(force=True)

        # Only react to issue deletion
        if data.get('webhookEvent') == 'jira:issue_deleted':
            # Jira sends the deleted issue key here:
            issue_key = data['issue']['key']  # ← This is the ID like TTO-123

            # Who deleted it (optional but nice)
            deleter = data.get('user', {}).get('displayName', 'Unknown User')

            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            log_line = f"{timestamp} | DELETED | {issue_key} | by {deleter}\n"

            print("ISSUE DELETED →", log_line.strip())

            # Save to log file (visible in Render Logs + persistent)
            with open("deleted_issues.log", "a", encoding="utf-8") as f:
                f.write(log_line)

        # Always respond fast so Jira doesn't retry
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "bad payload"}), 400


@app.route('/')
def home():
    return """
    <h1>Jira Issue Deletion Webhook – LIVE</h1>
    <p>Only listens for <code>jira:issue_deleted</code></p>
    <p>Deleted issue keys appear instantly in logs!</p>
    <hr>
    <p>Your URL: <code>https://webhook-1-py.onrender.com/jira</code></p>
    """

if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 10000)))
