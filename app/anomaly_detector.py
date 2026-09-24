import pandas as pd


class AnomalyDetector:

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

        self.df["created_at"] = pd.to_datetime(
            self.df["created_at"],
            errors="coerce"
        )

        self.df["resolution_time_hrs"] = pd.to_numeric(
            self.df["resolution_time_hrs"],
            errors="coerce"
        )

    # --------------------------------------------------
    # TIME RANGE FILTER
    # --------------------------------------------------

    def apply_time_range(
        self,
        data: pd.DataFrame,
        time_range: str
    ) -> pd.DataFrame:

        if time_range == "all":
            return data

        now = pd.Timestamp.now()

        if time_range == "today":

            start = now.normalize()

            return data[
                data["created_at"] >= start
            ]

        elif time_range == "this_week":

            start = (
                now.normalize()
                - pd.Timedelta(days=now.weekday())
            )

            return data[
                data["created_at"] >= start
            ]

        elif time_range == "this_month":

            start = pd.Timestamp(
                year=now.year,
                month=now.month,
                day=1
            )

            return data[
                data["created_at"] >= start
            ]

        return data

    # --------------------------------------------------
    # RESOLUTION TIME ANOMALIES
    # --------------------------------------------------

    def detect_resolution_time_anomalies(
        self,
        time_range="all"
    ):

        data = self.apply_time_range(
            self.df,
            time_range
        ).copy()

        data = data.dropna(
            subset=["resolution_time_hrs"]
        )

        if data.empty:

            return []

        q1 = data["resolution_time_hrs"].quantile(
            0.25
        )

        q3 = data["resolution_time_hrs"].quantile(
            0.75
        )

        iqr = q3 - q1

        upper_limit = q3 + (1.5 * iqr)

        anomalies = data[
            data["resolution_time_hrs"] > upper_limit
        ].copy()

        columns = [
            "ticket_id",
            "created_at",
            "category",
            "priority",
            "status",
            "resolution_time_hrs",
            "agent_id",
            "customer_rating",
            "issue_summary"
        ]

        return (
            anomalies[columns]
            .where(
                pd.notna(anomalies[columns]),
                None
            )
            .to_dict(
                orient="records"
            )
        )

    # --------------------------------------------------
    # CRITICAL UNRESOLVED
    # --------------------------------------------------

    def detect_critical_unresolved(
        self,
        time_range="all"
    ):

        data = self.apply_time_range(
            self.df,
            time_range
        ).copy()

        condition = (
            (
                data["priority"]
                .astype(str)
                .str.lower()
                == "critical"
            )
            &
            (
                data["status"]
                .astype(str)
                .str.lower()
                != "resolved"
            )
        )

        anomalies = data[condition].copy()

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

        return (
            anomalies[columns]
            .where(
                pd.notna(anomalies[columns]),
                None
            )
            .to_dict(
                orient="records"
            )
        )

    # --------------------------------------------------
    # GENERAL ANOMALY DETECTION
    # --------------------------------------------------

    def detect(
        self,
        anomaly_type: str,
        time_range: str = "all"
    ):

        if anomaly_type == "resolution_time":

            return self.detect_resolution_time_anomalies(
                time_range
            )

        elif anomaly_type == "critical_unresolved":

            return self.detect_critical_unresolved(
                time_range
            )

        else:

            raise ValueError(
                f"Unsupported anomaly type: {anomaly_type}"
            )

    # --------------------------------------------------
    # ALL ANOMALIES
    # --------------------------------------------------

    def detect_all(self):

        return {
            "critical_unresolved":
                self.detect_critical_unresolved(),

            "resolution_time_anomalies":
                self.detect_resolution_time_anomalies()
        }