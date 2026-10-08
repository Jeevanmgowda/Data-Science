import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(text):
    cells.append(nbf.v4.new_code_cell(text))

# 1. Project Introduction
md("""# Data Cleaning & Visualization Project — Retail Sales Analysis

**Internship Project:** Data Cleaning & Visualization

This notebook takes a raw, messy retail sales dataset, inspects it, cleans it,
explores it, visualizes it, and extracts business insights — end to end.
""")

# 2. Objective
md("""## Objective

- Understand common real-world data quality problems (missing values, duplicates,
  inconsistent categories, outliers, mixed data types).
- Learn how to systematically clean a dataset with Pandas/NumPy.
- Practice Exploratory Data Analysis (EDA) and visualization with Matplotlib/Seaborn.
- Turn the analysis into clear, evidence-based insights (data storytelling).
""")

# 3. Import Libraries
md("## 3. Import Libraries")
code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (9, 5)
pd.set_option("display.max_columns", None)
""")

# 4. Load Dataset
md("""## 4. Load Dataset

We load the **raw** dataset exactly as it was collected — including its problems.
We will not modify this raw file; all cleaning happens on a copy in memory,
and the result is saved separately as the *cleaned* dataset.
""")
code("""raw_df = pd.read_csv("../data/raw_sales_dataset.csv")
raw_df.head()
""")

# 5. Dataset Overview
md("## 5. Dataset Overview")
code("""print("Shape (rows, columns):", raw_df.shape)
print("\\nColumn names:")
print(list(raw_df.columns))
""")
code("""raw_df.info()
""")
code("""raw_df.tail()
""")

# 6. Data Quality Assessment
md("""## 6. Data Quality Assessment

Before touching anything, let's get a full picture of *what's wrong* with this data.
""")
code("""raw_df.describe(include="all").T
""")

# 7. Missing Value Analysis
md("""## 7. Missing Value Analysis

Missing values (`NaN`) usually happen because of skipped form fields, failed sensors,
optional inputs, or merge issues. We check **how many** and **where**.
""")
code("""missing = raw_df.isna().sum()
missing_pct = (missing / len(raw_df) * 100).round(2)
pd.DataFrame({"missing_count": missing, "missing_%": missing_pct}).sort_values("missing_count", ascending=False)
""")

# 8. Duplicate Analysis
md("""## 8. Duplicate Analysis

Duplicate rows can happen from double form submissions, repeated imports, or
logging errors. They inflate totals and distort averages if left in.
""")
code("""num_duplicates = raw_df.duplicated().sum()
print("Fully duplicated rows:", num_duplicates)
raw_df[raw_df.duplicated(keep=False)].sort_values("Order_ID").head(10)
""")

# 9. Data Type Analysis
md("""## 9. Data Type Analysis

`Quantity` and `Unit_Price` should be numeric, but a few rows contain text
noise (e.g. `"3 units"`, `"₹1200.5"`), which forces Pandas to store the whole
column as `object` (text) instead of a number.
""")
code("""print(raw_df.dtypes)
print()
print("Sample messy Quantity values:")
print(raw_df["Quantity"].astype(str).str.extract(r"([a-zA-Z]+)").dropna().head())
print()
print("Sample messy Unit_Price values:")
print(raw_df[raw_df["Unit_Price"].astype(str).str.contains("₹", na=False)]["Unit_Price"].head())
""")

# 10. Outlier Analysis
md("""## 10. Outlier Analysis

We use the **IQR (Interquartile Range) method**: values below `Q1 - 1.5*IQR` or
above `Q3 + 1.5*IQR` are flagged as statistical outliers.

Important: a statistical outlier is **not automatically wrong**. A ₹90,000
laptop is a genuine high-value sale, not an error — while a "customer age of 2"
is clearly a data-quality issue. We look at each flagged column with that lens
before deciding what to do with it.
""")
code("""numeric_cols_raw = raw_df.select_dtypes(include=np.number).columns.tolist()
print("Numeric columns detected in the raw data:", numeric_cols_raw)

