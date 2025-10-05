import json
from flask import Flask, jsonify
from src.persistence import get_connection
from datetime import datetime

app = Flask(__name__)

def fetch_anomalies(metric_name=None):
    conn = get_connection()
    cur = conn.cursor()
    selector = (
        "SELECT id, timestamp, metric_name, metric_value, threshold, status, "
        "detection_method, anomaly_score, context, config "
        "FROM anomalies "
    )
    if metric_name:
        query = selector + "WHERE metric_name=%s ORDER BY timestamp DESC"
        cur.execute(query, (metric_name,))
    else:
        query = selector + "ORDER BY timestamp DESC"
        cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    anomalies = []
    for r in rows:
        def parse_json_field(field):
            if isinstance(field, dict):
                return field
            if field is None:
                return None
            try:
                return json.loads(field)
            except Exception:
                return field

        anomalies.append({
            "id": r[0],
            "timestamp": r[1].isoformat() if hasattr(r[1], "isoformat") else r[1],
            "metric_name": r[2],
            "metric_value": r[3],
            "threshold": r[4],
            "status": r[5],
            "detection_method": r[6],
            "anomaly_score": r[7],
            "context": parse_json_field(r[8]),
            "config": parse_json_field(r[9]),
        })
    return anomalies

@app.route("/anomalies", methods=["GET"])
def get_all_anomalies():
    return jsonify(fetch_anomalies())

@app.route("/anomalies/<metric_name>", methods=["GET"])
def get_anomalies_by_metric(metric_name):
    return jsonify(fetch_anomalies(metric_name))

@app.route("/", methods=["GET"])
@app.route("/ui", methods=["GET"])
def anomaly_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Anomalies Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                background: #f6f8fa;
                margin: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                min-height: 100vh;
            }
            h1 {
                color: #2e3854;
                margin-top: 40px;
                margin-bottom: 8px;
                text-align: center;
            }
            .table-scroll {
                overflow-x: auto;
                width: 100vw;
                padding: 0 0;
                margin: 0 auto 30px auto;
                display: flex;
                justify-content: center;
            }
            table {
                border-collapse: separate;
                border-spacing: 0;
                margin: 0 auto;
                min-width: 1100px;
                max-width: 90vw;
                background: white;
                box-shadow: 0 1px 4px 0 #d4d6dd82;
                border-radius: 7px;
                overflow: hidden;
            }
            th, td { padding: 10px 14px; font-size: 15px; text-align: left;}
            th {
                background: #e6e8f1;
                position: sticky; top: 0;
                border-bottom: 2px solid #d8daf0;
                color: #233150;
                font-size: 15.5px;
            }
            tr:nth-child(even) { background: #f8f9fb;}
            tr:nth-child(odd) { background: #eef1f6; }
            td, th { border: none; }
            td .badge {
                padding: 2px 10px;
                border-radius: 11px;
                color: white;
                font-weight: 600;
                font-size: 14px;
                display: inline-block;
            }
            td .badge.ok { background: #28b77e; }
            td .badge.anomaly { background: #e14d4d; }
            td .badge { background: #ffb300;}
            .nowrap { white-space: nowrap; }
            .json {
                max-width: 270px; 
                overflow-x: auto;
                word-break: break-word;
                display: block;
                font-family: Menlo, monospace;
                font-size: 12.3px;
                background: #f0f2f6;
                color: #2d3648;
                border-radius: 5px;
                padding: 3px 5px;
            }
            button {
                background: #5353fa;
                color: #fff;
                font-weight: 600;
                border: none;
                border-radius: 4px;
                padding: 7px 16px;
                margin-top: 8px;
                font-size: 15px;
                cursor: pointer;
                margin-left: 16px;
            }
            button:hover { background: #2d37b8 }
            @media (max-width: 1280px) { table { min-width:900px; font-size:13px } }
            @media (max-width: 900px) { table { min-width:600px; font-size:11.8px } }
            @media (max-width: 700px) {
                table { min-width: 450px; }
                th, td { font-size: 10.9px;}
                .json { max-width: 120px;}
            }
        </style>
    </head>
    <body>
        <h1>Anomaly Detection Dashboard</h1>
        <button onclick="fetchAndRender()">Refresh</button>
        <br>
        <div class="table-scroll">
        <table id="anomalies"><thead>
            <tr>
                <th>ID</th>
                <th>Detected At</th>
                <th>Value</th>
                <th>Method</th>
                <th>Score</th>
                <th>Context</th>
                <th>Config</th>
            </tr>
        </thead>
        <tbody></tbody></table>
        </div>
        <script>
        function htmlEscape(str) {
            return String(str).replace(/[&<>'"]/g, x =>
                ({'&':'&','<':'<','>':'>',"'":'&#39;','"':'"'}[x])
            );
        }
        function preJSON(val) {
            if (!val) return "";
            try {
                return "<pre class='json'>" + htmlEscape(JSON.stringify(val, null, 2)) + "</pre>";
            } catch { return "<pre class='json'>"+htmlEscape(String(val))+"</pre>"; }
        }
        async function fetchAndRender() {
            let tbody = document.querySelector("#anomalies tbody");
            tbody.innerHTML = "<tr><td colspan=7>Loading...</td></tr>";
            let res = await fetch("/anomalies");
            let data = await res.json();
            if (!Array.isArray(data)) return;
            tbody.innerHTML = "";
            for (let row of data) {
                let tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class='nowrap'>${htmlEscape(row.id)}</td>
                    <td class='nowrap'>${htmlEscape(row.timestamp)}</td>
                    <td>${htmlEscape(row.metric_value)}</td>
                    <td>${htmlEscape(row.detection_method ?? "")}</td>
                    <td>${htmlEscape(row.anomaly_score ?? "")}</td>
                    <td>${preJSON(row.context)}</td>
                    <td>${preJSON(row.config)}</td>
                `;
                tbody.appendChild(tr);
            }
        }
        fetchAndRender();
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
