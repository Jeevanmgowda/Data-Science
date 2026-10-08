import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110

df = pd.read_csv("/home/claude/proj/data/cleaned_sales_dataset.csv")
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
OUT = "/home/claude/proj/visualizations"

# 1. Sales by Category (bar chart)
plt.figure(figsize=(9, 5))
cat_sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
ax = sns.barplot(x=cat_sales.values, y=cat_sales.index, hue=cat_sales.index,
                  palette="viridis", legend=False)
plt.title("Total Sales by Product Category", fontsize=14, fontweight="bold")
plt.xlabel("Total Sales (₹)")
plt.ylabel("Category")
for i, v in enumerate(cat_sales.values):
    plt.text(v, i, f" ₹{v:,.0f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUT}/sales_by_category.png")
plt.close()

# 2. Sales by City (bar chart)
plt.figure(figsize=(9, 5))
city_sales = df.groupby("City")["Sales"].sum().sort_values(ascending=False)
sns.barplot(x=city_sales.values, y=city_sales.index, hue=city_sales.index,
            palette="mako", legend=False)
plt.title("Total Sales by City", fontsize=14, fontweight="bold")
plt.xlabel("Total Sales (₹)")
plt.ylabel("City")
plt.tight_layout()
plt.savefig(f"{OUT}/sales_by_city.png")
plt.close()

# 3. Monthly Sales Trend (line chart)
plt.figure(figsize=(10, 5))
monthly = df.set_index("Order_Date").resample("ME")["Sales"].sum()
plt.plot(monthly.index, monthly.values, marker="o", color="#2a6f97", linewidth=2)
plt.title("Monthly Sales Trend (2023)", fontsize=14, fontweight="bold")
plt.xlabel("Month")
plt.ylabel("Total Sales (₹)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUT}/monthly_sales_trend.png")
plt.close()

# 4. Customer Age Distribution (histogram)
plt.figure(figsize=(8, 5))
sns.histplot(df["Customer_Age"], bins=20, kde=True, color="#e07a5f")
plt.title("Customer Age Distribution", fontsize=14, fontweight="bold")
plt.xlabel("Customer Age")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.savefig(f"{OUT}/customer_age_distribution.png")
plt.close()

# 5. Sales Distribution (box plot, to show spread/outliers post-cleaning)
plt.figure(figsize=(8, 5))
sns.boxplot(x=df["Sales"], color="#81b29a")
plt.title("Sales Distribution (Box Plot)", fontsize=14, fontweight="bold")
plt.xlabel("Sales (₹)")
plt.tight_layout()
plt.savefig(f"{OUT}/sales_distribution.png")
plt.close()

# 6. Correlation Heatmap
plt.figure(figsize=(7, 6))
num_cols = ["Quantity", "Unit_Price", "Sales", "Customer_Age", "Rating"]
corr = df[num_cols].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True, linewidths=0.5)
plt.title("Correlation Heatmap of Numerical Features", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/correlation_heatmap.png")
plt.close()

# 7. Top Products (bar chart) - extra useful chart
plt.figure(figsize=(9, 5))
top_products = df.groupby("Product")["Sales"].sum().sort_values(ascending=False).head(10)
sns.barplot(x=top_products.values, y=top_products.index, hue=top_products.index,
            palette="crest", legend=False)
plt.title("Top 10 Products by Total Sales", fontsize=14, fontweight="bold")
plt.xlabel("Total Sales (₹)")
plt.ylabel("Product")
plt.tight_layout()
plt.savefig(f"{OUT}/top_products.png")
plt.close()

# 8. Payment Method count plot
plt.figure(figsize=(7, 5))
sns.countplot(y="Payment_Method", data=df,
              order=df["Payment_Method"].value_counts().index,
              hue="Payment_Method", palette="flare", legend=False)
plt.title("Orders by Payment Method", fontsize=14, fontweight="bold")
plt.xlabel("Number of Orders")
plt.ylabel("Payment Method")
plt.tight_layout()
plt.savefig(f"{OUT}/payment_method_counts.png")
plt.close()

# 9. Quantity vs Sales scatter
plt.figure(figsize=(8, 5))
sns.scatterplot(x="Quantity", y="Sales", data=df, hue="Category", alpha=0.7)
plt.title("Quantity vs Sales", fontsize=14, fontweight="bold")
plt.xlabel("Quantity")
plt.ylabel("Sales (₹)")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(f"{OUT}/quantity_vs_sales.png")
plt.close()

print("All visualizations saved to", OUT)
