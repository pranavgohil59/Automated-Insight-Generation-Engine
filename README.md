# 🏥 Automated Insight Generation Engine

An interactive Python application that analyzes district-level healthcare performance data, discovers trends, outliers, and correlations, and generates plain-English insights with an interactive dashboard.

Built for **Assignment 4 — Automated Insight Generation (AI/ML)**.

---

## ⚡ Quick Start

### 1. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📁 Project Structure

This project is kept clean, lightweight, and easy to understand (only 2 source files):

- **[`app.py`](file:///Users/pranavgohil/Desktop/Data-insight%20project/app.py)**: The complete source code (~250 lines) containing all calculation functions and the Streamlit web dashboard.
- **[`analysis.ipynb`](file:///Users/pranavgohil/Desktop/Data-insight%20project/analysis.ipynb)**: Step-by-step Jupyter Notebook demonstrating each calculation with Pandas.
- **[`data/healthcare_data.csv`](file:///Users/pranavgohil/Desktop/Data-insight%20project/data/healthcare_data.csv)**: The sample healthcare dataset provided in the assignment PDF.
- **[`presentation_guide.md`](file:///Users/pranavgohil/Desktop/Data-insight%20project/presentation_guide.md)**: A simple interview preparation guide explaining every line of code and common questions.
- **[`requirements.txt`](file:///Users/pranavgohil/Desktop/Data-insight%20project/requirements.txt)**: Python dependencies (`pandas`, `numpy`, `streamlit`, `plotly`).

---

## 🧩 How the Code Works (`app.py`)

All logic is organized into 5 straightforward Python functions:

1. **`load_data(file_source)`**:
   - Ingests the CSV using Pandas.
   - Validates that the required columns exist (`month`, `district`, `anc_coverage`, `institutional_delivery`, `immunization`, `high_risk_cases`).
   - Cleans district text and formats months as `YYYY-MM`.
   - Removes any duplicate records.

2. **`detect_trends(df, indicators, threshold)`**:
   - Compares consecutive months for each district:
     $$\text{pct\_change} = \frac{\text{current} - \text{previous}}{\text{previous}} \times 100$$
   - Flags changes where $|\text{pct\_change}| \ge \text{threshold}$ (default: 10%, adjustable in UI).

3. **`detect_outliers(df, indicators, iqr_multiplier)`**:
   - Uses the standard **Interquartile Range (IQR)** rule:
     - $\text{IQR} = Q3 - Q1$
     - $\text{Lower Bound} = Q1 - (1.5 \times \text{IQR})$
     - $\text{Upper Bound} = Q3 + (1.5 \times \text{IQR})$
   - Flags values falling outside these fences.

4. **`detect_correlations(df, indicators, threshold)`**:
   - Computes Pearson correlation matrix across indicators using `df.corr()`.
   - Flags pairs with $|r| \ge 0.70$ (ignoring self-pairs and duplicates).

5. **`generate_insights(trends, outliers, correlations, trend_thresh)`**:
   - Combines findings into structured rows with IDs (`INS-0001`, `INS-0002`...).
   - Assigns data-derived severity (`High`, `Medium`, `Low`).
   - Generates plain-English narrative explanations without any hardcoded text.

---

## 📊 Dashboard Features

- **Sidebar Controls**:
  - Live filters for Districts, Months, and Indicators.
  - Interactive sliders for Trend Threshold (%), Outlier IQR Multiplier, and Correlation cutoff ($|r|$).
- **Tab 1: Automated Insights**:
  - Filterable table of structured findings with data-derived severity badges.
  - Download buttons for Insights CSV, Insights JSON, and Correlation Matrix CSV.
- **Tab 2: Visualizations**:
  - Severity distribution bar chart.
  - Pearson correlation heatmap.
  - District-level indicator trend line charts over time.
- **Tab 3: Raw Dataset**:
  - Table preview and missing values counter.

---

## 🔍 Key Findings in Provided Dataset

- **Ahmedabad:** ANC coverage dropped significantly from **85% to 69%** ($-18.8\%$, High Severity Trend).
- **Mehsana:** ANC coverage fell to an extreme outlier of **42%** (state average ~78%, High Severity Outlier).
- **Mehsana:** High-risk cases surged from **11 to 28** in the same month ($+154\%$).
- **Correlation:** Strong inverse correlation ($r = -0.93$) between ANC coverage and high-risk cases.
