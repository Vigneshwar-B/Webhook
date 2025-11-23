from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/jira', methods=['POST'])
def jira_webhook():
    try:
        data = request.get_json(force=True)

        # Only react to issue deletion
        if data.get('webhookEvent') == 'jira:issue_deleted':
            issue_key = data['issue']['key']  # ← e.g., TTO-123
            deleter = data.get('user', {}).get('displayName', 'Unknown User')
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            log_line = f"{timestamp} | DELETED | {issue_key} | by {deleter}\n"

            print("ISSUE DELETED →", log_line.strip())

            # Save to persistent log file
            with open("deleted_issues.log", "a", encoding="utf-8") as f:
                f.write(log_line)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "bad payload"}), 400


@app.route('/')
def home():
    return f"""
    <h1>Jira Issue Deletion Webhook – LIVE</h1>
    <p>Only listens for <code>jira:issue_deleted</code></p>
    <p>Deleted issue keys appear instantly in logs!</p>
    <hr>
    <p><strong>YOUR WEBHOOK URL:</strong></p>
    <h2><code>https://webhook-issue-deleted.onrender.com/jira</code></h2>
    <p><small>Use this exact URL in Jira → System → Webhooks</small></p>
    """


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
