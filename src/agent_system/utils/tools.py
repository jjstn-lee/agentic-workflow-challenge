from langchain.tools import tool
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union

# ----------------------------
# ----------------------------

@tool
def calculate_roi(data: List[Dict], campaign_id: int) -> List[Dict]:
    """
    Calculate ROI for a specific campaign from JSON-serializable input.
    
    Args:
        data: List of dicts representing campaign data (JSON-friendly).
        campaign_id: ID of the campaign to calculate ROI for.
    
    Returns:
        List of dicts containing campaign_id, brand_area, and roi.
    """
    df = pd.DataFrame(data)
    
    campaign_df = df[df["campaign_id"] == campaign_id].copy()
    
    if campaign_df.empty:
        return []

    campaign_df["roi"] = ((campaign_df["revenue"] - campaign_df["spend"]) / campaign_df["spend"]).astype(float)
    campaign_df["roi"] = campaign_df["roi"].round(2)

    return campaign_df[["campaign_id", "brand_area", "roi"]].to_dict(orient="records")


@tool
def calculate_ctr(data: List[Dict]) -> List[Dict]:
    """
    Calculate Click-Through Rate (CTR).
    CTR = clicks / impressions
    
    Args:
        data: List of dicts representing campaign data (JSON-friendly).
    
    Returns:
        List of dicts with added CTR column.
    """
    df = pd.DataFrame(data)
    df = df.copy()
    df["ctr"] = df["clicks"] / df["impressions"]
    return df.to_dict(orient="records")


@tool
def calculate_conversion_rate(data: List[Dict]) -> List[Dict]:
    """
    Calculate Conversion Rate (CR).
    CR = conversions / clicks
    
    Args:
        data: List of dicts representing campaign data (JSON-friendly).
    
    Returns:
        List of dicts with added conversion_rate column.
    """
    df = pd.DataFrame(data)
    df = df.copy()
    df["conversion_rate"] = df["conversions"] / df["clicks"]
    return df.to_dict(orient="records")

# ----------------------------
# ----------------------------

@tool
def filter_data(data: List[Dict], brand_area: Optional[Union[str, List[str]]] = None, 
                quarter: Optional[Union[str, List[str]]] = None, 
                tactic: Optional[Union[str, List[str]]] = None) -> List[Dict]:
    """
    Filter campaigns based on brand area, quarter, and/or tactic.
    Any of the parameters can be None (meaning "no filter").
    
    Args:
        data: List of dicts representing campaign data (JSON-friendly).
        brand_area: Brand area(s) to filter by.
        quarter: Quarter(s) to filter by.
        tactic: Tactic(s) to filter by.
    
    Returns:
        List of dicts containing filtered data.
    """
    df = pd.DataFrame(data)
    filtered = df.copy()
    
    if brand_area:
        brand_areas = brand_area if isinstance(brand_area, list) else [brand_area]
        filtered = filtered[filtered["brand_area"].isin(brand_areas)]
    if quarter:
        quarters = quarter if isinstance(quarter, list) else [quarter]
        filtered = filtered[filtered["quarter"].isin(quarters)]
    if tactic:
        tactics = tactic if isinstance(tactic, list) else [tactic]
        filtered = filtered[filtered["tactic"].isin(tactics)]
    
    return filtered.to_dict(orient="records")


