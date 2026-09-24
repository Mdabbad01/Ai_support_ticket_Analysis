import pandas as pd

from app.query_engine import QueryEngine


def create_test_dataframe():

    return pd.DataFrame({
        "ticket_id": [
            "T001",
            "T002",
            "T003",
            "T004"
        ],
        "category": [
            "Technical",
            "Billing",
            "Technical",
            "General"
        ],
        "priority": [
            "High",
            "Medium",
            "Critical",
            "Low"
        ],
        "status": [
            "Open",
            "Resolved",
            "Open",
            "Resolved"
        ],
        "response_time_hrs": [
            2.5,
            1.5,
            4.0,
            3.0
        ],
        "resolution_time_hrs": [
            None,
            5.0,
            None,
            2.0
        ],
        "agent_id": [
            "AGT-01",
            "AGT-02",
            "AGT-01",
            "AGT-03"
        ],
        "customer_rating": [
            None,
            4.5,
            None,
            5.0
        ]
    })


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

    assert result["count"] == 2


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

    assert result["average"] == 4.75


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
    assert groups[0]["count"] == 2


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