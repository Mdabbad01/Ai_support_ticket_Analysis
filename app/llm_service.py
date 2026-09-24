import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMService:

    def __init__(self):

        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set in the .env file"
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

        self.model = "gemini-2.5-flash"

    def generate_query_plan(
        self,
        question: str,
        columns: list,
        unique_values: dict
    ) -> dict:

        prompt = f"""
You are an AI assistant for a customer support ticket
analytics system.

Your task is to convert a user's natural-language question
into a structured JSON query plan.

The actual data is stored in a Pandas DataFrame.
Python will execute the query.

You must NOT calculate the answer yourself.

==================================================
DATASET COLUMNS
==================================================

{columns}

==================================================
AVAILABLE VALUES
==================================================

{unique_values}

==================================================
SUPPORTED OPERATIONS
==================================================

1. count
2. average
3. sum
4. min
5. max
6. list
7. group_count
8. anomaly_detection

==================================================
NORMAL QUERY PLANS
==================================================

COUNT:

{{
    "operation": "count",
    "filters": {{}}
}}

AVERAGE:

{{
    "operation": "average",
    "column": "customer_rating",
    "filters": {{}}
}}

SUM:

{{
    "operation": "sum",
    "column": "resolution_time_hrs",
    "filters": {{}}
}}

MIN:

{{
    "operation": "min",
    "column": "resolution_time_hrs",
    "filters": {{}}
}}

MAX:

{{
    "operation": "max",
    "column": "resolution_time_hrs",
    "filters": {{}}
}}

LIST:

{{
    "operation": "list",
    "columns": [
        "ticket_id",
        "priority",
        "status"
    ],
    "filters": {{}}
}}

GROUP COUNT:

{{
    "operation": "group_count",
    "group_by": "agent_id",
    "filters": {{}}
}}

==================================================
ANOMALY DETECTION
==================================================

If the user asks to find anomalies, unusual tickets,
outliers, unusually long resolution times, or similar
problems, use:

{{
    "operation": "anomaly_detection",
    "anomaly_type": "resolution_time",
    "time_range": "this_week"
}}

Possible anomaly_type values:

- resolution_time
- critical_unresolved

Possible time_range values:

- all
- today
- this_week
- this_month

==================================================
FILTERS
==================================================

Filters can contain categorical conditions.

Example:

{{
    "operation": "count",
    "filters": {{
        "status": "Open",
        "priority": "Critical"
    }}
}}

==================================================
NUMERIC CONDITIONS
==================================================

For numeric conditions, use:

{{
    "column": {{
        "operator": ">",
        "value": 12
    }}
}}

Example:

{{
    "operation": "list",
    "columns": [
        "ticket_id",
        "priority",
        "resolution_time_hrs"
    ],
    "filters": {{
        "priority": "Critical",
        "resolution_time_hrs": {{
            "operator": ">",
            "value": 12
        }}
    }}
}}

Supported operators:

- >
- <
- >=
- <=
- ==
- !=

==================================================
DATE / TIME RANGE
==================================================

If the user says:

"today"

use:

"today"

If the user says:

"this week"

use:

"this_week"

If the user says:

"this month"

use:

"this_month"

If no time period is mentioned, use:

"all"

==================================================
IMPORTANT RULES
==================================================

1. Return ONLY valid JSON.

2. Do not return markdown.

3. Do not include explanations.

4. Use ONLY dataset columns.

5. Do not invent column names.

6. Use exact column names.

7. Do not calculate answers.

8. "How many" means count.

9. "Average" means average.

10. "Total" means sum.

11. "Minimum" means min.

12. "Maximum" means max.

13. "Show/list tickets" means list.

14. "Count by agent/category/priority/status"
    means group_count.

15. "Find anomalies" means anomaly_detection.

16. "Unusually long resolution time" means
    anomaly_detection with anomaly_type
    resolution_time.

17. "Critical unresolved tickets" means either
    critical_unresolved anomaly detection or
    appropriate filtering.

18. If the user says "this week", preserve
    "this_week" in the query plan.

==================================================
USER QUESTION
==================================================

{question}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        response_text = response.text.strip()

        # Remove possible markdown code fences
        if response_text.startswith("```json"):
            response_text = response_text[7:]

        elif response_text.startswith("```"):
            response_text = response_text[3:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:

            query_plan = json.loads(response_text)

        except json.JSONDecodeError as e:

            raise ValueError(
                f"Gemini returned invalid JSON: {response_text}"
            ) from e

        return query_plan


# --------------------------------------------------
# TEST GEMINI
# --------------------------------------------------

if __name__ == "__main__":

    llm = LLMService()

    columns = [
        "ticket_id",
        "created_at",
        "category",
        "priority",
        "status",
        "response_time_hrs",
        "resolution_time_hrs",
        "agent_id",
        "customer_rating",
        "issue_summary"
    ]

    unique_values = {
        "category": [
            "General",
            "Billing",
            "Technical"
        ],
        "priority": [
            "Low",
            "Medium",
            "High",
            "Critical"
        ],
        "status": [
            "Open",
            "Resolved",
            "Escalated"
        ]
    }

    questions = [
        "How many tickets are currently open?",
        "What is the average customer rating for Technical tickets?",
        "Find anomalies in resolution time this week."
    ]

    for question in questions:

        result = llm.generate_query_plan(
            question=question,
            columns=columns,
            unique_values=unique_values
        )

        print("\nQuestion:")
        print(question)

        print("\nQuery Plan:")

        print(
            json.dumps(
                result,
                indent=4
            )
        )