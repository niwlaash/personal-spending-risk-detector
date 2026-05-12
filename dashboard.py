"""
Streamlit Dashboard for Personal Spending Risk & Burnout Detector.
Run with: streamlit run dashboard.py
"""

import os
import sys
import tempfile

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.pipeline import Pipeline

# --- Page Config ---
st.set_page_config(
    page_title="Spending Risk & Burnout Detector",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown(
    """
<style>
    .main > div { padding-top: 1rem; }
    .metric-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        border-radius: 16px; padding: 1.5rem; margin: 0.5rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .risk-low { color: #00e676; }
    .risk-medium { color: #ffab00; }
    .risk-high { color: #ff6d00; }
    .risk-critical { color: #ff1744; }
    .insight-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px; padding: 1rem; margin: 0.5rem 0;
        border-left: 4px solid #7c4dff;
    }
    div[data-testid="stMetricValue"] { font-size: 2rem; }
</style>
""",
    unsafe_allow_html=True,
)


def get_risk_color(level: str) -> str:
    colors = {
        "Low": "#00e676",
        "Medium": "#ffab00",
        "High": "#ff6d00",
        "Critical": "#ff1744",
    }
    return colors.get(level, "#ffffff")


def render_gauge(score, title, level):
    color = get_risk_color(level)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": title, "font": {"size": 18}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 30], "color": "rgba(0,230,118,0.15)"},
                    {"range": [30, 60], "color": "rgba(255,171,0,0.15)"},
                    {"range": [60, 80], "color": "rgba(255,109,0,0.15)"},
                    {"range": [80, 100], "color": "rgba(255,23,68,0.15)"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.8,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
    )
    return fig


def main():
    # --- Sidebar ---
    with st.sidebar:
        st.title("💰 Spending Risk Detector")
        st.markdown("---")
        st.subheader("📁 Upload Statement")
        uploaded_file = st.file_uploader(
            "Upload your bank statement (CSV or PDF)",
            type=["csv", "pdf"],
            help="Supports Malaysian bank CSV exports and PDF statements.",
        )
        st.markdown("---")
        st.subheader("ℹ️ About")
        st.markdown("""
        This tool analyzes your bank statements to detect:
        - **Financial risk** patterns
        - **Burnout** spending behavior
        - **Malaysia-specific** merchant insights

        Your data is processed locally and never stored permanently.
        """)
        use_sample = st.checkbox("📊 Use sample data", value=not uploaded_file)

    # --- Main Content ---
    st.title("Personal Spending Risk & Burnout Detector")
    st.caption(
        "Analyze your spending behavior for financial health and burnout signals"
    )

    pipeline = Pipeline()
    result = None

    if uploaded_file:
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name
        try:
            with st.spinner("🔍 Analyzing your statement..."):
                result = pipeline.run(tmp_path, file_type=ext)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
        finally:
            os.unlink(tmp_path)
    elif use_sample:
        sample_path = os.path.join(
            os.path.dirname(__file__), "data", "sample_statement.csv"
        )
        if os.path.exists(sample_path):
            with st.spinner("🔍 Analyzing sample data..."):
                result = pipeline.run(sample_path, file_type="csv")
        else:
            st.warning("Sample data not found. Please upload a file.")

    if not result:
        st.info("👆 Upload a bank statement or use sample data to get started.")
        return

    rs = result["risk_scores"]
    features = result["features"]
    insights = result["insights"]
    txns = pd.DataFrame(result["transactions"])

    # --- Risk Score Gauges ---
    st.markdown("## 📊 Risk Assessment")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            render_gauge(
                rs["financial_risk_score"], "Financial Risk", rs["financial_risk_level"]
            ),
            use_container_width=True,
        )
        st.markdown(
            f"**Level:** <span class='risk-{rs['financial_risk_level'].lower()}'>{rs['financial_risk_level']}</span>",
            unsafe_allow_html=True,
        )
    with col2:
        st.plotly_chart(
            render_gauge(
                rs["burnout_risk_score"], "Burnout Risk", rs["burnout_risk_level"]
            ),
            use_container_width=True,
        )
        st.markdown(
            f"**Level:** <span class='risk-{rs['burnout_risk_level'].lower()}'>{rs['burnout_risk_level']}</span>",
            unsafe_allow_html=True,
        )

    # --- Key Metrics ---
    st.markdown("## 📈 Key Metrics")
    summary = features.get("spending_summary", {})
    ie = features.get("income_vs_expense", {})
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💵 Total Income", f"RM {ie.get('income', 0):,.2f}")
    m2.metric("💸 Total Expenses", f"RM {ie.get('expenses', 0):,.2f}")
    m3.metric("💰 Savings Rate", f"{features.get('savings_rate', 0)*100:.1f}%")
    m4.metric("📊 Transactions", summary.get("transaction_count", 0))

    # --- Insights ---
    st.markdown("## 💡 Insights & Recommendations")
    for insight in insights:
        st.markdown(
            f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True
        )

    # --- Category Breakdown ---
    st.markdown("## 🏷️ Spending by Category")
    cat_data = features.get("category_breakdown", {})
    if cat_data:
        cat_df = pd.DataFrame(list(cat_data.items()), columns=["Category", "Amount"])
        cat_df = cat_df.sort_values("Amount", ascending=False)
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.pie(
                cat_df,
                values="Amount",
                names="Category",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}, height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.bar(
                cat_df,
                x="Amount",
                y="Category",
                orientation="h",
                color="Amount",
                color_continuous_scale="Viridis",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "white"},
                height=400,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- Daily Spending Trend ---
    st.markdown("## 📅 Daily Spending Trend")
    daily = features.get("daily_spending", {})
    if daily:
        daily_df = pd.DataFrame(list(daily.items()), columns=["Date", "Amount"])
        daily_df["Date"] = pd.to_datetime(daily_df["Date"])
        daily_df = daily_df.sort_values("Date")
        fig = px.area(
            daily_df, x="Date", y="Amount", color_discrete_sequence=["#7c4dff"]
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "white"},
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Risk Component Breakdown ---
    st.markdown("## 🔍 Score Breakdown")
    col_f, col_b = st.columns(2)
    with col_f:
        st.subheader("Financial Risk Components")
        fc = rs.get("financial_components", {})
        for k, v in fc.items():
            label = k.replace("_", " ").title()
            st.progress(v / 100, text=f"{label}: {v}/100")
    with col_b:
        st.subheader("Burnout Risk Components")
        bc = rs.get("burnout_components", {})
        for k, v in bc.items():
            label = k.replace("_", " ").title()
            st.progress(v / 100, text=f"{label}: {v}/100")

    # --- Transaction Table ---
    st.markdown("## 📋 Transaction Details")
    if not txns.empty:
        display_df = txns[["date", "description", "amount", "category"]].copy()
        display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%Y-%m-%d")
        display_df["amount"] = display_df["amount"].apply(lambda x: f"RM {x:,.2f}")
        st.dataframe(display_df, use_container_width=True, height=400)


if __name__ == "__main__":
    main()
