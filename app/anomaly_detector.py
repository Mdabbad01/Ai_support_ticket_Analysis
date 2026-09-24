import math

import pandas as pd


class AnomalyDetector:

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

        # =====================================================
        # PREPARE DATA
        # =====================================================

        if "created_at" in self.df.columns:
            self.df["created_at"] = pd.to_datetime(
                self.df["created_at"],
                errors="coerce"
            )

        if "resolution_time_hrs" in self.df.columns:
            self.df["resolution_time_hrs"] = pd.to_numeric(
                self.df["resolution_time_hrs"],
                errors="coerce"
            )

    # =====================================================
    # JSON SAFE CONVERSION
    # =====================================================

    def make_json_safe(self, records):
        """
        Convert Pandas/NumPy values into JSON-safe Python values.

        NaN and infinite values are converted to None.
        """

        safe_records = []

        for record in records:

            safe_record = {}

            for key, value in record.items():

                # Handle missing values
                if pd.isna(value):
                    safe_record[key] = None
                    continue

                # Handle timestamps
                if isinstance(
                    value,
                    (
                        pd.Timestamp,
                        pd.DatetimeIndex
                    )
                ):
                    safe_record[key] = str(value)
                    continue

                # Handle floating-point values
                if isinstance(value, float):

                    if not math.isfinite(value):
                        safe_record[key] = None
                    else:
                        safe_record[key] = value

                    continue

                # Handle NumPy numeric values
                if hasattr(value, "item"):

                    try:
                        value = value.item()
                    except (ValueError, TypeError):
                        pass

                safe_record[key] = value

            safe_records.append(
                safe_record
            )

        return safe_records

    # =====================================================
    # APPLY TIME RANGE
    # =====================================================

    def apply_time_range(
        self,
        data: pd.DataFrame,
        time_range: str
    ) -> pd.DataFrame:

        if not time_range or time_range == "all":
            return data

        if "created_at" not in data.columns:
            raise ValueError(
                "created_at column is required "
                "for time filtering"
            )

        valid_dates = data[
            "created_at"
        ].dropna()

        if valid_dates.empty:
            return data.iloc[0:0]

        # Use the latest dataset date as reference
        now = valid_dates.max()

        # =================================================
        # TODAY
        # =================================================

        if time_range == "today":

            start = now.normalize()

            return data[
                data["created_at"] >= start
            ]

        # =================================================
        # THIS WEEK
        # =================================================

        elif time_range == "this_week":

            start = (
                now.normalize()
                - pd.Timedelta(
                    days=now.weekday()
                )
            )

            return data[
                data["created_at"] >= start
            ]

        # =================================================
        # THIS MONTH
        # =================================================

        elif time_range == "this_month":

            start = pd.Timestamp(
                year=now.year,
                month=now.month,
                day=1
            )

            return data[
                data["created_at"] >= start
            ]

        else:

            raise ValueError(
                f"Unsupported time range: "
                f"{time_range}"
            )

    # =====================================================
    # RESOLUTION TIME ANOMALIES
    # =====================================================

    def detect_resolution_time_anomalies(
        self,
        time_range="all"
    ):

        data = self.apply_time_range(
            self.df,
            time_range
        ).copy()

        # Only resolved tickets with a resolution time
        data = data.dropna(
            subset=[
                "resolution_time_hrs"
            ]
        )

        if data.empty:
            return []

        # =================================================
        # IQR METHOD
        # =================================================

        q1 = data[
            "resolution_time_hrs"
        ].quantile(0.25)

        q3 = data[
            "resolution_time_hrs"
        ].quantile(0.75)

        iqr = q3 - q1

        upper_limit = q3 + (
            1.5 * iqr
        )

        anomalies = data[
            data[
                "resolution_time_hrs"
            ] > upper_limit
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

        records = (
            anomalies[columns]
            .to_dict(
                orient="records"
            )
        )

        return self.make_json_safe(
            records
        )

    # =====================================================
    # CRITICAL UNRESOLVED
    # =====================================================

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

        anomalies = data[
            condition
        ].copy()

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

        records = (
            anomalies[columns]
            .to_dict(
                orient="records"
            )
        )

        return self.make_json_safe(
            records
        )

    # =====================================================
    # GENERIC DETECTOR
    # =====================================================

    def detect(
        self,
        anomaly_type: str,
        time_range: str = "all"
    ):

        if anomaly_type == "resolution_time":

            return (
                self.detect_resolution_time_anomalies(
                    time_range
                )
            )

        elif anomaly_type == "critical_unresolved":

            return (
                self.detect_critical_unresolved(
                    time_range
                )
            )

        else:

            raise ValueError(
                f"Unsupported anomaly type: "
                f"{anomaly_type}"
            )

    # =====================================================
    # ALL ANOMALIES
    # =====================================================

    def detect_all(self):

        return {
            "critical_unresolved":
                self.detect_critical_unresolved(),

            "resolution_time_anomalies":
                self.detect_resolution_time_anomalies()
        }