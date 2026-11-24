# 💊 Pharmacy Medication Sales Dashboard with Streamlit

🚀 **Live App:** [pharmacy-sales-dashboard.streamlit.app](https://pharmacy-sales-dashboard.streamlit.app/)

## 📌 Project Overview

This project is an interactive dashboard built in Python and Streamlit to analyze pharmacy medication sales. It uses 400 sales from January to April 2025 across 10 medications, with medication, category, dosage form, quantity, unit price, payment method, date, and total price.

The base dashboard ranks the most dispensed medications and filters them by category. I then expanded it to answer the questions a pharmacy manager would actually ask: where the revenue comes from, how sales change week to week, and which medications are about to run out. I added KPI cards, revenue and payment charts, date and payment filters, a working low-stock alert system, and CSV export. I also audited the data for clinical plausibility and found that **84% of sales list the medication under the wrong drug category**.

## 🎯 Key Features

✅ KPI Summary: Shows total revenue, units dispensed, transactions, and average sale, updating with every filter.<br>
✅ Most Dispensed Medications: Ranks medications by units sold, colored by therapeutic class.<br>
✅ Revenue by Medication: Compares how much each drug brings in, not just how many units it sells.<br>
✅ Payment Method Mix: Shows the share of revenue paid by cash, card, and insurance in a donut chart.<br>
✅ Weekly Revenue Trend: Plots revenue week by week across the four months.<br>
✅ Dosage Form Breakdown: Compares units sold as tablets, capsules, syrup, and injections.<br>
✅ Inventory and Low-Stock Alerts: Simulates current stock, days of supply, and color-coded alerts with an adjustable threshold.<br>
✅ Corrected Therapeutic Classes: Groups each drug by its real class, with a toggle to switch back to the original categories.<br>
✅ Data Quality Tab: Shows category mismatches in a heatmap and flags dosage forms that do not exist.<br>
✅ Interactive Filters: Filters by category, date range, and payment method.<br>
✅ Data Export: Lets users download the filtered records as a CSV.

## 🗂️ Repository Files

| File | Description |
|------|-------------|
| `app.py` | Streamlit app that builds the interactive dashboard |
| `pharmacy_sales.csv` | Raw dataset: 400 rows and 9 columns of pharmacy sales records |
| `requirements.txt` | Packages used to deploy the app |

## 🧹 Data Preparation

- Loaded the data with `pd.read_csv()` using a relative file path, so the app runs on any computer and on Streamlit Cloud.
- Confirmed the dataset has no missing values and that total price always equals quantity times unit price.
- Converted `date` to a datetime column with `pd.to_datetime()`.
- Added a `therapeutic_class` column that assigns each drug its correct class from the medication name.
- Flagged injection sales of drugs that are only made as oral products.
- **Fixed the inventory calculation.** The original version subtracted each drug's sales from a starting stock of 500 units, but every drug sold 712 to 1,181 units, so every stock level came out negative. The dashboard now uses an adjustable starting stock (default 1,500 units) and adds days of supply.
- **Flagged a clinical plausibility issue.** Only 63 of 400 sales (15.8%) list the correct category. Metformin, a diabetes drug, appears under all six categories. With six categories, random assignment would match about 16.7% of the time, so the category column appears to be random. Each drug's unit price also ranges from about $3 to $50 regardless of drug or form. Both point to synthetic practice data, so category-level results should be read as a demonstration of the method, not as real pharmacy findings.

## 🛠️ Skills & Tools Applied

- Language and Environment: Python, Visual Studio Code
- Libraries: pandas, Plotly Express, Streamlit
- Analysis: Grouping and aggregation, weekly resampling, inventory simulation, days-of-supply calculation
- Visualization: Bar, horizontal bar, line, donut, and heatmap charts
- App Development: Sidebar filters, KPI metrics, tabs, multi-column layout, CSV download
- Deployment: GitHub and Streamlit Community Cloud
- Clinical Knowledge: Therapeutic drug classes, dosage form plausibility, data quality review

## 📈 Business Questions Answered

This project provides insights into:

- Which medications are dispensed the most, and which bring in the most revenue?
- Which therapeutic classes drive the pharmacy's sales?
- How do customers pay, and how does revenue change over time?
- Which medications are close to running out?
- Is the data clinically plausible?

## 💡 Key Insights

### Overall Sales

- The pharmacy recorded **$261,887 in revenue** from **400 sales** and **9,720 units**, an average of **$654.72 per sale**.
- **January was the strongest month** ($70,784) and **April the weakest** ($60,714).
- **Cash brought in the most revenue (36.9%)**, followed by card (31.6%) and insurance (31.5%).
- **Syrup was the top dosage form** at 29.0% of units, followed by injections (24.9%), capsules (23.6%), and tablets (22.4%).

### Revenue by Therapeutic Class

| Class | Sales | Units | Revenue | Share of Revenue |
|---|---|---|---|---|
| Cardiology | 129 | 3,299 | $95,778 | **36.6%** |
| Antibiotic | 77 | 1,886 | $52,827 | 20.2% |
| Pain Relief | 82 | 2,065 | $48,936 | 18.7% |
| Gastro | 41 | 978 | $25,928 | 9.9% |
| Antihistamine | 35 | 780 | $21,439 | 8.2% |
| Diabetes | 36 | 712 | $16,979 | 6.5% |

- **Cardiology drugs brought in more than a third of all revenue.** Atorvastatin ($33,206) and Amlodipine ($33,076) were the two top-earning medications.
- **Paracetamol sold the most units (1,181)** but ranked third in revenue, which shows why units and revenue tell different stories.
- **Metformin was the lowest seller** by both units (712) and revenue ($16,979).

### Inventory Alerts (starting stock of 1,500 units)

| Medication | Units Sold | Current Stock | Days of Supply |
|---|---|---|---|
| Paracetamol | 1,181 | **319** | **32** |
| Atorvastatin | 1,173 | **327** | **33** |
| Amlodipine | 1,168 | **332** | **34** |
| Omeprazole | 978 | 522 | 64 |
| Metformin | 712 | 788 | 133 |

- **Paracetamol, Atorvastatin, and Amlodipine fell below the 400-unit alert threshold**, with about a month of supply left at their current pace.
- Metformin had more than four months of supply, so stocking every drug at the same level would tie up money in slow sellers.

### Clinical Plausibility Check

| Check | Result |
|---|---|
| Sales listed under the correct category | **63 of 400 (15.8%)** |
| Injections of oral-only drugs | **39** |
| Unit price range for each drug | About $3 to $50 |
| Total price equals quantity × unit price | Yes |

- **84% of sales list the wrong category.** Metformin appears under all six categories, including Pain Relief and Cardiology.
- **39 sales are injections of drugs that only come as oral products:** Metformin (13), Atorvastatin (10), Amlodipine (8), and Lisinopril (8).
- These findings are why the dashboard groups drugs by their **real therapeutic class** by default. The original categories are still available through a sidebar toggle.

*Note: This dataset appears to be synthetic. The inventory is simulated because the data has no stock levels. The findings demonstrate dashboard and data quality methods, not real pharmacy performance.*

## 🚀 Learning Outcomes

Building this project strengthened my skills in:

📌 Building an interactive dashboard with Streamlit and Plotly<br>
📌 Comparing units and revenue to see which products truly drive sales<br>
📌 Designing filters that update every chart and metric at once<br>
📌 Turning sales data into an inventory tool with alerts and days of supply<br>
📌 Finding and fixing a calculation that gave impossible results<br>
📌 Checking a dataset for clinical plausibility before trusting the results<br>
📌 Deploying a Python app to the web with GitHub and Streamlit Community Cloud

## 🔮 Next Steps

- Forecast future demand for each medication to set reorder points.
- Add real stock levels and supplier lead times to replace the simulated inventory.
- Compare prices and margins by dosage form once real pricing is available.
- Apply the dashboard to a larger, real-world pharmacy dataset.

## 🙌 Acknowledgment

This project taught me that a dashboard is only as useful as the questions it answers. A chart of top-selling drugs is a starting point. Asking which drugs are about to run out, and whether the data even makes clinical sense, turned it into a tool a pharmacy manager could act on.

## 👨‍💻 Author

**Omar Shazley**: Data Analyst | Python, Excel, SQL, and healthcare data analytics

💼 [LinkedIn](https://www.linkedin.com/in/omar-shazley-914a16b1/)<br>
💻 [GitHub Portfolio](https://github.com/Bromar95)<br>
📧 Email: [omarshazley@gmail.com](mailto:omarshazley@gmail.com)

✨ If you like this project, don't forget to ⭐ star the repo!
