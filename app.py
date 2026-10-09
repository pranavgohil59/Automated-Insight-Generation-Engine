import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# Set up page
st.set_page_config(page_title="Healthcare Insight Engine", page_icon="🏥", layout="wide")

st.title("🏥 Healthcare Automated Insight Engine")
st.write("Automatically discovers trends, statistical outliers, and correlations from district performance data.")


# -------------------------------------------------------------
# 1. DATA LOADING & BASIC CHECKS
# -------------------------------------------------------------
def load_data(file_source):
    """Loads CSV and cleans up column names and date format."""
    df = pd.read_csv(file_source)

    # Required columns from assignment
    required_cols = [
        "month", "district", "anc_coverage",
        "institutional_delivery", "immunization", "high_risk_cases"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Missing required columns in CSV: {', '.join(missing)}")
        return None

    # Clean district names and format month as YYYY-MM
    df["district"] = df["district"].astype(str).str.strip()
    df["month"] = df["month"].astype(str).str.strip().str[:7]

    # Convert numeric columns
    numeric_cols = ["anc_coverage", "institutional_delivery", "immunization", "high_risk_cases"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove any duplicate district-month rows (keep first)
    df = df.drop_duplicates(subset=["district", "month"], keep="first")
    df = df.sort_values(by=["district", "month"]).reset_index(drop=True)

    return df


# -------------------------------------------------------------
# 2. TREND DETECTION (Month-over-Month % Change)
# -------------------------------------------------------------
def detect_trends(df, indicators, threshold):
    """Calculates month-over-month % change for each district and indicator."""
    trends = []

    # Group by each district to compare consecutive months
    for district, group in df.groupby("district"):
        group = group.sort_values("month").reset_index(drop=True)
        if len(group) < 2:
            continue

        for ind in indicators:
            for i in range(1, len(group)):
                prev_val = group.loc[i - 1, ind]
                curr_val = group.loc[i, ind]
                month = group.loc[i, "month"]
                prev_month = group.loc[i - 1, "month"]

                if pd.isna(prev_val) or pd.isna(curr_val) or prev_val == 0:
                    continue

                # Standard percentage change formula
                pct_change = ((curr_val - prev_val) / prev_val) * 100.0

                # Flag if change is greater than or equal to threshold
                if abs(pct_change) >= threshold:
                    trends.append({
                        "district": district,
                        "indicator": ind,
                        "period": month,
                        "prev_period": prev_month,
                        "value": curr_val,
                        "prev_value": prev_val,
                        "change_pct": round(pct_change, 1)
                    })

    return trends


# -------------------------------------------------------------
# 3. OUTLIER DETECTION (IQR Method)
# -------------------------------------------------------------
def detect_outliers(df, indicators, iqr_multiplier):
    """Finds unusual values using the Interquartile Range (IQR) rule."""
    outliers = []

    for ind in indicators:
        vals = df[ind].dropna()
        if len(vals) < 4:
            continue

        q1 = vals.quantile(0.25)
        q3 = vals.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - (iqr_multiplier * iqr)
        upper_bound = q3 + (iqr_multiplier * iqr)
        mean_val = vals.mean()

        for _, row in df.iterrows():
            val = row[ind]
            if pd.isna(val):
                continue

            if val < lower_bound or val > upper_bound:
                outliers.append({
                    "district": row["district"],
                    "indicator": ind,
                    "period": row["month"],
                    "value": val,
                    "mean": round(mean_val, 1),
                    "lower_bound": round(lower_bound, 1),
                    "upper_bound": round(upper_bound, 1)
                })

    return outliers


# -------------------------------------------------------------
# 4. CORRELATION ANALYSIS (Pearson Correlation)
# -------------------------------------------------------------
def detect_correlations(df, indicators, threshold):
    """Calculates Pearson correlation between numeric indicators."""
    valid_cols = [c for c in indicators if c in df.columns]
    if len(valid_cols) < 2:
        return [], pd.DataFrame()

    corr_matrix = df[valid_cols].corr(method="pearson").round(2)
    flagged = []

    # Get unique pairs (ignore self-correlation and duplicates)
    cols = list(corr_matrix.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            col1 = cols[i]
            col2 = cols[j]
            r = corr_matrix.loc[col1, col2]

            if abs(r) >= threshold:
                flagged.append({
                    "indicator_1": col1,
                    "indicator_2": col2,
                    "r_value": r
                })

    return flagged, corr_matrix


# -------------------------------------------------------------
# 5. AUTOMATED INSIGHT GENERATION
# -------------------------------------------------------------
def generate_insights(trends, outliers, correlations, trend_thresh):
    """Combines trends, outliers, and correlations into human-readable insights."""
    records = []

    # 1. Trend Insights
    for t in trends:
        val = t["value"]
        prev = t["prev_value"]
        pct = t["change_pct"]
        ind_name = t["indicator"].replace("_", " ").title()

        # Severity based on change magnitude
        severity = "High" if abs(pct) >= (trend_thresh * 1.8) else ("Medium" if abs(pct) >= (trend_thresh * 1.3) else "Low")
        direction = "dropped" if pct < 0 else "increased"

        explanation = (
            f"{ind_name} in {t['district']} {direction} by {abs(pct)}% "
            f"(from {prev} to {val}) compared to {t['prev_period']}."
        )

        records.append({
            "type": "trend",
            "indicator": t["indicator"],
            "entity": t["district"],
            "period": t["period"],
            "value": val,
            "prev_value": prev,
            "change_pct": pct,
            "severity": severity,
            "explanation": explanation
        })

    # 2. Outlier Insights
    for o in outliers:
        val = o["value"]
        ind_name = o["indicator"].replace("_", " ").title()
        bound_type = "lower bound" if val < o["lower_bound"] else "upper bound"

        explanation = (
            f"{o['district']}'s {ind_name} of {val} in {o['period']} is an outlier "
            f"crossing the {bound_type} (state average was {o['mean']})."
        )

        records.append({
            "type": "outlier",
            "indicator": o["indicator"],
            "entity": o["district"],
            "period": o["period"],
            "value": val,
            "prev_value": o["mean"],
            "change_pct": round(((val - o["mean"]) / o["mean"]) * 100, 1),
            "severity": "High",
            "explanation": explanation
        })

    # 3. Correlation Insights
    for c in correlations:
        name1 = c["indicator_1"].replace("_", " ").title()
        name2 = c["indicator_2"].replace("_", " ").title()
        r = c["r_value"]
        direction = "positive" if r > 0 else "negative"

        explanation = (
            f"Strong {direction} correlation (r = {r}) detected between "
            f"{name1} and {name2} across districts."
        )

        records.append({
            "type": "correlation",
            "indicator": f"{c['indicator_1']}: {c['indicator_2']}",
            "entity": "Statewide",
            "period": "All periods",
            "value": r,
            "prev_value": None,
            "change_pct": None,
            "severity": "High" if abs(r) >= 0.85 else "Medium",
            "explanation": explanation
        })

    if not records:
        return pd.DataFrame()

    insights_df = pd.DataFrame(records)

    # Sort High -> Medium -> Low
    sev_map = {"High": 1, "Medium": 2, "Low": 3}
    insights_df["sev_rank"] = insights_df["severity"].map(sev_map)
    insights_df = insights_df.sort_values(by=["sev_rank", "type"]).reset_index(drop=True)
    insights_df = insights_df.drop(columns=["sev_rank"])

    # Auto-number IDs: INS-0001, INS-0002...
    insights_df.insert(0, "insight_id", [f"INS-{i+1:04d}" for i in range(len(insights_df))])

    return insights_df


# -------------------------------------------------------------
# 6. STREAMLIT USER INTERFACE & CONTROLS
# -------------------------------------------------------------
# Sidebar: Data Source
st.sidebar.header("📁 Data Source")
use_sample = st.sidebar.checkbox("Use Company Dataset", value=True)

df = None
if use_sample:
    default_path = os.path.join(os.path.dirname(__file__), "data", "healthcare_data.csv")
    if os.path.exists(default_path):
        df = load_data(default_path)
    else:
        st.error("Default healthcare_data.csv not found in data/ folder.")
else:
    uploaded = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
    if uploaded is not None:
        df = load_data(uploaded)

if df is None:
    st.info("👈 Please select 'Use Company Dataset' or upload a CSV file from the sidebar.")
    st.stop()

# Sidebar: Filters
st.sidebar.header("🔍 Filters")
districts = sorted(df["district"].unique().tolist())
selected_districts = st.sidebar.multiselect("Select Districts:", districts, default=districts)

months = sorted(df["month"].unique().tolist())
selected_months = st.sidebar.multiselect("Select Months:", months, default=months)

all_indicators = ["anc_coverage", "institutional_delivery", "immunization", "high_risk_cases"]
selected_indicators = st.sidebar.multiselect("Select Indicators:", all_indicators, default=all_indicators)

# Sidebar: Sliders for Thresholds
st.sidebar.header("⚙️ Thresholds")
trend_thresh = st.sidebar.slider("Significant Trend Threshold (±%)", min_value=5.0, max_value=30.0, value=10.0, step=1.0)
iqr_factor = st.sidebar.slider("Outlier IQR Multiplier", min_value=1.0, max_value=2.5, value=1.5, step=0.1)
corr_thresh = st.sidebar.slider("Correlation Flag (|r|)", min_value=0.50, max_value=0.95, value=0.70, step=0.05)

# Apply filters
filtered_df = df[df["district"].isin(selected_districts) & df["month"].isin(selected_months)]
if filtered_df.empty:
    st.warning("No data found for the selected filters. Please adjust filters.")
    st.stop()

# Run calculations
trends = detect_trends(filtered_df, selected_indicators, trend_thresh)
outliers = detect_outliers(filtered_df, selected_indicators, iqr_factor)
flagged_corrs, corr_matrix = detect_correlations(filtered_df, selected_indicators, corr_thresh)
insights_df = generate_insights(trends, outliers, flagged_corrs, trend_thresh)

# Top Metrics Bar
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Insights", len(insights_df))
col2.metric("Trends Flagged", len(trends))
col3.metric("Outliers Detected", len(outliers))
col4.metric("Strong Correlations", len(flagged_corrs))

st.markdown("---")

# Main Content Tabs
tab1, tab2, tab3 = st.tabs(["💡 Automated Insights", "📊 Charts & Visualizations", "📋 Raw Dataset"])

# TAB 1: Insights Table & Downloads
with tab1:
    st.subheader("Auto-Generated Healthcare Insights")
    st.write("Plain-English summaries derived directly from computed statistical signals:")

    if insights_df.empty:
        st.info("No insights flagged with current threshold settings.")
    else:
        st.dataframe(insights_df, width="stretch", hide_index=True)

        # Download Buttons
        st.write("### Export Insights")
        dcol1, dcol2, dcol3 = st.columns(3)
        with dcol1:
            csv_data = insights_df.to_csv(index=False)
            st.download_button("📥 Download Insights CSV", csv_data, "insights.csv", "text/csv")
        with dcol2:
            clean_json_df = insights_df.replace({np.nan: None})
            json_data = json.dumps(clean_json_df.to_dict(orient="records"), indent=2)
            st.download_button("📥 Download Insights JSON", json_data, "insights.json", "application/json")
        with dcol3:
            if not corr_matrix.empty:
                st.download_button("📥 Download Correlation Matrix CSV", corr_matrix.to_csv(), "correlations.csv", "text/csv")

# TAB 2: Visualizations
with tab2:
    st.subheader("Visual Analytics")
    c1, c2 = st.columns(2)

    with c1:
        st.write("#### 1. Severity Distribution")
        if not insights_df.empty:
            sev_counts = insights_df["severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "Count"]
            fig_bar = px.bar(
                sev_counts, x="Severity", y="Count", color="Severity",
                color_discrete_map={"High": "#e11d48", "Medium": "#f59e0b", "Low": "#3b82f6"}
            )
            st.plotly_chart(fig_bar, width="stretch")
        else:
            st.write("No insights to display.")

    with c2:
        st.write("#### 2. Pearson Correlation Heatmap")
        if not corr_matrix.empty:
            fig_heat = px.imshow(
                corr_matrix, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1
            )
            st.plotly_chart(fig_heat, width="stretch")
            st.caption("⚠️ Note: Small dataset (12 records). Correlations show linear association, not causation.")

    st.write("#### 3. District Trend Over Time")
    chart_col = st.selectbox("Select Indicator to Plot:", selected_indicators)
    fig_line = px.line(
        filtered_df, x="month", y=chart_col, color="district", markers=True,
        title=f"{chart_col.replace('_', ' ').title()} across Districts"
    )
    st.plotly_chart(fig_line, width="stretch")

# TAB 3: Raw Data & Health Checks
with tab3:
    st.subheader("Dataset Preview")
    st.dataframe(filtered_df, width="stretch", hide_index=True)

    st.write("#### Missing Values Count")
    missing_counts = filtered_df.isna().sum().reset_index()
    missing_counts.columns = ["Column", "Missing Count"]
    st.dataframe(missing_counts, hide_index=True)