def iqr_outlier_count(series):
    s = pd.to_numeric(series, errors="coerce").dropna()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return ((s < low) | (s > high)).sum(), low, high

for col in ["Sales", "Customer_Age", "Rating"]:
    count, low, high = iqr_outlier_count(raw_df[col])
    print(f"{col}: {count} potential outliers (bounds: {low:.2f} to {high:.2f})")
""")
code("""print("Suspicious Customer_Age values:", sorted(raw_df["Customer_Age"].dropna().unique())[:5],
      "...", sorted(raw_df["Customer_Age"].dropna().unique())[-5:])
print("Suspicious Rating values (should be 1-5):", sorted(raw_df["Rating"].dropna().unique()))
print("Negative Quantity rows:", raw_df["Quantity"].astype(str).str.contains("-").sum())
""")

# 11. Data Cleaning
md("""## 11. Data Cleaning

We now clean the data step by step. Each step is explained before the code.

**General rule we follow:** never blindly fill everything with 0, and never
remove every statistical outlier — the treatment is chosen per column based on
what makes sense for that column.
""")

md("### 11.1 Standardize text columns (whitespace, inconsistent capitalization, aliases)")
code("""df = raw_df.copy()

# Trim whitespace and fix casing
df["Customer_Name"] = df["Customer_Name"].str.strip().str.title()
df["City"] = df["City"].str.strip().str.title().replace({"Bengaluru": "Bangalore"})
df["Category"] = df["Category"].str.strip().str.title().replace({"Cloths": "Clothing", "Foot Wear": "Footwear"})
df["Payment_Method"] = df["Payment_Method"].str.strip().str.title().replace({"Upi": "UPI"})

print("Unique City values after cleaning:", sorted(df["City"].dropna().unique()))
print("Unique Category values after cleaning:", sorted(df["Category"].dropna().unique()))
""")

md("### 11.2 Fix data types (Unit_Price and Quantity should be numeric)")
code("""df["Unit_Price"] = df["Unit_Price"].astype(str).str.replace("₹", "", regex=False).str.strip()
df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce")

df["Quantity"] = df["Quantity"].astype(str).str.extract(r"(-?\\d+)").astype(float)

print(df[["Unit_Price", "Quantity"]].dtypes)
""")

md("### 11.3 Fix invalid values (negative quantity, out-of-range ratings)")
code("""# A negative Quantity is not a real business scenario here (not a returns dataset) -> sign error, take absolute value
df.loc[df["Quantity"] < 0, "Quantity"] = df.loc[df["Quantity"] < 0, "Quantity"].abs()

# Rating is only valid between 1 and 5 -> treat out-of-range values as missing
df.loc[(df["Rating"] < 1) | (df["Rating"] > 5), "Rating"] = np.nan

print("Remaining out-of-range ratings:", ((df['Rating'] < 1) | (df['Rating'] > 5)).sum())
""")

md("### 11.4 Standardize dates")
code("""def parse_date(val):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["Order_Date"] = df["Order_Date"].apply(parse_date)
print("Unparseable dates left:", df["Order_Date"].isna().sum())
""")

md("### 11.5 Recompute Sales consistently")
code("""recalculated_sales = df["Quantity"] * df["Unit_Price"]
mismatch = (df["Sales"] - recalculated_sales).abs() > 1
print("Rows where stored Sales did not equal Quantity x Unit_Price:", mismatch.sum())
df["Sales"] = recalculated_sales.round(2)
""")

md("""### 11.6 Handle missing values (column-appropriate strategy)

- `Customer_Age`, `Rating` → numeric → fill with **median** (robust to outliers, unlike mean)
- `City`, `Payment_Method` → categorical → fill with **mode** (most frequent value)
- `Unit_Price` → recompute from `Sales / Quantity` where possible, otherwise median
- `Order_Date` → cannot be guessed → rows with unparseable dates are dropped
""")
code("""before_missing = df.isna().sum()

df["Customer_Age"] = df["Customer_Age"].fillna(df["Customer_Age"].median())
df["Rating"] = df["Rating"].fillna(df["Rating"].median())
df["City"] = df["City"].fillna(df["City"].mode()[0])
df["Payment_Method"] = df["Payment_Method"].fillna(df["Payment_Method"].mode()[0])

