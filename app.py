"""
app.py
──────
Streamlit frontend for the SuperMarket Sales Analysis dashboard.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_data, summary_stats, branch_summary, product_summary

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supermarket Sales Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS  (clean, readable, professional)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Main header */
        .main-header {
            font-size: 2rem;
            font-weight: 700;
            color: #1f2328;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1rem;
            color: #57606a;
            margin-bottom: 1.5rem;
        }
        /* Section titles */
        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1f2328;
            border-left: 4px solid #3b82d4;
            padding-left: 0.6rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        /* KPI cards */
        [data-testid="metric-container"] {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.8rem 1rem;
        }
        [data-testid="metric-container"] label {
            font-size: 0.75rem !important;
            color: #57606a !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            color: #1f2328 !important;
        }
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #f7f8fa;
            border-right: 1px solid #e5e7eb;
        }
        /* Dataframe text */
        .stDataFrame { font-size: 0.85rem; }
        /* Divider */
        hr { border-color: #e5e7eb; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Load & cache data
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def get_data():
    return load_data()


df_full = get_data()

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — Filters
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 Supermarket Analytics")
    st.markdown("### 🔍 Filters")
    st.markdown("---")

    branches = sorted(df_full["Branch"].unique())
    sel_branches = st.multiselect(
        "Branch", options=branches, default=branches, help="Select one or more branches"
    )

    product_lines = sorted(df_full["Product Line"].unique())
    sel_products = st.multiselect(
        "Product Line",
        options=product_lines,
        default=product_lines,
        help="Select one or more product lines",
    )

    genders = sorted(df_full["Gender"].unique())
    sel_genders = st.multiselect(
        "Gender", options=genders, default=genders
    )

    customer_types = sorted(df_full["Customer Type"].unique())
    sel_cust = st.multiselect(
        "Customer Type", options=customer_types, default=customer_types
    )

    payments = sorted(df_full["Payment"].unique())
    sel_pay = st.multiselect(
        "Payment Method", options=payments, default=payments
    )

    st.markdown("---")
    st.markdown(
        "<span style='font-size:0.75rem;color:#57606a;'>Data: SuperMarket Analysis.csv</span>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Apply filters
# ─────────────────────────────────────────────────────────────────────────────
df = df_full[
    df_full["Branch"].isin(sel_branches)
    & df_full["Product Line"].isin(sel_products)
    & df_full["Gender"].isin(sel_genders)
    & df_full["Customer Type"].isin(sel_cust)
    & df_full["Payment"].isin(sel_pay)
].copy()

if df.empty:
    st.warning("⚠️  No data matches the current filters. Please broaden your selections.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🛒 Supermarket Sales Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Interactive dashboard for supermarket sales performance — '
    f"showing <strong>{len(df):,}</strong> of <strong>{len(df_full):,}</strong> transactions</div>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# ① KPI Row
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Key Performance Indicators</div>', unsafe_allow_html=True)

kpis = summary_stats(df)
cols = st.columns(4)
kpi_items = list(kpis.items())

for i, col in enumerate(cols):
    with col:
        label, val = kpi_items[i]
        st.metric(label, f"{val:,.2f}" if isinstance(val, float) else f"{val:,}")

cols2 = st.columns(4)
for i, col in enumerate(cols2):
    with col:
        label, val = kpi_items[i + 4]
        st.metric(label, f"{val:,.2f}" if isinstance(val, float) else f"{val:,}")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ② Data Quality Report
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("🔎 Data Quality Report", expanded=False):
    st.markdown("**Missing values per column (after cleaning)**")
    missing = df.isnull().sum().rename("Missing Values").reset_index()
    missing.columns = ["Column", "Missing Values"]
    missing["% Missing"] = (missing["Missing Values"] / len(df) * 100).round(2)
    st.dataframe(missing, use_container_width=True, hide_index=True)

    st.markdown("**Descriptive statistics for numeric columns**")
    desc = df.describe().T.round(2)
    st.dataframe(desc, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# ③ Sales = Quantity × Unit Price  (verification table)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🧮 Sales Calculation Verification</div>', unsafe_allow_html=True)
st.caption("Sales is computed as **Quantity × Unit Price** for every transaction.")

sample_cols = ["Invoice ID", "Branch", "Product Line", "Unit Price", "Quantity", "Sales", "Tax (5%)", "Gross Income", "Rating"]
st.dataframe(
    df[sample_cols].head(20).style.format(
        {"Unit Price": "${:,.2f}", "Sales": "${:,.2f}", "Tax (5%)": "${:,.2f}", "Gross Income": "${:,.2f}"}
    ),
    use_container_width=True,
    hide_index=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# ④ Branch Analysis
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🏪 Branch Performance</div>', unsafe_allow_html=True)

b_sum = branch_summary(df)
b_sum.columns = ["Branch", "Transactions", "Total Sales ($)", "Avg Sale ($)", "Total Qty", "Avg Rating", "Gross Income ($)"]

col_t, col_c = st.columns([1.5, 2.5])

with col_t:
    st.markdown("**Summary Table**")
    st.dataframe(
        b_sum.style.format(
            {"Total Sales ($)": "${:,.2f}", "Avg Sale ($)": "${:,.2f}",
             "Gross Income ($)": "${:,.2f}", "Avg Rating": "{:.2f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

with col_c:
    fig_branch = px.bar(
        b_sum,
        x="Branch",
        y="Total Sales ($)",
        color="Branch",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Total Sales by Branch",
    )
    fig_branch.update_layout(
        showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=20, l=10, r=10),
        yaxis_title="Total Sales (USD)",
    )
    st.plotly_chart(fig_branch, use_container_width=True)

# Branch rating vs gross income scatter
fig_bscatter = px.scatter(
    b_sum,
    x="Avg Rating",
    y="Gross Income ($)",
    size="Total Sales ($)",
    color="Branch",
    text="Branch",
    color_discrete_sequence=px.colors.qualitative.Set2,
    title="Branch: Avg Rating vs Gross Income (bubble = Total Sales)",
)
fig_bscatter.update_traces(textposition="top center")
fig_bscatter.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=40, b=20, l=10, r=10),
)
st.plotly_chart(fig_bscatter, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# ⑤ Product Line Analysis
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📦 Product Line Performance</div>', unsafe_allow_html=True)

p_sum = product_summary(df)
p_sum.columns = ["Product Line", "Transactions", "Total Sales ($)", "Avg Sale ($)", "Total Qty", "Avg Rating"]

col_p1, col_p2 = st.columns(2)

with col_p1:
    fig_pie = px.pie(
        p_sum,
        names="Product Line",
        values="Total Sales ($)",
        title="Sales Share by Product Line",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.38,
    )
    fig_pie.update_traces(textinfo="label+percent", textposition="outside")
    fig_pie.update_layout(
        margin=dict(t=40, b=20, l=10, r=10),
        paper_bgcolor="white",
        showlegend=False,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_p2:
    fig_bar_prod = px.bar(
        p_sum.sort_values("Total Sales ($)"),
        x="Total Sales ($)",
        y="Product Line",
        orientation="h",
        color="Total Sales ($)",
        color_continuous_scale="Blues",
        text_auto=".2s",
        title="Total Sales by Product Line",
    )
    fig_bar_prod.update_layout(
        coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=20, l=10, r=10),
        xaxis_title="Total Sales (USD)",
    )
    st.plotly_chart(fig_bar_prod, use_container_width=True)

# Product line avg rating
fig_rating = px.bar(
    p_sum.sort_values("Avg Rating", ascending=False),
    x="Product Line",
    y="Avg Rating",
    color="Avg Rating",
    color_continuous_scale="RdYlGn",
    text_auto=".2f",
    title="Average Customer Rating by Product Line",
)
fig_rating.update_layout(
    coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=40, b=20, l=10, r=10),
    yaxis=dict(range=[0, 10]),
)
st.plotly_chart(fig_rating, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# ⑥ Customer & Demographics
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">👤 Customer Demographics</div>', unsafe_allow_html=True)

col_d1, col_d2 = st.columns(2)

with col_d1:
    gender_sales = df.groupby("Gender")["Sales"].sum().reset_index()
    fig_gen = px.pie(
        gender_sales, names="Gender", values="Sales",
        title="Sales by Gender",
        color_discrete_sequence=["#7c5cd8", "#3b82d4"],
        hole=0.4,
    )
    fig_gen.update_layout(paper_bgcolor="white", margin=dict(t=40, b=10, l=10, r=10))
    st.plotly_chart(fig_gen, use_container_width=True)

with col_d2:
    cust_sales = df.groupby("Customer Type")["Sales"].sum().reset_index()
    fig_cust = px.bar(
        cust_sales, x="Customer Type", y="Sales",
        color="Customer Type",
        text_auto=".2s",
        title="Total Sales by Customer Type",
        color_discrete_sequence=["#3b82d4", "#7c5cd8"],
    )
    fig_cust.update_layout(
        showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=10, l=10, r=10),
        yaxis_title="Total Sales (USD)",
    )
    st.plotly_chart(fig_cust, use_container_width=True)

# Gender × Product Line heatmap
gender_prod = df.groupby(["Gender", "Product Line"])["Sales"].sum().reset_index()
fig_heat = px.density_heatmap(
    gender_prod,
    x="Product Line",
    y="Gender",
    z="Sales",
    color_continuous_scale="Blues",
    title="Sales Heatmap: Gender × Product Line",
    text_auto=".2s",
)
fig_heat.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=40, b=20, l=10, r=10),
    xaxis_tickangle=-20,
)
st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# ⑦ Payment Analysis
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">💳 Payment Method Analysis</div>', unsafe_allow_html=True)

pay_sum = (
    df.groupby("Payment")
    .agg(Transactions=("Invoice ID", "count"), Total_Sales=("Sales", "sum"), Avg_Sale=("Sales", "mean"))
    .round(2)
    .reset_index()
    .sort_values("Total_Sales", ascending=False)
)

col_pay1, col_pay2 = st.columns(2)

with col_pay1:
    fig_pay_pie = px.pie(
        pay_sum, names="Payment", values="Total_Sales",
        title="Sales Share by Payment Method",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.38,
    )
    fig_pay_pie.update_layout(paper_bgcolor="white", margin=dict(t=40, b=10, l=10, r=10))
    st.plotly_chart(fig_pay_pie, use_container_width=True)

with col_pay2:
    fig_pay_bar = px.bar(
        pay_sum, x="Payment", y="Transactions",
        color="Payment",
        text_auto=True,
        title="Number of Transactions by Payment Method",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_pay_bar.update_layout(
        showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=10, l=10, r=10),
        yaxis_title="Transactions",
    )
    st.plotly_chart(fig_pay_bar, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# ⑧ Time Series & Temporal Trends
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📅 Sales Trends Over Time</div>', unsafe_allow_html=True)

# Daily sales
daily = df.groupby("Date")["Sales"].sum().reset_index().sort_values("Date")
fig_daily = px.line(
    daily, x="Date", y="Sales",
    title="Daily Total Sales",
    color_discrete_sequence=["#3b82d4"],
    markers=True,
)
fig_daily.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=40, b=20, l=10, r=10),
    yaxis_title="Total Sales (USD)",
    xaxis_title="Date",
)
st.plotly_chart(fig_daily, use_container_width=True)

col_t1, col_t2 = st.columns(2)

with col_t1:
    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    monthly = (
        df.groupby(["Month", "Month Num"])["Sales"]
        .sum()
        .reset_index()
        .sort_values("Month Num")
    )
    fig_month = px.bar(
        monthly, x="Month", y="Sales",
        color="Sales", color_continuous_scale="Blues",
        text_auto=".2s",
        title="Monthly Sales",
    )
    fig_month.update_layout(
        coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=20, l=10, r=10),
        yaxis_title="Total Sales (USD)",
    )
    st.plotly_chart(fig_month, use_container_width=True)

with col_t2:
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df.groupby("Day of Week")["Sales"].mean().reindex(dow_order).reset_index()
    dow.columns = ["Day", "Avg Sales"]
    fig_dow = px.bar(
        dow, x="Day", y="Avg Sales",
        color="Avg Sales", color_continuous_scale="Greens",
        text_auto=".2f",
        title="Average Sales by Day of Week",
    )
    fig_dow.update_layout(
        coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=20, l=10, r=10),
        yaxis_title="Avg Sales (USD)",
    )
    st.plotly_chart(fig_dow, use_container_width=True)

# Hourly distribution
if df["Hour"].notna().any():
    hourly = df.groupby("Hour")["Sales"].sum().reset_index()
    fig_hour = px.area(
        hourly, x="Hour", y="Sales",
        title="Sales by Hour of Day",
        color_discrete_sequence=["#7c5cd8"],
        markers=True,
    )
    fig_hour.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=20, l=10, r=10),
        yaxis_title="Total Sales (USD)",
        xaxis=dict(tickmode="linear", dtick=1),
    )
    st.plotly_chart(fig_hour, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# ⑨ Profitability Analysis
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">💰 Profitability & Income</div>', unsafe_allow_html=True)

col_pr1, col_pr2 = st.columns(2)

with col_pr1:
    prod_income = (
        df.groupby("Product Line")["Gross Income"].sum().reset_index()
        .sort_values("Gross Income", ascending=False)
    )
    fig_income = px.bar(
        prod_income,
        x="Product Line", y="Gross Income",
        color="Gross Income", color_continuous_scale="Purples",
        text_auto=".2s",
        title="Gross Income by Product Line",
    )
    fig_income.update_layout(
        coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=20, l=10, r=10),
        xaxis_tickangle=-20,
        yaxis_title="Gross Income (USD)",
    )
    st.plotly_chart(fig_income, use_container_width=True)

with col_pr2:
    branch_income = df.groupby("Branch")["Gross Income"].sum().reset_index()
    fig_b_income = px.bar(
        branch_income, x="Branch", y="Gross Income",
        color="Branch",
        text_auto=".2s",
        title="Gross Income by Branch",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_b_income.update_layout(
        showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=20, l=10, r=10),
        yaxis_title="Gross Income (USD)",
    )
    st.plotly_chart(fig_b_income, use_container_width=True)

# Rating vs Sales scatter
fig_rs = px.scatter(
    df,
    x="Rating", y="Sales",
    color="Product Line",
    size="Quantity",
    opacity=0.65,
    title="Rating vs Sales per Transaction (size = Quantity)",
    color_discrete_sequence=px.colors.qualitative.Set1,
    hover_data=["Branch", "Payment", "Date"],
)
fig_rs.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=40, b=20, l=10, r=10),
    yaxis_title="Sales (USD)",
)
st.plotly_chart(fig_rs, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# ⑩ Business Insights & Recommendations
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">💡 Business Insights & Recommendations</div>', unsafe_allow_html=True)

top_branch = branch_summary(df).sort_values("Total_Sales", ascending=False).iloc[0]
top_product = product_summary(df).iloc[0]
top_payment = pay_sum.iloc[0]
best_hour = df.groupby("Hour")["Sales"].sum().idxmax() if df["Hour"].notna().any() else "N/A"

insights = [
    {
        "icon": "🏆",
        "title": f"Top Branch: {top_branch['Branch']}",
        "text": f"Generated **${top_branch['Total_Sales']:,.2f}** in total sales. "
                f"Consider replicating its operational model at underperforming branches.",
    },
    {
        "icon": "📦",
        "title": f"Best-Selling Product Line: {top_product['Product Line']}",
        "text": f"Contributed **${top_product['Total_Sales']:,.2f}** in sales. "
                f"Increase inventory and promotional spend for this category.",
    },
    {
        "icon": "💳",
        "title": f"Preferred Payment Method: {top_payment['Payment']}",
        "text": f"Used in **{top_payment['Transactions']:,}** transactions. "
                f"Ensure seamless support and possible discount incentives for this method.",
    },
    {
        "icon": "⏰",
        "title": f"Peak Shopping Hour: {best_hour}:00",
        "text": "Staff more cashiers and ensure shelves are fully stocked during peak hours "
                "to maximise throughput and customer satisfaction.",
    },
    {
        "icon": "👥",
        "title": "Member vs Normal Customers",
        "text": "Analyse member vs normal spending gaps. If Normal customers spend similarly, "
                "a targeted loyalty programme could convert them and increase lifetime value.",
    },
    {
        "icon": "⭐",
        "title": "Customer Satisfaction",
        "text": f"Overall average rating is **{df['Rating'].mean():.2f}/10**. "
                "Focus on product lines with ratings below 7 to improve customer experience.",
    },
]

for ins in insights:
    with st.container():
        st.markdown(
            f"""
            <div style="background:#f7f8fa;border:1px solid #e5e7eb;border-radius:8px;
                        padding:1rem 1.2rem;margin-bottom:0.75rem;">
                <span style="font-size:1.1rem;font-weight:700;color:#1f2328;">{ins['icon']} {ins['title']}</span><br/>
                <span style="font-size:0.9rem;color:#57606a;">{ins['text']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# ⑪ Raw Data Explorer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Raw Data Explorer</div>', unsafe_allow_html=True)

with st.expander("Browse & Download Filtered Dataset", expanded=False):
    st.markdown(f"**{len(df):,} rows × {len(df.columns)} columns**")
    st.dataframe(
        df.style.format(
            {"Unit Price": "${:,.2f}", "Sales": "${:,.2f}",
             "Tax (5%)": "${:,.2f}", "Gross Income": "${:,.2f}",
             "COGS": "${:,.2f}", "Gross Margin %": "{:.4f}%"}
        ),
        use_container_width=True,
        height=400,
    )
    csv_export = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download Filtered Data as CSV",
        data=csv_export,
        file_name="supermarket_filtered.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:0.78rem;color:#57606a;padding:0.5rem 0;'>"
    "Supermarket Sales Analytics Dashboard &nbsp;|&nbsp; Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True,
)
