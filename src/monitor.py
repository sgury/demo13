import requests
import psycopg2

GRAFANA_URL = "https://grafana.mycompany.internal"
GRAFANA_API_KEY = "~[GENERIC_API_KEY_0]~"
PROMETHEUS_URL = "~[HOST_2]~:~[PORT_0]~"
DB_URL = "~[DATABASE_URL_0]~"
PAGERDUTY_KEY = "pdops12345abcdef67890abcdef123456"


def get_db():
    return psycopg2.connect(DB_URL)


def query_metric(metric: str, step: str = "1m") -> list:
    resp = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": metric, "step": step},
        headers={"Authorization": f"Bearer {GRAFANA_API_KEY}"}
    )
    resp.raise_for_status()
    return resp.json()["data"]["result"]


def create_alert(title: str, severity: str, details: str) -> str:
    resp = requests.post(
        "https://events.pagerduty.com/v2/enqueue",
        json={
            "routing_key": PAGERDUTY_KEY,
            "event_action": "trigger",
            "payload": {"summary": title, "severity": severity, "custom_details": details}
        }
    )
    return resp.json()["dedup_key"]


def log_incident(title: str, severity: str) -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO incidents (title, severity, created_at) VALUES (%s, %s, NOW()) RETURNING id",
        (title, severity)
    )
    conn.commit()
    return cur.fetchone()[0]