@tool
def summarize_performance(data: List[Dict], group_by: List[str] = None) -> List[Dict]:
    """
    Summarize key metrics by grouping fields.
    Returns mean, median, and standard deviation for ROI, CTR, and conversion rate.
    
    Args:
        data: List of dicts representing campaign data (JSON-friendly).
        group_by: List of fields to group by. Defaults to ["brand_area", "tactic", "quarter"].
    
    Returns:
        List of dicts containing summary statistics.
    """
    if group_by is None:
        group_by = ["brand_area", "tactic", "quarter"]
    
    df = pd.DataFrame(data)
    
    required_cols = ["roi", "ctr", "conversion_rate", "conversions", "revenue", "spend"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        for col in missing_cols:
            if col in ["roi", "ctr", "conversion_rate"]:
                df[col] = 0.0
            else:
                df[col] = 0
    
    summary = (
        df.groupby(group_by)
        .agg({
            "roi": ["mean", "std", "median"],
            "ctr": ["mean", "std", "median"],
            "conversion_rate": ["mean", "std", "median"],
            "conversions": "sum",
            "revenue": "sum",
            "spend": "sum"
        })
        .reset_index()
    )
    summary.columns = ["_".join(col).rstrip("_") for col in summary.columns.values]
    return summary.to_dict(orient="records")


# ----------------------------
# ----------------------------

@tool
def compare_tactic_performance(data: List[Dict], brand_areas: List[str], quarter: str) -> List[Dict]:
    """
    Compare tactic performance (ROI, CTR, Conversion Rate) between multiple brand areas
    for a specific quarter.
    
    Args:
        data: List of dicts representing campaign data (JSON-friendly).
        brand_areas: List of brand areas to compare.
        quarter: Quarter to analyze.
    
    Returns:
        List of dicts containing comparison results.
    """
    filtered_data = filter_data(data, brand_area=brand_areas, quarter=quarter)
    summary = summarize_performance(filtered_data, group_by=["brand_area", "tactic"])
    
    df = pd.DataFrame(summary)
    if not df.empty:
        df = df.sort_values(by=["tactic", "brand_area"]).reset_index(drop=True)
        return df.to_dict(orient="records")
    return []


@tool
def calculate_metric_by_tactic(data: List[Dict], brand_area: str, quarter: str, metric: str = "roi") -> List[Dict]:
    """
    Calculate the specified metric (ROI, CTR, etc.) by tactic for a given brand area and quarter.
    
    Args:
        data: List of dicts representing campaign data (JSON-friendly).
        brand_area: Brand area to analyze.
        quarter: Quarter to analyze.
        metric: Metric to calculate (default: "roi").
    
    Returns:
        List of dicts containing metric calculations by tactic.
    """
    filtered_data = filter_data(data, brand_area=brand_area, quarter=quarter)
    df = pd.DataFrame(filtered_data)
    
    if df.empty or metric not in df.columns:
        return []
    
    result = (
        df.groupby("tactic")[metric]
        .agg(["mean", "std", "median"])
        .reset_index()
        .sort_values("mean", ascending=False)
    )
    return result.to_dict(orient="records")


@tool
def calculate_roi_stability(data: List[Dict], brand_area: str, start_quarter: str, end_quarter: str) -> List[Dict]:
    """
    Measure ROI stability (standard deviation and coefficient of variation)
    across quarters for each tactic.
    
    Args:
        data: List of dicts representing campaign data (JSON-friendly).
        brand_area: Brand area to analyze.
        start_quarter: Starting quarter.
        end_quarter: Ending quarter.
    
    Returns:
        List of dicts containing stability metrics.
    """
    quarters = [start_quarter, end_quarter]
    filtered_data = filter_data(data, brand_area=brand_area, quarter=quarters)
    df = pd.DataFrame(filtered_data)
    
    if df.empty or "roi" not in df.columns:
        return []
    
    stability = (
        df.groupby("tactic")["roi"]
        .agg(["mean", "std"])
        .reset_index()
    )
    stability["cv"] = stability["std"] / np.abs(stability["mean"])
    stability = stability.sort_values("cv", ascending=True)
    return stability.to_dict(orient="records")


@tool
def get_top_stable_tactics(data: List[Dict], brand_area: str, start_quarter: str, end_quarter: str, top_n: int = 2) -> List[Dict]:
    """
    Return the top N tactics with the most stable ROI (lowest coefficient of variation).
    
    Args:
        data: List of dicts representing campaign data (JSON-friendly).
        brand_area: Brand area to analyze.
        start_quarter: Starting quarter.
        end_quarter: Ending quarter.
        top_n: Number of top tactics to return (default: 2).
    
    Returns:
        List of dicts containing top stable tactics.
    """
    stability_data = calculate_roi_stability(data, brand_area, start_quarter, end_quarter)
    df = pd.DataFrame(stability_data)
    
    if df.empty:
        return []
    
    return df.head(top_n).to_dict(orient="records")

# list of tools to assist in analysis (Analysis Agent)
analysis_tools = [
    calculate_roi, 
    calculate_ctr, 
    calculate_conversion_rate, 
    filter_data, 
    summarize_performance, 
    compare_tactic_performance, 
    calculate_metric_by_tactic, 
    calculate_roi_stability, 
    get_top_stable_tactics
]