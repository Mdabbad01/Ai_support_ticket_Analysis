from pathlib import Path

import pandas as pd

from fastapi import (
    FastAPI,
    HTTPException,
    Request
)

from fastapi.responses import HTMLResponse

from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

from app.llm_service import LLMService

from app.query_engine import QueryEngine

from app.anomaly_detector import AnomalyDetector


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "support_tickets.csv"
)

TEMPLATE_DIR = (
    BASE_DIR
    / "app"
    / "templates"
)

STATIC_DIR = (
    BASE_DIR
    / "app"
    / "static"
)


# --------------------------------------------------
# CHECK DATASET
# --------------------------------------------------

if not DATA_PATH.exists():

    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}"
    )


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)


# --------------------------------------------------
# CONVERT DATE
# --------------------------------------------------

if "created_at" in df.columns:

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )


# --------------------------------------------------
# DATASET INFORMATION
# --------------------------------------------------

columns = df.columns.tolist()

unique_values = {}


for column in df.columns:

    if pd.api.types.is_object_dtype(
        df[column]
    ):

        values = (
            df[column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if len(values) <= 50:

            unique_values[column] = values


# --------------------------------------------------
# INITIALIZE SERVICES
# --------------------------------------------------

llm_service = LLMService()

query_engine = QueryEngine(df)

anomaly_detector = AnomalyDetector(df)


# --------------------------------------------------
# FASTAPI
# --------------------------------------------------

app = FastAPI(
    title="AI Support Ticket Analyzer",
    description="AI-powered support ticket analysis system",
    version="1.0.0"
)


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static"
)


# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------

templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class QueryRequest(BaseModel):

    question: str


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "dataset_rows": len(df),
        "dataset_columns": columns
    }


# --------------------------------------------------
# DATASET
# --------------------------------------------------

@app.get("/dataset")
async def dataset_info():

    return {
        "rows": len(df),
        "columns": columns,
        "categorical_values": unique_values
    }


# --------------------------------------------------
# MAIN AI QUERY
# --------------------------------------------------

@app.post("/query")
async def query(request: QueryRequest):

    try:

        question = request.question.strip()

        if not question:

            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )


        # ------------------------------------------
        # STEP 1
        # Gemini generates query plan
        # ------------------------------------------

        query_plan = (
            llm_service.generate_query_plan(
                question=question,
                columns=columns,
                unique_values=unique_values
            )
        )


        # ------------------------------------------
        # STEP 2
        # Check operation
        # ------------------------------------------

        operation = query_plan.get(
            "operation"
        )


        # ------------------------------------------
        # ANOMALY DETECTION
        # ------------------------------------------

        if operation == "anomaly_detection":

            anomaly_type = query_plan.get(
                "anomaly_type"
            )

            time_range = query_plan.get(
                "time_range",
                "all"
            )

            anomalies = (
                anomaly_detector.detect(
                    anomaly_type=anomaly_type,
                    time_range=time_range
                )
            )

            result = {
                "count": len(anomalies),
                "anomalies": anomalies
            }


        # ------------------------------------------
        # NORMAL QUERY
        # ------------------------------------------

        else:

            result = query_engine.execute(
                query_plan
            )


        # ------------------------------------------
        # RETURN RESULT
        # ------------------------------------------

        return {
            "question": question,
            "query_plan": query_plan,
            "result": result
        }


    except HTTPException:

        raise


    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# CRITICAL UNRESOLVED
# --------------------------------------------------

@app.get(
    "/anomalies/critical-unresolved"
)
async def critical_unresolved():

    try:

        anomalies = (
            anomaly_detector
            .detect_critical_unresolved()
        )

        return {
            "count": len(anomalies),
            "anomalies": anomalies
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# RESOLUTION TIME ANOMALIES
# --------------------------------------------------

@app.get(
    "/anomalies/resolution-time"
)
async def resolution_time_anomalies():

    try:

        anomalies = (
            anomaly_detector
            .detect_resolution_time_anomalies()
        )

        return {
            "count": len(anomalies),
            "anomalies": anomalies
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# ALL ANOMALIES
# --------------------------------------------------

@app.get("/anomalies")
async def all_anomalies():

    try:

        return anomaly_detector.detect_all()


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )