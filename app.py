import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pharmacy Sales Dashboard", page_icon="💊", layout="wide")


# Full-width charts and tables on both newer and older Streamlit versions
def show_chart(fig):
    try:
        st.plotly_chart(fig, width="stretch")
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


def show_table(data):
    try:
        st.dataframe(data, width="stretch", hide_index=True)
    except Exception:
        st.dataframe(data, use_container_width=True, hide_index=True)

# Load Data
df = pd.read_csv("pharmacy_sales.csv")
df["date"] = pd.to_datetime(df["date"])

# Clinical check: the dataset's "category" column does not match each drug's real
# therapeutic class (for example, Metformin is listed under Pain Relief).
# This mapping assigns the correct class from the medication name.
therapeutic_class = {
    "Amlodipine": "Cardiology",
    "Atorvastatin": "Cardiology",
    "Lisinopril": "Cardiology",
    "Azithromycin": "Antibiotic",
    "Amoxicillin": "Antibiotic",
    "Omeprazole": "Gastro",
    "Metformin": "Diabetes",
    "Cetirizine": "Antihistamine",
    "Paracetamol": "Pain Relief",
    "Ibuprofen": "Pain Relief",
}
df["therapeutic_class"] = df["medication"].map(therapeutic_class)
df["category_matches"] = df["category"] == df["therapeutic_class"]

# These four drugs are only made as oral products, so an "Injection" sale is not possible
oral_only = ["Amlodipine", "Atorvastatin", "Lisinopril", "Metformin"]
df["impossible_form"] = (df["unit"] == "Injection") & df["medication"].isin(oral_only)

# Sidebar Filters
st.sidebar.header("Filters")

class_source = st.sidebar.radio(
    "Group medications by",
    ["Corrected therapeutic class", "Original dataset category"],
    help="The original category column does not match each drug's real class. See the Data Quality tab.",
)
class_col = "therapeutic_class" if class_source == "Corrected therapeutic class" else "category"

categories = sorted(df[class_col].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", ["All"] + categories)

min_date, max_date = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)

payment_methods = sorted(df["payment_method"].unique().tolist())
selected_payments = st.sidebar.multiselect("Payment method", payment_methods, default=payment_methods)

st.sidebar.header("Inventory Settings")
starting_stock = st.sidebar.number_input("Starting stock per medication (units)", 500, 5000, 1500, step=100)
quantity_alert = st.sidebar.slider("Show Low Stock Under (units):", 10, 1000, 400)

# Filter dataset
filtered_df = df.copy()
if selected_category != "All":
    filtered_df = filtered_df[filtered_df[class_col] == selected_category]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df["date"] >= start) & (filtered_df["date"] <= end)]
filtered_df = filtered_df[filtered_df["payment_method"].isin(selected_payments)]

# Dashboard Title
st.title("💊 Pharmacy Medication Sales Dashboard")
st.write(f"Displaying **{len(filtered_df)}** of {len(df)} sales records")

if filtered_df.empty:
    st.warning("No sales match these filters. Try widening the date range or selecting more payment methods.")
    st.stop()

# KPI Row
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"${filtered_df['total_price'].sum():,.0f}")
k2.metric("Units Dispensed", f"{filtered_df['quantity_sold'].sum():,}")
k3.metric("Transactions", f"{len(filtered_df):,}")
k4.metric("Average Sale", f"${filtered_df['total_price'].mean():,.2f}")

tab_sales, tab_inventory, tab_quality = st.tabs(["📈 Sales", "📦 Inventory", "🩺 Data Quality"])

# ---------------- Sales tab ----------------
with tab_sales:
    # Most Dispensed Drugs
    st.subheader("🏆 Most Dispensed Medications")
    dispensed = (filtered_df.groupby(["medication", "therapeutic_class"])["quantity_sold"]
                 .sum().reset_index().sort_values("quantity_sold", ascending=False))
    fig_dispensed = px.bar(
        dispensed,
        x="medication",
        y="quantity_sold",
        color="therapeutic_class",
        title="Most Dispensed Medications (colored by therapeutic class)",
        text="quantity_sold",
        labels={"quantity_sold": "Units dispensed", "medication": "Medication", "therapeutic_class": "Class"},
    )
    fig_dispensed.update_xaxes(categoryorder="total descending")
    show_chart(fig_dispensed)

    col1, col2 = st.columns(2)

    # Revenue by medication
    with col1:
        revenue = (filtered_df.groupby("medication")["total_price"].sum()
                   .reset_index().sort_values("total_price"))
        fig_revenue = px.bar(revenue, x="total_price", y="medication", orientation="h",
                             title="Revenue by Medication",
                             labels={"total_price": "Revenue ($)", "medication": ""})
        show_chart(fig_revenue)

    # Payment method mix
    with col2:
        payments = filtered_df.groupby("payment_method")["total_price"].sum().reset_index()
        fig_payment = px.pie(payments, names="payment_method", values="total_price",
                             title="Revenue by Payment Method", hole=0.45)
        show_chart(fig_payment)

    # Weekly trend
    weekly = (filtered_df.set_index("date").resample("W")[["total_price", "quantity_sold"]]
              .sum().reset_index())
    fig_trend = px.line(weekly, x="date", y="total_price", markers=True,
                        title="Weekly Revenue",
                        labels={"total_price": "Revenue ($)", "date": "Week"})
    show_chart(fig_trend)

    # Dosage form breakdown
    forms = filtered_df.groupby("unit")["quantity_sold"].sum().reset_index().sort_values("quantity_sold", ascending=False)
    fig_forms = px.bar(forms, x="unit", y="quantity_sold", text="quantity_sold",
                       title="Units Dispensed by Dosage Form",
                       labels={"unit": "Dosage form", "quantity_sold": "Units dispensed"})
    show_chart(fig_forms)

# ---------------- Inventory tab ----------------
with tab_inventory:
    st.subheader("📦 Simulated Inventory and Low-Stock Alerts")
    st.caption(
        "The dataset has no stock levels, so inventory is simulated: every medication starts with the "
        "stock set in the sidebar, minus everything sold. Days of supply uses the average daily units "
        "sold over the full period."
    )

    days_in_period = (df["date"].max() - df["date"].min()).days + 1
    inventory = df.groupby(["medication", "therapeutic_class"])["quantity_sold"].sum().reset_index()
    inventory["current_stock"] = starting_stock - inventory["quantity_sold"]
    inventory["avg_daily_units"] = (inventory["quantity_sold"] / days_in_period).round(1)
    inventory["days_of_supply"] = (inventory["current_stock"] / inventory["avg_daily_units"]).round(0)
    inventory["status"] = pd.cut(
        inventory["current_stock"],
        bins=[-float("inf"), 0, quantity_alert, float("inf")],
        labels=["Out of stock", "Low stock", "OK"],
        right=False,
    )
    inventory = inventory.sort_values("current_stock")

    low = inventory[inventory["current_stock"] < quantity_alert]
    if low.empty:
        st.success(f"No medications are below {quantity_alert} units.")
    else:
        st.error(f"{len(low)} medication(s) below {quantity_alert} units: {', '.join(low['medication'])}")

    fig_stock = px.bar(
        inventory, x="current_stock", y="medication", orientation="h", color="status",
        color_discrete_map={"Out of stock": "#d62728", "Low stock": "#ff7f0e", "OK": "#2ca02c"},
        title="Current Stock by Medication", labels={"current_stock": "Units in stock", "medication": ""},
    )
    fig_stock.add_vline(x=quantity_alert, line_dash="dash", annotation_text="Alert threshold")
    show_chart(fig_stock)

    show_table(inventory[["medication", "therapeutic_class", "quantity_sold", "current_stock",
                          "avg_daily_units", "days_of_supply", "status"]])

# ---------------- Data Quality tab ----------------
with tab_quality:
    st.subheader("🩺 Clinical Data Quality Checks")

    match_rate = df["category_matches"].mean()
    impossible = int(df["impossible_form"].sum())
    price_ok = ((df["quantity_sold"] * df["unit_price"]).round(2) - df["total_price"]).abs().max() < 0.01

    q1, q2, q3 = st.columns(3)
    q1.metric("Category matches drug class", f"{match_rate:.1%}")
    q2.metric("Injections of oral-only drugs", impossible)
    q3.metric("Price math correct", "Yes" if price_ok else "No")

    st.markdown(
        f"""
- **Only {match_rate:.1%} of sales list the correct category.** With 6 categories, random assignment would
  match about 16.7% of the time, so the category column appears to be random. This dashboard groups
  medications by their real therapeutic class by default.
- **{impossible} sales are injections of drugs that only come as oral products** (Amlodipine, Atorvastatin,
  Lisinopril, and Metformin).
- **Each drug's unit price ranges from about \\$3 to \\$50**, regardless of the drug or dosage form, which also
  suggests the data is synthetic.
- Total price always equals quantity times unit price, so the revenue figures are internally consistent.
"""
    )

    mismatch = pd.crosstab(df["medication"], df["category"])
    fig_heat = px.imshow(mismatch, text_auto=True, color_continuous_scale="Blues",
                         title="Original Category Assigned to Each Medication (sales count)",
                         labels={"x": "Original category", "y": "Medication", "color": "Sales"})
    show_chart(fig_heat)

    price_range = (df.groupby("medication")["unit_price"].agg(["min", "median", "max"])
                   .round(2).reset_index())
    show_table(price_range)

# Download
st.download_button(
    "⬇️ Download filtered data (CSV)",
    filtered_df.drop(columns=["category_matches", "impossible_form"]).to_csv(index=False),
    file_name="filtered_pharmacy_sales.csv",
    mime="text/csv",
)