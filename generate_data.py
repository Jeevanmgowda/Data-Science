"""
Generates a realistic, intentionally messy retail sales dataset for a
Data Cleaning & Visualization internship project.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N = 850  # base number of "clean" rows before we inject duplicates

cities_clean = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
                "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]

# messy variants we will sprinkle in for a subset of rows
city_variants = {
    "Delhi": ["Delhi", "delhi", "DELHI", "Delhi "],
    "Mumbai": ["Mumbai", "mumbai", "MUMBAI"],
    "Bangalore": ["Bangalore", "bangalore", "Bengaluru"],
    "Chennai": ["Chennai", "chennai", "CHENNAI"],
}

categories_clean = ["Electronics", "Clothing", "Furniture", "Groceries",
                     "Footwear", "Books", "Toys", "Beauty"]

category_variants = {
    "Electronics": ["Electronics", "electronics", "ELECTRONICS"],
    "Clothing": ["Clothing", "clothing", "Cloths"],
    "Footwear": ["Footwear", "footwear", "Foot Wear"],
}

products_by_category = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Smartwatch", "Tablet", "Bluetooth Speaker"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Kurta", "Dress"],
    "Furniture": ["Office Chair", "Dining Table", "Bookshelf", "Sofa", "Bed Frame"],
    "Groceries": ["Rice 5kg", "Cooking Oil 1L", "Wheat Flour 5kg", "Tea Pack", "Sugar 1kg"],
    "Footwear": ["Running Shoes", "Sandals", "Formal Shoes", "Sneakers"],
    "Books": ["Novel", "Textbook", "Comic Book", "Notebook Set"],
    "Toys": ["Action Figure", "Puzzle Set", "Remote Car", "Building Blocks"],
    "Beauty": ["Face Cream", "Shampoo", "Perfume", "Lipstick"],
}

unit_price_range = {
    "Smartphone": (8000, 45000), "Laptop": (25000, 90000), "Headphones": (500, 4000),
    "Smartwatch": (1500, 12000), "Tablet": (9000, 35000), "Bluetooth Speaker": (800, 5000),
    "T-Shirt": (250, 1200), "Jeans": (700, 2500), "Jacket": (1000, 4500), "Kurta": (500, 2000),
    "Dress": (600, 3000), "Office Chair": (2500, 12000), "Dining Table": (5000, 25000),
    "Bookshelf": (1500, 8000), "Sofa": (8000, 40000), "Bed Frame": (6000, 30000),
    "Rice 5kg": (250, 500), "Cooking Oil 1L": (120, 220), "Wheat Flour 5kg": (180, 350),
    "Tea Pack": (100, 400), "Sugar 1kg": (40, 70), "Running Shoes": (900, 5000),
    "Sandals": (300, 1500), "Formal Shoes": (1200, 6000), "Sneakers": (800, 4500),
    "Novel": (150, 600), "Textbook": (300, 1500), "Comic Book": (80, 300),
    "Notebook Set": (100, 400), "Action Figure": (300, 1500), "Puzzle Set": (200, 900),
    "Remote Car": (600, 3000), "Building Blocks": (400, 2500), "Face Cream": (150, 900),
    "Shampoo": (120, 700), "Perfume": (500, 3500), "Lipstick": (200, 1200),
}

first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
               "Ishaan", "Rohan", "Ananya", "Diya", "Priya", "Isha", "Aadhya", "Kavya",
               "Meera", "Sneha", "Riya", "Neha", "Rahul", "Amit", "Sanjay", "Pooja", "Anjali"]
last_names = ["Sharma", "Verma", "Gupta", "Kumar", "Singh", "Reddy", "Nair", "Iyer",
              "Patel", "Mehta", "Rao", "Das", "Chatterjee", "Joshi", "Bose"]

payment_methods_clean = ["Credit Card", "Debit Card", "UPI", "Cash", "Net Banking"]
payment_variants = ["Credit Card", "credit card", "UPI", "upi", "Cash", "CASH",
                     "Debit Card", "Net Banking"]

start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
date_range_days = (end_date - start_date).days

rows = []
for i in range(1, N + 1):
    category = np.random.choice(categories_clean)
    product = np.random.choice(products_by_category[category])
    lo, hi = unit_price_range[product]
    unit_price = round(np.random.uniform(lo, hi), 2)
    quantity = np.random.choice([1, 1, 1, 2, 2, 3, 4, 5], p=[0.30, 0.15, 0.15, 0.15, 0.1, 0.05, 0.05, 0.05])
    sales = round(unit_price * quantity, 2)

    order_date = start_date + timedelta(days=int(np.random.randint(0, date_range_days + 1)))
    customer_name = f"{np.random.choice(first_names)} {np.random.choice(last_names)}"

    base_city = np.random.choice(cities_clean)
    city = base_city
    if base_city in city_variants and np.random.rand() < 0.12:
        city = np.random.choice(city_variants[base_city])

    cat_display = category
    if category in category_variants and np.random.rand() < 0.10:
        cat_display = np.random.choice(category_variants[category])

    payment = np.random.choice(payment_methods_clean)
    if np.random.rand() < 0.10:
        payment = np.random.choice(payment_variants)

    age = int(np.random.normal(35, 11))
    age = max(18, min(70, age))

    rating = round(np.random.uniform(1, 5), 1)

    rows.append({
        "Order_ID": f"ORD{1000 + i}",
        "Order_Date": order_date.strftime("%Y-%m-%d"),
        "Customer_Name": customer_name,
        "City": city,
        "Product": product,
        "Category": cat_display,
        "Quantity": quantity,
        "Unit_Price": unit_price,
        "Sales": sales,
        "Payment_Method": payment,
        "Customer_Age": age,
        "Rating": rating,
    })

df = pd.DataFrame(rows)

# ---------------------------------------------------------------
# Intentionally inject data-quality problems
# ---------------------------------------------------------------
rng = np.random.default_rng(7)

# 1. Missing values in several columns (different missingness patterns)
for col, frac in [("Customer_Age", 0.06), ("Rating", 0.05), ("City", 0.03),
                   ("Payment_Method", 0.03), ("Unit_Price", 0.02)]:
    idx = rng.choice(df.index, size=int(len(df) * frac), replace=False)
    df.loc[idx, col] = np.nan

# 2. Duplicate rows (exact duplicates of existing rows appended)
dup_idx = rng.choice(df.index, size=40, replace=False)
duplicates = df.loc[dup_idx].copy()
df = pd.concat([df, duplicates], ignore_index=True)

# 3. Numerical outliers - a few extreme Sales / Unit_Price / Quantity values
outlier_idx = rng.choice(df.index, size=8, replace=False)
for j, idx in enumerate(outlier_idx):
    if j % 3 == 0:
        df.loc[idx, "Quantity"] = int(rng.integers(50, 100))
        df.loc[idx, "Sales"] = round(df.loc[idx, "Unit_Price"] * df.loc[idx, "Quantity"], 2)
    elif j % 3 == 1:
        df.loc[idx, "Unit_Price"] = df.loc[idx, "Unit_Price"] * rng.uniform(15, 25)
        df.loc[idx, "Sales"] = round(df.loc[idx, "Unit_Price"] * df.loc[idx, "Quantity"], 2)
    else:
        df.loc[idx, "Customer_Age"] = int(rng.choice([2, 3, 95, 99]))

# 4. A few invalid / suspicious values
neg_idx = rng.choice(df.index, size=4, replace=False)
df.loc[neg_idx, "Quantity"] = -abs(df.loc[neg_idx, "Quantity"])

bad_rating_idx = rng.choice(df.index, size=3, replace=False)
df.loc[bad_rating_idx, "Rating"] = rng.choice([0, 6, 7.5])

# 5. Mixed / inconsistent data types (Quantity or Unit_Price stored as text with noise)
mixed_idx = rng.choice(df.index, size=6, replace=False)
df["Quantity"] = df["Quantity"].astype(object)
for idx in mixed_idx:
    df.loc[idx, "Quantity"] = f"{df.loc[idx, 'Quantity']} units"

# Unit_Price with currency symbol / stray whitespace for a few rows
price_str_idx = rng.choice(df.index, size=6, replace=False)
df["Unit_Price"] = df["Unit_Price"].astype(object)
for idx in price_str_idx:
    df.loc[idx, "Unit_Price"] = f"₹{df.loc[idx, 'Unit_Price']}"

# 6. Whitespace / capitalization noise in Customer_Name
name_noise_idx = rng.choice(df.index, size=10, replace=False)
for idx in name_noise_idx:
    df.loc[idx, "Customer_Name"] = f"  {df.loc[idx, 'Customer_Name'].upper()}  "

# 7. Inconsistent Order_Date formats for a handful of rows (string mismatch)
date_fmt_idx = rng.choice(df.index, size=8, replace=False)
for idx in date_fmt_idx:
    d = datetime.strptime(df.loc[idx, "Order_Date"], "%Y-%m-%d")
    df.loc[idx, "Order_Date"] = d.strftime("%d/%m/%Y")

# Shuffle rows so duplicates aren't all at the bottom
df = df.sample(frac=1, random_state=1).reset_index(drop=True)

# Re-generate Order_ID uniqueness note: keep duplicate rows with same Order_ID (real dup rows)
df.to_csv("/home/claude/proj/data/raw_sales_dataset.csv", index=False)
df.to_excel("/home/claude/proj/data/raw_sales_dataset.xlsx", index=False)

print("Raw dataset shape:", df.shape)
print(df.dtypes)
print(df.isna().sum())