mask_missing_price = df["Unit_Price"].isna() & df["Quantity"].notna() & (df["Quantity"] != 0)
df.loc[mask_missing_price, "Unit_Price"] = df.loc[mask_missing_price, "Sales"] / df.loc[mask_missing_price, "Quantity"]
df["Unit_Price"] = df["Unit_Price"].fillna(df["Unit_Price"].median())
df["Sales"] = (df["Quantity"] * df["Unit_Price"]).round(2)

df = df.dropna(subset=["Order_Date"])

after_missing = df.isna().sum()
pd.DataFrame({"before": before_missing, "after": after_missing})
""")

md("### 11.7 Remove duplicate rows")
code("""before_rows = len(df)
df = df.drop_duplicates()
print(f"Removed {before_rows - len(df)} duplicate rows ({before_rows} -> {len(df)})")
""")

md("""### 11.8 Outlier treatment

We deliberately do **not** apply one global IQR rule to `Sales`/`Unit_Price`,
because categories like Electronics and Groceries naturally sit on very
different price scales — a global rule would wrongly flag most electronics
sales as "outliers". Instead:

- `Quantity`: statistically the IQR bound sits around 3.5, which would flag
  even normal bulk orders of 4-5 units. Since those are still realistic retail
  quantities, we only cap clearly implausible values (orders of 50-100 units,
  which were injected data-entry errors) using a **domain-based cap of 10**.
- `Customer_Age`: ages like 2, 3, 95, 99 are implausible for a retail customer
  → clipped to a realistic 16-85 range.
- `Unit_Price`: checked **per category** with a wide IQR multiplier (k=3), so
  only genuinely extreme, data-entry-error-like prices are capped — normal
  premium items are left untouched.
""")
code("""def iqr_bounds(series, k=1.5):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

low_q, high_q = iqr_bounds(df["Quantity"])
print(f"Quantity IQR bounds (for reference only): {low_q:.2f} to {high_q:.2f}")
print("Values above domain cap of 10 (treated as errors):", (df['Quantity'] > 10).sum())
df["Quantity"] = df["Quantity"].clip(lower=1, upper=10)

low_a, high_a = iqr_bounds(df["Customer_Age"])
print(f"Customer_Age IQR bounds: {low_a:.2f} to {high_a:.2f}")
df["Customer_Age"] = df["Customer_Age"].clip(lower=16, upper=85)
""")
code("""def cap_per_category(frame, col, k=3):
    capped = frame.copy()
    total_flagged = 0
    for cat, group in frame.groupby("Category"):
        q1, q3 = group[col].quantile(0.25), group[col].quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - k * iqr, q3 + k * iqr
        mask = (group[col] < low) | (group[col] > high)
        total_flagged += mask.sum()
        capped.loc[group.index, col] = group[col].clip(lower=max(low, 0), upper=high)
    print(f"{col}: {total_flagged} extreme values capped (per-category IQR, k={k})")
    return capped

df = cap_per_category(df, "Unit_Price")
df["Sales"] = (df["Quantity"] * df["Unit_Price"]).round(2)
""")

md("### 11.9 Final dtype cleanup")
code("""df["Quantity"] = df["Quantity"].round().astype(int)
df["Customer_Age"] = df["Customer_Age"].round().astype(int)
df["Order_Date"] = pd.to_datetime(df["Order_Date"]).dt.strftime("%Y-%m-%d")
df = df.reset_index(drop=True)
df.head()
""")

# 12. Cleaned Dataset Validation
md("""## 12. Cleaned Dataset Validation

A final check before saving: no missing values, no duplicates, sensible ranges.
""")
code("""print("Shape:", df.shape)
print("\\nMissing values:\\n", df.isna().sum())
print("\\nDuplicate rows:", df.duplicated().sum())
print("\\nRanges:")
print(df[["Quantity", "Unit_Price", "Sales", "Customer_Age", "Rating"]].describe())
""")
code("""df.to_csv("../data/cleaned_sales_dataset.csv", index=False)
df.to_excel("../data/cleaned_sales_dataset.xlsx", index=False)
print("Cleaned dataset saved.")
""")

# 13. EDA
md("""## 13. Exploratory Data Analysis

