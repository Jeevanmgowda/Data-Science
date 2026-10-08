# Data Cleaning & Visualization Project — Retail Sales Analysis

A beginner-friendly, end-to-end data analytics project: a raw, intentionally
messy retail sales dataset is cleaned, explored, visualized, and turned into
an interactive dashboard.

## Overview

This project simulates a real internship task: you're handed a raw dataset
full of the usual problems (missing values, duplicates, inconsistent text,
outliers, mixed data types) and asked to clean it, analyze it, and present
findings. Every step — cleaning, EDA, visualization, and storytelling — is
done here with actual code and actual results (nothing is invented).

## Objective

- Practice systematic data cleaning with Pandas/NumPy.
- Perform purposeful Exploratory Data Analysis (EDA).
- Build clear, well-labeled visualizations with Matplotlib/Seaborn.
- Communicate findings as data-backed insights.
- Package the analysis into an interactive Streamlit + Plotly dashboard.

## Dataset Description

A synthetic retail sales dataset (`data/raw_sales_dataset.csv`) with **890
rows** and **12 columns**, generated to resemble a real point-of-sale export.

### Columns

| Column | Description |
|---|---|
| Order_ID | Unique order identifier |
| Order_Date | Date the order was placed |
| Customer_Name | Customer's full name |
| City | City the order was placed from |
| Product | Product name |
| Category | Product category |
| Quantity | Units purchased |
| Unit_Price | Price per unit (₹) |
| Sales | Total sale value (Quantity × Unit_Price) |
| Payment_Method | How the order was paid for |
| Customer_Age | Customer's age |
| Rating | Customer's rating of the order (1-5) |

### Problems intentionally present in the raw data

- **Missing values** in `City`, `Payment_Method`, `Customer_Age`, `Rating`, `Unit_Price`
- **~40 duplicate rows**
- **Inconsistent capitalization / aliases**: `Delhi` / `delhi` / `DELHI`, `Bengaluru` vs `Bangalore`, `Cloths` vs `Clothing`
- **Mixed data types**: `Quantity` values like `"3 units"`, `Unit_Price` values like `"₹1200.5"`
- **Invalid values**: negative `Quantity`, `Rating` values outside the 1-5 range
- **Numerical outliers**: a handful of implausible `Quantity` (50-100 units), inflated `Unit_Price`, and implausible `Customer_Age` (2, 3, 95, 99)
- **Inconsistent date formats**: a mix of `YYYY-MM-DD` and `DD/MM/YYYY`
- **Whitespace/casing noise** in `Customer_Name`

## Cleaning Process

Implemented in `notebooks/data_analysis.ipynb` (section 11) and mirrored in
`clean_data.py`:

1. Standardize text columns (trim whitespace, consistent casing, fix aliases).
2. Fix data types (strip currency symbols/text noise, convert to numeric).
3. Fix invalid values (absolute value for negative quantities, drop out-of-range ratings).
4. Standardize date formats.
5. Recompute `Sales` consistently as `Quantity × Unit_Price`.
6. Handle missing values with **column-appropriate strategies** — median for
   numeric columns, mode for categorical columns, recomputation where
   possible — never a blanket fill with zero.
7. Remove exact duplicate rows.
8. Handle outliers using the **IQR method**, applied thoughtfully:
   - `Quantity`: a domain-based cap (10 units) rather than a strict statistical
     bound, since normal bulk orders of 4-5 units shouldn't be treated as errors.
   - `Customer_Age`: clipped to a realistic 16-85 range.
   - `Unit_Price`: outliers are checked **per category** (a global rule would
     wrongly flag most Electronics/Furniture sales), with only extreme,
     data-entry-error-like values capped.

## Exploratory Data Analysis

Questions answered in the notebook (section 13): total sales, top categories
and cities, monthly sales trend, best-selling products, payment method mix,
customer age distribution, category-level ratings, and the relationship
between quantity, price, and sales.

## Visualizations

Saved in `visualizations/`:

- `sales_by_category.png` — bar chart
- `sales_by_city.png` — bar chart
- `monthly_sales_trend.png` — line chart
- `customer_age_distribution.png` — histogram
- `sales_distribution.png` — box plot
- `correlation_heatmap.png` — heatmap
- `top_products.png` — bar chart
- `payment_method_counts.png` — count plot
- `quantity_vs_sales.png` — scatter plot

## Key Findings

- **Electronics and Furniture drive ~82% of total revenue**, despite not being
  the highest-volume categories — high unit price matters more than order count.
- **Ahmedabad, Delhi, and Pune are the top revenue cities**, with demand fairly
  spread across metro cities rather than concentrated in one.
- **All five payment methods are used at similar rates** (18-23% of orders each) — no single method dominates.
- **Quantity and Sales are only weakly correlated (~0.25)** — unit price, not
  order size, is the main driver of a sale's value.
- **Average ratings are fairly consistent across categories (~2.8-3.1 / 5)** —
  no single category stands out as a satisfaction outlier.

Full reasoning (observation → interpretation) is in the notebook's "Key
Insights" section.

## Dashboard

An interactive Streamlit + Plotly dashboard (`dashboard/app.py`) showing:

- KPIs: Total Sales, Total Orders, Average Order Value, Average Rating
- Sales by Category / City
- Monthly Sales Trend
- Top Products
- Payment Method breakdown
- Customer Age Distribution
- Filters: City, Category, Payment Method, Order Date range

## Technologies Used

Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly, Streamlit, Jupyter, openpyxl.

## Project Structure

```
Data-Cleaning-Visualization-Project/
│
├── data/
│   ├── raw_sales_dataset.csv
│   ├── raw_sales_dataset.xlsx
│   ├── cleaned_sales_dataset.csv
│   └── cleaned_sales_dataset.xlsx
│
├── notebooks/
│   └── data_analysis.ipynb
│
├── visualizations/
│   ├── sales_by_category.png
│   ├── sales_by_city.png
│   ├── monthly_sales_trend.png
│   ├── customer_age_distribution.png
│   ├── sales_distribution.png
│   ├── correlation_heatmap.png
│   ├── top_products.png
│   ├── payment_method_counts.png
│   └── quantity_vs_sales.png
│
├── dashboard/
│   └── app.py
│
├── generate_data.py        # creates the raw dataset
├── clean_data.py            # standalone cleaning script
├── README.md
├── LEARNING_GUIDE.md
├── INTERVIEW_NOTES.md
└── requirements.txt
```

## Installation Steps

```bash
# 1. Extract the project and open it in VS Code, then in a terminal:
cd Data-Cleaning-Visualization-Project

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## How to Run the Notebook

```bash
jupyter notebook notebooks/data_analysis.ipynb
```
Run all cells from top to bottom (`Kernel → Restart & Run All`). It reads the
raw dataset, cleans it, saves the cleaned dataset, and produces every chart.

## How to Run the Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```
This opens the dashboard in your browser (default: `http://localhost:8501`),
using the already-cleaned dataset in `data/cleaned_sales_dataset.csv`.

## Conclusion

This project demonstrates the full data analyst workflow on a realistic,
messy dataset: diagnosing data-quality issues, cleaning them with justified
(not blanket) methods, exploring the clean data purposefully, visualizing it
clearly, and telling a data-backed story — packaged into a portfolio-ready
repository with an interactive dashboard.
