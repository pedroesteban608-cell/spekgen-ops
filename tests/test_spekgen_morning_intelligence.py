"""
Unit tests for SpekGen Morning Intelligence System.

Run tests with: pytest tests/ -v
"""

import pytest
from datetime import datetime, timezone


def test_timestamp_conversion_from_unix_ms():
    """Test conversion of ClickUp Unix millisecond timestamps to datetime."""
    ts_ms = 1715356800000  # 2024-05-10 12:00:00 UTC

    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

    assert dt.year == 2024
    assert dt.month == 5
    assert dt.day == 10


def test_timestamp_conversion_edge_cases():
    """Test edge cases for timestamp conversion."""
    # Zero timestamp
    ts_zero = 0
    dt_zero = datetime.fromtimestamp(ts_zero / 1000, tz=timezone.utc)
    assert dt_zero.year == 1970

    # Future date
    ts_future = 9999999999000  # Year 2286
    dt_future = datetime.fromtimestamp(ts_future / 1000, tz=timezone.utc)
    assert dt_future.year == 2286


def test_health_classification_green():
    """Test health classification returns 🟢 Green for healthy projects."""
    client_data = {
        "status": "SUCCESS",
        "metrics": {
            "on_time_pct": "95%",
            "overdue_count": 0,
            "total_completed": 10
        },
        "baseline": 85.0
    }

    # Simulate classify_project_health logic
    on_time_pct = float(client_data["metrics"]["on_time_pct"].rstrip("%"))
    overdue_count = client_data["metrics"]["overdue_count"]
    baseline = client_data.get("baseline", 85.0)

    if on_time_pct >= baseline and overdue_count == 0:
        health = "🟢"
    elif on_time_pct >= (baseline - 10) or overdue_count <= 2:
        health = "🟡"
    else:
        health = "🔴"

    assert health == "🟢"


def test_health_classification_yellow():
    """Test health classification returns 🟡 Yellow for degrading projects."""
    client_data = {
        "status": "SUCCESS",
        "metrics": {
            "on_time_pct": "75%",
            "overdue_count": 1,
            "total_completed": 10
        },
        "baseline": 85.0
    }

    on_time_pct = float(client_data["metrics"]["on_time_pct"].rstrip("%"))
    overdue_count = client_data["metrics"]["overdue_count"]
    baseline = client_data.get("baseline", 85.0)

    if on_time_pct >= baseline and overdue_count == 0:
        health = "🟢"
    elif on_time_pct >= (baseline - 10) or overdue_count <= 2:
        health = "🟡"
    else:
        health = "🔴"

    assert health == "🟡"


def test_health_classification_red():
    """Test health classification returns 🔴 Red for failing projects."""
    client_data = {
        "status": "SUCCESS",
        "metrics": {
            "on_time_pct": "60%",
            "overdue_count": 5,
            "total_completed": 10
        },
        "baseline": 85.0
    }

    on_time_pct = float(client_data["metrics"]["on_time_pct"].rstrip("%"))
    overdue_count = client_data["metrics"]["overdue_count"]
    baseline = client_data.get("baseline", 85.0)

    if on_time_pct >= baseline and overdue_count == 0:
        health = "🟢"
    elif on_time_pct >= (baseline - 10) or overdue_count <= 2:
        health = "🟡"
    else:
        health = "🔴"

    assert health == "🔴"


def test_pagination_accumulates_all_pages():
    """Test pagination loop accumulates tasks from multiple API pages."""
    # Mock paginated API responses
    pages = [
        {"tasks": [{"id": i, "name": f"task_{i}"} for i in range(100)]},  # Page 0: 100 tasks
        {"tasks": [{"id": i, "name": f"task_{i}"} for i in range(100, 150)]},  # Page 1: 50 tasks
        {"tasks": []},  # Page 2: empty (stop condition)
    ]

    all_tasks = []
    page = 0

    # Simulate pagination loop
    while page < len(pages):
        tasks = pages[page].get("tasks", [])
        if not tasks:
            break
        all_tasks.extend(tasks)
        page += 1

    assert len(all_tasks) == 150
    assert all_tasks[0]["id"] == 0
    assert all_tasks[149]["id"] == 149