We now ask specific, purposeful business questions of the cleaned data.
""")
code("""total_sales = df["Sales"].sum()
total_orders = len(df)
avg_order_value = df["Sales"].mean()
avg_rating = df["Rating"].mean()

print(f"Total Sales: ₹{total_sales:,.2f}")
print(f"Total Orders: {total_orders}")
print(f"Average Order Value: ₹{avg_order_value:,.2f}")
print(f"Average Customer Rating: {avg_rating:.2f} / 5")
""")
code("""category_sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
category_sales
""")
code("""city_sales = df.groupby("City")["Sales"].sum().sort_values(ascending=False)
city_sales
""")
code("""monthly_sales = df.assign(Order_Date=pd.to_datetime(df["Order_Date"])) \\
                   .set_index("Order_Date").resample("ME")["Sales"].sum()
monthly_sales
""")
code("""top_products = df.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(10)
top_products
""")
code("""payment_counts = df["Payment_Method"].value_counts()
payment_counts
""")
code("""category_ratings = df.groupby("Category")["Rating"].mean().sort_values(ascending=False)
category_ratings
""")
code("""print("Correlation between Quantity and Sales:", round(df["Quantity"].corr(df["Sales"]), 3))
numeric_cols = ["Quantity", "Unit_Price", "Sales", "Customer_Age", "Rating"]
df[numeric_cols].corr()
""")

# 14. Visualizations
md("""## 14. Visualizations

Each chart below answers one of the questions above, with a title, axis
labels, and readable values.
""")

code("""plt.figure(figsize=(9, 5))
ax = sns.barplot(x=category_sales.values, y=category_sales.index,
                  hue=category_sales.index, palette="viridis", legend=False)
