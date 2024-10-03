import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg 
import seaborn as sns 
import streamlit as st
import urllib
from func import DataAnalyzer, BrazilMapPlotter

sns.set(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
ecommerce_df = pd.read_csv("https://raw.githubusercontent.com/ramdhan8/submission-dicoding-ecommerce/master/dashboard/df.csv")
ecommerce_df.sort_values(by="order_approved_at", inplace=True)
ecommerce_df.reset_index(inplace=True)

# Geolocation Dataset
geo_data = pd.read_csv("https://raw.githubusercontent.com/ramdhan8/submission-dicoding-ecommerce/master/dashboard/geolocation.csv")
unique_geo_data = geo_data.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    ecommerce_df[col] = pd.to_datetime(ecommerce_df[col])

min_date = ecommerce_df["order_approved_at"].min()
max_date = ecommerce_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/ramdhan8/submission-dicoding-ecommerce/master/dashboard/logo.png", width=100)
    
    # Date Range Selector
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Filter data based on date range
filtered_df = ecommerce_df[(ecommerce_df["order_approved_at"] >= str(start_date)) & 
                           (ecommerce_df["order_approved_at"] <= str(end_date))]

analyzer = DataAnalyzer(filtered_df)
brazil_plotter = BrazilMapPlotter(unique_geo_data, plt, mpimg, urllib, st)

# Data Analysis
daily_orders = analyzer.create_daily_orders_df()
total_spending = analyzer.create_sum_spend_df()
order_items = analyzer.create_sum_order_items_df()
review_score_data, most_common_review = analyzer.review_score_df()
customer_state, most_common_state = analyzer.create_bystate_df()
order_status_data, most_frequent_status = analyzer.create_order_status()

# Streamlit App
st.title("E-Commerce Public Data Dashboard")

st.write("**This dashboard provides an analysis of public e-commerce data.**")

# Daily Orders Section
st.subheader("Orders Delivered Per Day")
col1, col2 = st.columns(2)

with col1:
    total_order_count = daily_orders["order_count"].sum()
    st.markdown(f"Total Orders: **{total_order_count}**")

with col2:
    total_revenue_generated = daily_orders["revenue"].sum()
    st.markdown(f"Total Revenue: **{total_revenue_generated}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=daily_orders["order_approved_at"],
    y=daily_orders["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Customer Spending Section
st.subheader("Customer Spending Patterns")
col1, col2 = st.columns(2)

with col1:
    total_spent = total_spending["total_spend"].sum()
    st.markdown(f"Total Spent: **{total_spent}**")

with col2:
    avg_spending = total_spending["total_spend"].mean()
    st.markdown(f"Average Spending: **{avg_spending}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    data=total_spending,
    x="order_approved_at",
    y="total_spend",
    marker="o",
    linewidth=2,
    color="#90CAF9"
)

ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Order Items Section
st.subheader("Ordered Items Overview")
col1, col2 = st.columns(2)

with col1:
    total_items_ordered = order_items["product_count"].sum()
    st.markdown(f"Total Items Ordered: **{total_items_ordered}**")

with col2:
    avg_items_ordered = order_items["product_count"].mean()
    st.markdown(f"Average Items Ordered: **{avg_items_ordered}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

# Top 5 Products
sns.barplot(x="product_count", y="product_category_name_english", data=order_items.head(5), palette="viridis", ax=ax[0])
ax[0].set_xlabel("Sales Count", fontsize=80)
ax[0].set_title("Top Sold Products", loc="center", fontsize=90)
ax[0].tick_params(axis='y', labelsize=55)

# Least 5 Products
sns.barplot(x="product_count", y="product_category_name_english", data=order_items.tail(5), palette="viridis", ax=ax[1])
ax[1].invert_xaxis()
ax[1].set_xlabel("Sales Count", fontsize=80)
ax[1].set_title("Least Sold Products", loc="center", fontsize=90)
ax[1].tick_params(axis='y', labelsize=55)
st.pyplot(fig)

# Review Scores Section
st.subheader("Customer Review Scores")
col1, col2 = st.columns(2)

with col1:
    avg_review_score = review_score_data.mean()
    st.markdown(f"Average Review Score: **{avg_review_score:.2f}**")

with col2:
    common_review_score = review_score_data.value_counts().idxmax()
    st.markdown(f"Most Common Review Score: **{common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
colors = sns.color_palette("viridis", len(review_score_data))

sns.barplot(x=review_score_data.index, y=review_score_data.values, palette=colors)
plt.title("Review Scores Distribution", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
for i, v in enumerate(review_score_data.values):
    ax.text(i, v + 5, str(v), ha='center', fontsize=12, color='black')

st.pyplot(fig)

# Customer Demographics Section
st.subheader("Customer Demographics")
tab1, tab2 = st.tabs(["State", "Geolocation"])

with tab1:
    common_state = customer_state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=customer_state.customer_state.value_counts().index,
                y=customer_state.customer_count.values, 
                palette="viridis")
    plt.title("Customers by State", fontsize=15)
    st.pyplot(fig)

with tab2:
    brazil_plotter.plot()

    with st.expander("Explanation"):
        st.write("The map highlights customer concentration, showing a higher density in the southeastern and southern regions, particularly in major cities like São Paulo and Rio de Janeiro.")

st.caption('All rights reserved. Custom project by Nur Rahmat Ramdhan © 2024')