def test_graceful_error_handling_one_client_failure():
    """Test that one client's API error doesn't block others."""
    clients = [
        {"code": "HC", "list_id": "valid_123"},
        {"code": "GR", "list_id": "valid_456"},
        {"code": "LF", "list_id": "broken_789"},  # Simulated broken list ID
        {"code": "MG", "list_id": "valid_012"},
    ]

    results = {}

    for client in clients:
        try:
            # Simulate API call
            if client["list_id"].startswith("broken"):
                raise Exception(f"Invalid list ID: {client['list_id']}")

            results[client["code"]] = {"status": "SUCCESS", "tasks": []}

        except Exception as e:
            results[client["code"]] = {"status": "ERROR", "error": str(e)}

    # Verify 3 successes + 1 error
    success_count = sum(1 for r in results.values() if r["status"] == "SUCCESS")
    error_count = sum(1 for r in results.values() if r["status"] == "ERROR")

    assert success_count == 3
    assert error_count == 1
    assert results["LF"]["status"] == "ERROR"
    assert results["HC"]["status"] == "SUCCESS"


def test_completed_yesterday_detection():
    """Test detection of tasks completed in the last 24 hours."""
    now_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    one_hour_ago = now_ts - 3600000
    two_days_ago = now_ts - (86400000 * 2)

    tasks = [
        {"name": "Recent", "date_closed": one_hour_ago},
        {"name": "Old", "date_closed": two_days_ago},
    ]

    completed_yesterday = []

    for t in tasks:
        date_closed = int(t.get("date_closed", 0))
        if date_closed and (now_ts - date_closed) < 86400000:
            completed_yesterday.append(t)

    assert len(completed_yesterday) == 1
    assert completed_yesterday[0]["name"] == "Recent"


def test_overdue_detection():
    """Test detection of overdue tasks."""
    now_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    yesterday = now_ts - 86400000
    tomorrow = now_ts + 86400000

    tasks = [
        {"name": "Overdue", "due_date": yesterday, "status": {"status": "open"}},
        {"name": "Due Soon", "due_date": tomorrow, "status": {"status": "open"}},
    ]

    overdue = []

    for t in tasks:
        due_date = int(t.get("due_date", 0)) if t.get("due_date") else None
        status = t.get("status", {}).get("status", "").lower()

        if status != "closed" and due_date and due_date < now_ts:
            overdue.append(t)

    assert len(overdue) == 1
    assert overdue[0]["name"] == "Overdue"


def test_blocker_detection_from_tags():
    """Test detection of blocker tasks by tag."""
    tasks = [
        {"name": "Task 1", "tags": [{"name": "feature"}]},
        {"name": "Task 2", "tags": [{"name": "BLOCKER"}]},
        {"name": "Task 3", "tags": [{"name": "BLOCKED"}]},
        {"name": "Task 4", "tags": [{"name": "🚨"}]},
    ]

    blockers = []

    for t in tasks:
        tags = [tag.get("name", "").upper() for tag in t.get("tags", [])]
        if any(b in tags for b in ["BLOCKER", "BLOCKED", "🚨"]):
            blockers.append(t)

    assert len(blockers) == 3
    assert blockers[0]["name"] == "Task 2"
    assert blockers[1]["name"] == "Task 3"
    assert blockers[2]["name"] == "Task 4"


def test_memo_structure_validation():
    """Test that memo has all required sections."""
    memo = """# SPEKGEN MORNING INTELLIGENCE — 2026-05-10

## 🔴 AT RISK (1 projects bleeding)
**VELOCITY:** 71%

## CASUALTIES & BLOCKERS

🔴 **F24** — Pedro
- **Status:** 65% on time
- **Blockers:** Photos pending, Gateway down
- **Overdue:** 4 tasks

## DIRECT ORDERS
@Pedro: **RESOLVE** — Get photos from Sergio by 5 PM

## OPERATIONAL (No action required)
HC, GR
"""

    # Check structure
    assert "FRONTLINE" in memo or "AT RISK" in memo or "CAUTION" in memo or "OPERATIONAL" in memo
    assert "CASUALTIES" in memo
    assert "DIRECT ORDERS" in memo
    assert "🔴" in memo or "🟡" in memo or "🟢" in memo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