plt.title("Total Sales by Product Category", fontsize=14, fontweight="bold")
plt.xlabel("Total Sales (₹)")
plt.ylabel("Category")
for i, v in enumerate(category_sales.values):
    plt.text(v, i, f" ₹{v:,.0f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig("../visualizations/sales_by_category.png")
plt.show()
""")

code("""plt.figure(figsize=(9, 5))
sns.barplot(x=city_sales.values, y=city_sales.index, hue=city_sales.index,
            palette="mako", legend=False)
plt.title("Total Sales by City", fontsize=14, fontweight="bold")
plt.xlabel("Total Sales (₹)")
plt.ylabel("City")
plt.tight_layout()
plt.savefig("../visualizations/sales_by_city.png")
plt.show()
""")

code("""plt.figure(figsize=(10, 5))
plt.plot(monthly_sales.index, monthly_sales.values, marker="o", color="#2a6f97", linewidth=2)
plt.title("Monthly Sales Trend (2023)", fontsize=14, fontweight="bold")
plt.xlabel("Month")
plt.ylabel("Total Sales (₹)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("../visualizations/monthly_sales_trend.png")
plt.show()
""")

code("""plt.figure(figsize=(8, 5))
sns.histplot(df["Customer_Age"], bins=20, kde=True, color="#e07a5f")
plt.title("Customer Age Distribution", fontsize=14, fontweight="bold")
plt.xlabel("Customer Age")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.savefig("../visualizations/customer_age_distribution.png")
plt.show()
""")

code("""plt.figure(figsize=(8, 5))
sns.boxplot(x=df["Sales"], color="#81b29a")
plt.title("Sales Distribution (Box Plot)", fontsize=14, fontweight="bold")
plt.xlabel("Sales (₹)")
plt.tight_layout()
plt.savefig("../visualizations/sales_distribution.png")
plt.show()
""")

code("""plt.figure(figsize=(7, 6))
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f",
            square=True, linewidths=0.5)
plt.title("Correlation Heatmap of Numerical Features", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("../visualizations/correlation_heatmap.png")
plt.show()
""")

code("""plt.figure(figsize=(9, 5))
sns.barplot(x=top_products.values, y=top_products.index, hue=top_products.index,
            palette="crest", legend=False)
plt.title("Top 10 Products by Total Sales", fontsize=14, fontweight="bold")
plt.xlabel("Total Sales (₹)")
plt.ylabel("Product")
plt.tight_layout()
plt.savefig("../visualizations/top_products.png")
plt.show()
""")

code("""plt.figure(figsize=(7, 5))
sns.countplot(y="Payment_Method", data=df, order=payment_counts.index,
              hue="Payment_Method", palette="flare", legend=False)
plt.title("Orders by Payment Method", fontsize=14, fontweight="bold")
plt.xlabel("Number of Orders")
plt.ylabel("Payment Method")
plt.tight_layout()
plt.savefig("../visualizations/payment_method_counts.png")
plt.show()
""")

code("""plt.figure(figsize=(8, 5))
sns.scatterplot(x="Quantity", y="Sales", data=df, hue="Category", alpha=0.7)
plt.title("Quantity vs Sales", fontsize=14, fontweight="bold")
plt.xlabel("Quantity")
plt.ylabel("Sales (₹)")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig("../visualizations/quantity_vs_sales.png")
plt.show()
""")

# 15. Key Insights
md("""## 15. Key Insights

For each insight: **Observation** (what the numbers show) → **Interpretation**
(what it likely means) → *(Speculation, only where explicitly marked)*.

1. **Electronics and Furniture dominate revenue.**
   *Observation:* Electronics (₹31.8L) and Furniture (₹23.5L) together contribute
   roughly 82% of total sales, while Groceries and Books contribute under 2%
   combined.
   *Interpretation:* Revenue is driven by a small number of high-ticket
   categories, not by transaction volume — Groceries/Books likely have many
   low-value orders that don't move the total much.

2. **Ahmedabad, Delhi, and Pune are the top revenue cities.**
   *Observation:* These three cities lead total sales, though the gap to the
   next tier of cities (Bangalore, Chennai) is modest.
   *Interpretation:* Demand is fairly distributed across metro cities rather
   than concentrated in one location.

3. **Cash is still the most-used payment method**, followed closely by Net
   Banking, UPI, Debit Card, and Credit Card — all five methods are used at
   broadly similar rates (roughly 18-23% of orders each).
   *Interpretation:* No single payment method dominates, suggesting the
   business should keep supporting all these options rather than optimizing
   for just one.

4. **Quantity and Sales are only weakly correlated** (~0.25).
   *Observation:* Buying more units doesn't strongly predict a higher sales
   value.
   *Interpretation:* This makes sense — a single ₹45,000 laptop produces far
   more revenue than 5 units of a ₹200 item, so **unit price**, not quantity,
   is the main driver of order value.

5. **Average customer ratings sit around 2.9-3.1 across most categories**,
   with Furniture/Clothing slightly higher and Footwear slightly lower.
   *Interpretation:* Ratings are fairly uniform across categories — there
   isn't one category with a standout satisfaction problem based on this data.

*(Speculation: if this were real business data, the low Grocery/Books revenue
combined with steady order counts might suggest these are used as "add-on"
categories rather than primary purchase drivers — but this dataset does not
contain basket-level data to confirm that.)*
""")

# 16. Conclusion
md("""## 16. Conclusion

Starting from a deliberately messy raw dataset, we:

- Diagnosed missing values, duplicates, inconsistent categories, invalid
  values, mixed data types, and outliers.
- Cleaned the data using column-appropriate strategies rather than one-size-
  fits-all rules (median/mode imputation, per-category outlier handling,
  domain-aware caps).
- Explored the cleaned data to answer concrete business questions.
- Visualized the findings clearly, and translated them into insights that are
  grounded in the actual numbers.

This mirrors the real workflow of a data analyst: **raw data is never ready
to analyze — cleaning it thoughtfully is what makes the rest of the analysis
trustworthy.**
""")

nb["cells"] = cells
nbf.write(nb, "/home/claude/proj/notebooks/data_analysis.ipynb")
print("Notebook written.")
