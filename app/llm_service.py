import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMService:

    def __init__(self):

        self.api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set "
                "in the .env file"
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

        self.model = "gemini-3.5-flash-lite"

    # =====================================================
    # GENERATE QUERY PLAN
    # =====================================================

    def generate_query_plan(
        self,
        question: str,
        columns: list,
        unique_values: dict
    ) -> dict:

        prompt = f"""
You are an AI assistant for a customer support
ticket analytics system.

Your job is to convert a user's natural-language
question into a structured JSON query plan.

The actual data is stored in a Pandas DataFrame.

Python will execute the query.

You MUST NOT calculate the answer yourself.

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
COUNT
==================================================

Example:

{{
    "operation": "count",
    "filters": {{
        "status": "Open"
    }}
}}

==================================================
AVERAGE
==================================================

Example:

{{
    "operation": "average",
    "column": "customer_rating",
    "filters": {{
        "category": "Technical"
    }}
}}

==================================================
SUM
==================================================

Example:

{{
    "operation": "sum",
    "column": "resolution_time_hrs",
    "filters": {{}}
}}

==================================================
MIN
==================================================

Example:

{{
    "operation": "min",
    "column": "resolution_time_hrs",
    "filters": {{}}
}}

==================================================
MAX
==================================================

Example:

{{
    "operation": "max",
    "column": "resolution_time_hrs",
    "filters": {{}}
}}

==================================================
LIST
==================================================

Example:

{{
    "operation": "list",
    "columns": [
        "ticket_id",
        "priority",
        "status",
        "resolution_time_hrs"
    ],
    "filters": {{}}
}}

==================================================
GROUP COUNT
==================================================

Example:

{{
    "operation": "group_count",
    "group_by": "agent_id",
    "filters": {{}}
}}

==================================================
GROUP COUNT WITH TIME RANGE
==================================================

For:

"Which agent resolved the most tickets this month?"

use:

{{
    "operation": "group_count",
    "group_by": "agent_id",
    "filters": {{
        "status": "Resolved"
    }},
    "time_range": "this_month",
    "limit": 1
}}

==================================================
MULTIPLE VALUES
==================================================

When a filter can contain multiple categorical
values, use a list.

Example:

{{
    "operation": "count",
    "filters": {{
        "status": [
            "Open",
            "Escalated"
        ]
    }}
}}

==================================================
UNRESOLVED TICKETS
==================================================

In this dataset:

Resolved = issue has been solved.

Open = issue is still being worked on.

Escalated = issue has not been resolved and
has been passed to a higher-level team/person.

Therefore:

UNRESOLVED means:

- Open
- OR Escalated

Use:

{{
    "status": [
        "Open",
        "Escalated"
    ]
}}

Do NOT interpret unresolved as only Open.

==================================================
NUMERIC CONDITIONS
==================================================

For numeric columns use:

{{
    "column": {{
        "operator": ">",
        "value": 12
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
TICKET AGE
==================================================

The system supports a special filter:

"age_hours"

age_hours means:

CURRENT TIME - created_at

It represents how many hours a ticket has existed.

Use age_hours when the user asks whether an
UNRESOLVED ticket has been unresolved for a
certain amount of time.

Example:

"unresolved for more than 12 hours"

means:

{{
    "age_hours": {{
        "operator": ">",
        "value": 12
    }}
}}

==================================================
IMPORTANT DISTINCTION
==================================================

Do NOT use:

"resolution_time_hrs"

for an unresolved ticket.

Why?

Because resolution_time_hrs represents the time
taken to actually resolve a ticket.

An unresolved ticket does not have a resolution
time yet.

Therefore:

"not resolved within 12 hours"

means:

1. The ticket is unresolved.
2. The ticket age is greater than 12 hours.

Use:

{{
    "status": [
        "Open",
        "Escalated"
    ],
    "age_hours": {{
        "operator": ">",
        "value": 12
    }}
}}

==================================================
ASSESSMENT QUERY
==================================================

Question:

"Show me all Critical tickets not resolved
within 12 hours."

Correct query plan:

{{
    "operation": "list",
    "columns": [
        "ticket_id",
        "created_at",
        "priority",
        "status",
        "response_time_hrs",
        "resolution_time_hrs",
        "agent_id",
        "issue_summary"
    ],
    "filters": {{
        "priority": "Critical",
        "status": [
            "Open",
            "Escalated"
        ],
        "age_hours": {{
            "operator": ">",
            "value": 12
        }}
    }}
}}

==================================================
TIME RANGE
==================================================

Supported time ranges:

- all
- today
- this_week
- this_month

"today" means:

"time_range": "today"

"this week" means:

"time_range": "this_week"

"this month" means:

"time_range": "this_month"

If no time period is mentioned:

"time_range": "all"

Python will calculate the actual date range.

==================================================
ANOMALY DETECTION
==================================================

If the user asks for:

- anomalies
- unusual tickets
- outliers
- unusually long resolution times
- abnormal resolution times

use:

{{
    "operation": "anomaly_detection",
    "anomaly_type": "resolution_time",
    "time_range": "this_week"
}}

Possible anomaly types:

- resolution_time
- critical_unresolved

==================================================
CRITICAL UNRESOLVED
==================================================

If the user asks:

"critical unresolved tickets"

you may use:

{{
    "operation": "anomaly_detection",
    "anomaly_type": "critical_unresolved",
    "time_range": "all"
}}

==================================================
LIMIT
==================================================

Use "limit": 1 when the user asks:

- most
- highest
- top
- which agent has the most

Example:

"Which agent resolved the most tickets?"

Use:

{{
    "operation": "group_count",
    "group_by": "agent_id",
    "filters": {{
        "status": "Resolved"
    }},
    "limit": 1
}}

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

15. "Which agent resolved the most"
    means group_count by agent_id,
    filtered to Resolved.

16. "Resolved the most this month"
    means:
    status = Resolved
    time_range = this_month
    group_by = agent_id
    limit = 1.

17. "Unresolved" means:
    Open OR Escalated.

18. "Critical unresolved" means:
    priority = Critical
    AND status = Open OR Escalated.

19. "Not resolved within X hours" means:
    unresolved
    AND age_hours > X.

20. Do NOT use resolution_time_hrs
    for unresolved tickets.

21. "Find anomalies" means:
    anomaly_detection.

22. Preserve requested time ranges.

23. Python performs all calculations.

24. Never return the actual answer.
    Return only the query plan.

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

        # Remove markdown code fences
        if response_text.startswith(
            "```json"
        ):
            response_text = response_text[7:]

        elif response_text.startswith(
            "```"
        ):
            response_text = response_text[3:]

        if response_text.endswith(
            "```"
        ):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:

            query_plan = json.loads(
                response_text
            )

        except json.JSONDecodeError as e:

            raise ValueError(
                "Gemini returned invalid JSON: "
                f"{response_text}"
            ) from e

        return query_plan


# =====================================================
# TEST GEMINI
# =====================================================

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

        "What is the average customer rating "
        "for Technical tickets?",

        "Find anomalies in resolution time "
        "this week.",

        "Which agent resolved the most tickets "
        "this month?",

        "Show me all Critical tickets not "
        "resolved within 12 hours."

    ]

    for question in questions:

        result = llm.generate_query_plan(
            question=question,
            columns=columns,
            unique_values=unique_values
        )

        print("\n" + "=" * 60)

        print("Question:")
        print(question)

        print("\nQuery Plan:")

        print(
            json.dumps(
                result,
                indent=4
            )
        )