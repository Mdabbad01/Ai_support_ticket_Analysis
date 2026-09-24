# AI Support Ticket Analyzer

An AI-powered support ticket analytics system that allows users to analyze customer support tickets using natural-language questions.

The system uses **Google Gemini** to convert natural-language questions into structured JSON query plans. The actual data analysis is performed deterministically using **Python and Pandas**.

The application provides a **FastAPI REST API** and a simple web interface for interacting with the system.

---

## Features

- Natural-language support ticket queries
- Google Gemini LLM integration
- Structured JSON query planning
- Deterministic Pandas-based query execution
- Ticket filtering
- Ticket counting
- Average, sum, minimum and maximum calculations
- Group-wise ticket analysis
- Time-range filtering
- Unresolved ticket detection
- Critical ticket detection
- Resolution-time anomaly detection
- Ticket age calculation
- REST API
- FastAPI Swagger documentation
- Simple web UI
- JSON-safe API responses
- Unit tests with Pytest

---

# Architecture

The system follows a separation-of-concerns architecture where the LLM understands the user's intent, while Python performs the actual data processing.

```text
                         ┌──────────────────────┐
                         │       User           │
                         │  Natural Language    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Web UI           │
                         │   HTML/CSS/JavaScript │
                         └──────────┬───────────┘
                                    │
                                    │ POST /query
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │      REST API        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     LLM Service      │
                         │   Google Gemini      │
                         └──────────┬───────────┘
                                    │
                                    │ Structured JSON
                                    ▼
                 ┌─────────────────────────────────────┐
                 │          Query Plan                  │
                 │                                     │
                 │ operation                           │
                 │ filters                             │
                 │ column                              │
                 │ group_by                            │
                 │ time_range                          │
                 │ limit                               │
                 └─────────────────┬───────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │   Query Engine   │          │ Anomaly Detector │
          │     Pandas       │          │      Pandas      │
          └────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  support_tickets │
                         │       .csv       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Deterministic    │
                         │ Analysis Result  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │       UI / API   │
                         │      Response    │
                         └──────────────────┘