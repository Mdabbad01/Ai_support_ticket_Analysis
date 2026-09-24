import pandas as pd

from app.query_engine import QueryEngine


def create_test_dataframe():

    return pd.DataFrame({
        "ticket_id": [
            "T001",
            "T002",
            "T003",
            "T004",
            "T005",
            "T006"
        ],
        "created_at": [
            "2026-09-22",
            "2026-09-23",
            "2026-09-23",
            "2026-09-24",
            "2026-09-24",
            "2026-09-24"
        ],
        "category": [
            "Technical",
            "Billing",
            "Technical",
            "General",
            "Technical",
            "Billing"
        ],
        "priority": [
            "High",
            "Medium",
            "Critical",
            "Low",
            "Critical",
            "High"
        ],
        "status": [
            "Open",
            "Resolved",
            "Open",
            "Resolved",
            "Escalated",
            "Resolved"
        ],
        "response_time_hrs": [
            2.5,
            1.5,
            4.0,
            3.0,
            6.0,
            2.0
        ],
        "resolution_time_hrs": [
            None,
            5.0,
            None,
            2.0,
            15.0,
            8.0
        ],
        "agent_id": [
            "AGT-01",
            "AGT-02",
            "AGT-01",
            "AGT-03",
            "AGT-01",
            "AGT-02"
        ],
        "customer_rating": [
            None,
            4.5,
            None,
            5.0,
            None,
            4.0
        ]
    })


# ============================================================
# BASIC TESTS
# ============================================================


def test_count_open_tickets():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "count",
        "filters": {
            "status": "Open"
        }
    }

    result = engine.execute(query_plan)

    assert result["count"] == 2


def test_count_technical_tickets():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "count",
        "filters": {
            "category": "Technical"
        }
    }

    result = engine.execute(query_plan)

    assert result["count"] == 3


def test_average_customer_rating():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "average",
        "column": "customer_rating",
        "filters": {
            "status": "Resolved"
        }
    }

    result = engine.execute(query_plan)

    assert result["average"] == 4.5


def test_group_count_by_agent():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "group_count",
        "group_by": "agent_id",
        "filters": {}
    }

    result = engine.execute(query_plan)

    groups = result["groups"]

    assert groups[0]["agent_id"] == "AGT-01"
    assert groups[0]["count"] == 3


def test_list_tickets():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "list",
        "columns": [
            "ticket_id",
            "status"
        ],
        "filters": {
            "status": "Open"
        }
    }

    result = engine.execute(query_plan)

    assert len(result["rows"]) == 2


# ============================================================
# NEW NUMERIC FILTER TESTS
# ============================================================


def test_resolution_time_greater_than_12():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "list",
        "columns": [
            "ticket_id",
            "resolution_time_hrs"
        ],
        "filters": {
            "resolution_time_hrs": {
                "operator": ">",
                "value": 12
            }
        }
    }

    result = engine.execute(query_plan)

    rows = result["rows"]

    assert len(rows) == 1
    assert rows[0]["ticket_id"] == "T005"
    assert rows[0]["resolution_time_hrs"] == 15.0


def test_resolution_time_less_than_or_equal_to_8():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "list",
        "columns": [
            "ticket_id",
            "resolution_time_hrs"
        ],
        "filters": {
            "resolution_time_hrs": {
                "operator": "<=",
                "value": 8
            }
        }
    }

    result = engine.execute(query_plan)

    rows = result["rows"]

    assert len(rows) == 3


# ============================================================
# MULTIPLE VALUE FILTER TEST
# ============================================================

def test_unresolved_status_filter():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "count",
        "filters": {
            "status": [
                "Open",
                "Escalated"
            ]
        }
    }

    result = engine.execute(query_plan)

    assert result["count"] == 3



# ============================================================
# CRITICAL UNRESOLVED > 12 HOURS
# ============================================================


def test_critical_unresolved_over_12_hours():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "list",
        "columns": [
            "ticket_id",
            "priority",
            "status",
            "resolution_time_hrs"
        ],
        "filters": {
            "priority": "Critical",
            "status": [
                "Open",
                "Escalated"
            ],
            "resolution_time_hrs": {
                "operator": ">",
                "value": 12
            }
        }
    }

    result = engine.execute(query_plan)

    rows = result["rows"]

    assert len(rows) == 1
    assert rows[0]["ticket_id"] == "T005"


# ============================================================
# TIME RANGE TEST
# ============================================================


def test_this_month_filter():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "count",
        "filters": {},
        "time_range": "this_month"
    }

    result = engine.execute(query_plan)

    # All test records are from September 2026
    assert result["count"] == 6


# ============================================================
# GROUP COUNT + TIME RANGE + LIMIT
# ============================================================


def test_most_resolved_agent_this_month():

    df = create_test_dataframe()

    engine = QueryEngine(df)

    query_plan = {
        "operation": "group_count",
        "group_by": "agent_id",
        "filters": {
            "status": "Resolved"
        },
        "time_range": "this_month",
        "limit": 1
    }

    result = engine.execute(query_plan)

    groups = result["groups"]

    assert len(groups) == 1
    assert groups[0]["agent_id"] == "AGT-02"
    assert groups[0]["count"] == 2