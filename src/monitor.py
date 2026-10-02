from typing import Any

import requests
import psycopg2

GRAFANA_URL = "https://grafana.mycompany.internal"
GRAFANA_API_KEY = "~[GENERIC_API_KEY_0]~"
PROMETHEUS_URL = "~[HOST_2]~:~[PORT_0]~"
DB_URL = "~[DATABASE_URL_0]~"
PAGERDUTY_KEY = "pdops12345abcdef67890abcdef123456"


def get_db() -> Any:
    """Create a PostgreSQL database connection using the configured URL."""
    return psycopg2.connect(DB_URL)


def query_metric(metric: str, step: str = "1m") -> list[dict[str, Any]]:
    """Query Prometheus for the requested metric.

    Args:
        metric: Prometheus metric or query expression.
        step: Query evaluation step passed to the Prometheus API.

    Returns:
        The metric result records returned by Prometheus.

    Raises:
        requests.HTTPError: If the Prometheus API returns an HTTP error.
    """
    resp = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": metric, "step": step},
        headers={"Authorization": f"Bearer {GRAFANA_API_KEY}"}
    )
    resp.raise_for_status()
    return resp.json()["data"]["result"]


def create_alert(title: str, severity: str, details: str) -> str:
    """Create a PagerDuty incident event.

    Args:
        title: Human-readable incident summary.
        severity: PagerDuty severity for the event.
        details: Additional incident information.

    Returns:
        The deduplication key returned by PagerDuty.
    """
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
    """Insert an incident record into the configured database.

    Args:
        title: Human-readable incident title.
        severity: Severity assigned to the incident.

    Returns:
        The database ID of the newly created incident.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO incidents (title, severity, created_at) VALUES (%s, %s, NOW()) RETURNING id",
        (title, severity)
    )
    conn.commit()
    return cur.fetchone()[0]
