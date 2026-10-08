import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "cleaned_sales_dataset.csv")


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    return df


df = load_data(DATA_PATH)

st.title("🛒 Retail Sales Dashboard")
st.caption("Built on the cleaned sales dataset — Data Cleaning & Visualization internship project.")

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")

cities = sorted(df["City"].unique())
categories = sorted(df["Category"].unique())
payment_methods = sorted(df["Payment_Method"].unique())

selected_cities = st.sidebar.multiselect("City", cities, default=cities)
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
selected_payments = st.sidebar.multiselect("Payment Method", payment_methods, default=payment_methods)

min_date, max_date = df["Order_Date"].min(), df["Order_Date"].max()
date_range = st.sidebar.date_input("Order Date Range", value=(min_date, max_date),
                                    min_value=min_date, max_value=max_date)

filtered = df[
    df["City"].isin(selected_cities)
    & df["Category"].isin(selected_categories)
    & df["Payment_Method"].isin(selected_payments)
]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["Order_Date"] >= start) & (filtered["Order_Date"] <= end)]

if filtered.empty:
    st.warning("No data matches the selected filters. Please widen your filter selection.")
    st.stop()

# ---------------- KPIs ----------------
total_sales = filtered["Sales"].sum()
total_orders = len(filtered)
avg_order_value = filtered["Sales"].mean()
avg_rating = filtered["Rating"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"₹{total_sales:,.0f}")
k2.metric("Total Orders", f"{total_orders:,}")
k3.metric("Avg Order Value", f"₹{avg_order_value:,.0f}")
k4.metric("Avg Customer Rating", f"{avg_rating:.2f} / 5")

st.divider()

# ---------------- Charts row 1 ----------------
col1, col2 = st.columns(2)

with col1:
    cat_sales = filtered.groupby("Category", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    fig = px.bar(cat_sales, x="Sales", y="Category", orientation="h",
                 title="Sales by Category", color="Sales", color_continuous_scale="Viridis")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    city_sales = filtered.groupby("City", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    fig = px.bar(city_sales, x="Sales", y="City", orientation="h",
                 title="Sales by City", color="Sales", color_continuous_scale="Teal")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Charts row 2 ----------------
col3, col4 = st.columns(2)

with col3:
    monthly = filtered.set_index("Order_Date").resample("ME")["Sales"].sum().reset_index()
    fig = px.line(monthly, x="Order_Date", y="Sales", markers=True, title="Monthly Sales Trend")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    top_products = (
        filtered.groupby("Product", as_index=False)["Sales"].sum()
        .sort_values("Sales", ascending=False).head(10)
    )
    fig = px.bar(top_products, x="Sales", y="Product", orientation="h", title="Top 10 Products by Sales")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------- Charts row 3 ----------------
col5, col6 = st.columns(2)

with col5:
    payment_counts = filtered["Payment_Method"].value_counts().reset_index()
    payment_counts.columns = ["Payment_Method", "Orders"]
    fig = px.pie(payment_counts, names="Payment_Method", values="Orders", title="Orders by Payment Method")
    st.plotly_chart(fig, use_container_width=True)

with col6:
    fig = px.histogram(filtered, x="Customer_Age", nbins=20, title="Customer Age Distribution")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Filtered Data")
st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
