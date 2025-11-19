from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# This route will receive Jira webhooks
@app.route('/jira', methods=['POST'])
def jira_webhook():
    try:
        data = request.get_json(force=True)

        if data.get('webhookEvent') == 'jira:issue_created':
            issue = data['issue']
            key = issue['key']
            project = issue['fields']['project']['key']
            summary = issue['fields'].get('summary', '(no summary)')
            creator = issue['fields']['creator'].get('displayName', 'Unknown')

            log_line = f"{datetime.utcnow().isoformat()}Z | {project} | {key} | {summary} | {creator}\n"
            print("NEW JIRA ISSUE →", log_line)

            # Save to file (visible in Render Logs + disk)
            with open("jira_issues.log", "a", encoding="utf-8") as f:
                f.write(log_line)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/')
def home():
    return """
    <h1>Jira Webhook is LIVE and WORKING!</h1>
    <p>Use this URL in Jira → System → Webhooks:</p>
    <h2><code>https://YOUR-APP.onrender.com/jira</code></h2>
    <p>Events: Issue created | Filter: project = TTO (or all)</p>
    <hr>
    <p>Check logs below to see new issues appear instantly</p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
