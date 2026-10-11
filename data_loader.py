"""
data_loader.py
──────────────
Loads and preprocesses the SuperMarket Analysis CSV dataset.
Handles missing values, type coercions, and derived column creation.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Union

CSV_PATH = Path(__file__).parent / "SuperMarket Analysis.csv"


def load_data(path: Union[str, Path] = CSV_PATH) -> pd.DataFrame:
    """Load the CSV, clean it, and return a tidy DataFrame."""

    # ── 1. Load ───────────────────────────────────────────────────────────────
    df = pd.read_csv(path)

    # ── 2. Standardise column names (strip whitespace) ───────────────────────
    df.columns = df.columns.str.strip()

    # ── 3. Rename columns to consistent snake-ish readable names ─────────────
    rename_map = {
        "Invoice ID":             "Invoice ID",
        "Branch":                 "Branch",
        "City":                   "City",
        "Customer type":          "Customer Type",
        "Gender":                 "Gender",
        "Product line":           "Product Line",
        "Unit price":             "Unit Price",
        "Quantity":               "Quantity",
        "Tax 5%":                 "Tax (5%)",
        "Sales":                  "Sales (Raw)",   # original column – may be wrong
        "Date":                   "Date",
        "Time":                   "Time",
        "Payment":                "Payment",
        "cogs":                   "COGS",
        "gross margin percentage":"Gross Margin %",
        "gross income":           "Gross Income",
        "Rating":                 "Rating",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # ── 4. Missing / incorrect value handling ─────────────────────────────────
    #    Drop rows where core numeric columns are completely missing
    core_cols = ["Unit Price", "Quantity"]
    df.dropna(subset=core_cols, inplace=True)

    #    Coerce numerics (handles stray string values gracefully)
    for col in ["Unit Price", "Quantity", "Tax (5%)", "Sales (Raw)",
                "COGS", "Gross Margin %", "Gross Income", "Rating"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    #    Fill remaining numeric NaNs with column median (non-destructive)
    num_cols = df.select_dtypes(include="number").columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    #    Fill string NaNs with 'Unknown'
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].fillna("Unknown")

    # ── 5. Derived column: Sales = Quantity × Unit Price ─────────────────────
    df["Sales"] = (df["Quantity"] * df["Unit Price"]).round(2)

    # ── 6. Parse Date & Time ─────────────────────────────────────────────────
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.month_name()
    df["Month Num"] = df["Date"].dt.month
    df["Day of Week"] = df["Date"].dt.day_name()
    df["Hour"] = pd.to_datetime(df["Time"], format="%I:%M:%S %p", errors="coerce").dt.hour

    # ── 7. Drop helper columns no longer needed ───────────────────────────────
    df.drop(columns=["Sales (Raw)"], errors="ignore", inplace=True)

    df.reset_index(drop=True, inplace=True)
    return df


def summary_stats(df: pd.DataFrame) -> dict:
    """Return a flat dict of high-level KPIs."""
    return {
        "Total Transactions":   len(df),
        "Total Sales (USD)":    round(df["Sales"].sum(), 2),
        "Avg Sales per Txn":    round(df["Sales"].mean(), 2),
        "Total Quantity Sold":  int(df["Quantity"].sum()),
        "Avg Rating":           round(df["Rating"].mean(), 2),
        "Total Gross Income":   round(df["Gross Income"].sum(), 2),
        "Unique Customers":     df["Invoice ID"].nunique(),
        "Branches":             df["Branch"].nunique(),
    }


def branch_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Branch")
        .agg(
            Transactions=("Invoice ID", "count"),
            Total_Sales=("Sales", "sum"),
            Avg_Sales=("Sales", "mean"),
            Total_Quantity=("Quantity", "sum"),
            Avg_Rating=("Rating", "mean"),
            Gross_Income=("Gross Income", "sum"),
        )
        .round(2)
        .reset_index()
    )


def product_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Product Line")
        .agg(
            Transactions=("Invoice ID", "count"),
            Total_Sales=("Sales", "sum"),
            Avg_Sales=("Sales", "mean"),
            Total_Quantity=("Quantity", "sum"),
            Avg_Rating=("Rating", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
    )
