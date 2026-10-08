"""
Cleans data/raw_sales_dataset.csv and writes data/cleaned_sales_dataset.csv/.xlsx
This same logic is reproduced (with explanations) inside the Jupyter notebook.
"""
import numpy as np
import pandas as pd

RAW_PATH = "/home/claude/proj/data/raw_sales_dataset.csv"
df = pd.read_csv(RAW_PATH)

print("BEFORE CLEANING:", df.shape)

# --- 1. Fix Customer_Name whitespace/casing ---
df["Customer_Name"] = df["Customer_Name"].str.strip().str.title()

# --- 2. Standardize City (strip, title case, fix known alias) ---
df["City"] = df["City"].str.strip().str.title()
df["City"] = df["City"].replace({"Bengaluru": "Bangalore"})

# --- 3. Standardize Category ---
df["Category"] = df["Category"].str.strip().str.title()
df["Category"] = df["Category"].replace({"Cloths": "Clothing", "Foot Wear": "Footwear"})

# --- 4. Standardize Payment_Method casing ---
df["Payment_Method"] = df["Payment_Method"].str.strip().str.title()
df["Payment_Method"] = df["Payment_Method"].replace({"Upi": "UPI"})

# --- 5. Clean Unit_Price: remove currency symbols, convert to numeric ---
df["Unit_Price"] = (
    df["Unit_Price"].astype(str).str.replace("₹", "", regex=False).str.strip()
)
df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce")

# --- 6. Clean Quantity: remove text like "units", convert to numeric ---
df["Quantity"] = (
    df["Quantity"].astype(str).str.extract(r"(-?\d+)").astype(float)
)

# --- 7. Fix negative Quantity (data entry sign error -> take absolute value) ---
df.loc[df["Quantity"] < 0, "Quantity"] = df.loc[df["Quantity"] < 0, "Quantity"].abs()

# --- 8. Standardize Order_Date to a single format ---
def parse_date(val):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["Order_Date"] = df["Order_Date"].apply(parse_date)

# --- 9. Fix invalid Rating values (valid range is 1-5) ---
df.loc[(df["Rating"] < 1) | (df["Rating"] > 5), "Rating"] = np.nan

# --- 10. Recompute Sales consistently as Quantity * Unit_Price where both are known ---
recalculated = df["Quantity"] * df["Unit_Price"]
mismatch = (df["Sales"] - recalculated).abs() > 1
print("Rows where stored Sales did not match Quantity*Unit_Price:", mismatch.sum())
df["Sales"] = recalculated.round(2)

# --- 11. Handle missing values (column-appropriate strategy) ---
# Customer_Age: numeric, roughly symmetric -> fill with median
df["Customer_Age"] = df["Customer_Age"].fillna(df["Customer_Age"].median())
# Rating: numeric, ordinal 1-5 -> fill with median
df["Rating"] = df["Rating"].fillna(df["Rating"].median())
# City / Payment_Method: categorical -> fill with mode (most frequent value)
df["City"] = df["City"].fillna(df["City"].mode()[0])
df["Payment_Method"] = df["Payment_Method"].fillna(df["Payment_Method"].mode()[0])
# Unit_Price: recompute from Sales/Quantity where possible, else median
mask_missing_price = df["Unit_Price"].isna() & df["Quantity"].notna() & (df["Quantity"] != 0)
df.loc[mask_missing_price, "Unit_Price"] = (
    df.loc[mask_missing_price, "Sales"] / df.loc[mask_missing_price, "Quantity"]
)
df["Unit_Price"] = df["Unit_Price"].fillna(df["Unit_Price"].median())
# Recompute Sales again for the rows we just repaired
df["Sales"] = (df["Quantity"] * df["Unit_Price"]).round(2)
# Order_Date: drop rows where date could not be parsed at all (very few, if any)
df = df.dropna(subset=["Order_Date"])

# --- 12. Remove duplicate rows ---
before_dedup = len(df)
df = df.drop_duplicates()
print("Duplicate rows removed:", before_dedup - len(df))

# --- 13. Outlier handling using IQR ---
# NOTE: Unit_Price and Sales naturally span very different ranges across categories
# (e.g. Groceries vs Electronics), so a single global IQR would wrongly flag thousands
# of genuine premium-category sales as outliers. We instead compute IQR bounds
# PER CATEGORY for Sales/Unit_Price, and a global IQR for Quantity and Customer_Age,
# which are not category-scale-dependent.
def iqr_bounds(series, k=1.5):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

# Quantity: the statistical IQR bound (~3.5) flags even normal bulk purchases of 4-5
# units, which are still realistic retail quantities, not data errors. So instead of
# blindly capping at the IQR bound, we only treat CLEARLY implausible values (an
# injected data-entry error of 50-100 units in a single order) as outliers to cap,
# and keep normal 1-5 unit orders untouched.
low_q, high_q = iqr_bounds(df["Quantity"])
flagged_qty_iqr = ((df["Quantity"] < low_q) | (df["Quantity"] > high_q)).sum()
print(f"Quantity IQR bounds (statistical, not all applied): low={low_q:.2f}, high={high_q:.2f}, flagged={flagged_qty_iqr}")
DOMAIN_MAX_QTY = 10
genuine_outliers = (df["Quantity"] > DOMAIN_MAX_QTY).sum()
print(f"Quantity values above domain-reasonable max ({DOMAIN_MAX_QTY}) treated as data errors: {genuine_outliers}")
df["Quantity"] = df["Quantity"].clip(lower=1, upper=DOMAIN_MAX_QTY)

# Customer_Age: ages like 2, 3, 95, 99 are implausible for a retail customer
low_a, high_a = iqr_bounds(df["Customer_Age"])
flagged_age = ((df["Customer_Age"] < low_a) | (df["Customer_Age"] > high_a)).sum()
print(f"Customer_Age IQR bounds: low={low_a:.2f}, high={high_a:.2f}, flagged={flagged_age}")
df["Customer_Age"] = df["Customer_Age"].clip(lower=16, upper=85)

# Unit_Price: flag within each category separately, only cap genuinely extreme
# values (an injected data-entry error, e.g. price x15-25), not normal premium items.
def flag_and_cap_per_category(frame, col):
    capped = frame.copy()
    total_flagged = 0
    for cat, group in frame.groupby("Category"):
        low, high = iqr_bounds(group[col])
        # Use a wider multiplier (k=3) so only extreme data-entry errors are capped,
        # not the normal spread of prices within a category.
        q1, q3 = group[col].quantile(0.25), group[col].quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - 3 * iqr, q3 + 3 * iqr
        mask = (group[col] < low) | (group[col] > high)
        total_flagged += mask.sum()
        capped.loc[group.index, col] = group[col].clip(lower=max(low, 0), upper=high)
    print(f"{col} per-category IQR (k=3) flagged/capped: {total_flagged}")
    return capped

df = flag_and_cap_per_category(df, "Unit_Price")

df["Sales"] = (df["Quantity"] * df["Unit_Price"]).round(2)

# --- 14. Final dtype cleanup ---
df["Quantity"] = df["Quantity"].round().astype(int)
df["Customer_Age"] = df["Customer_Age"].round().astype(int)
df["Order_Date"] = pd.to_datetime(df["Order_Date"]).dt.strftime("%Y-%m-%d")

df = df.reset_index(drop=True)

print("AFTER CLEANING:", df.shape)
print(df.isna().sum())

df.to_csv("/home/claude/proj/data/cleaned_sales_dataset.csv", index=False)
df.to_excel("/home/claude/proj/data/cleaned_sales_dataset.xlsx", index=False)
print("Saved cleaned dataset.")
