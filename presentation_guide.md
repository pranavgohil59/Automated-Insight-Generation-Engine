# 🎤 Simple Presentation & Interview Guide (Fresher Edition)

> **Purpose:** This guide is written in plain, simple English so you can easily understand every line of code, explain the project with full confidence in your interview tomorrow, and answer any question without getting nervous.

---

## ⏱️ 1. How to Introduce Your Project (30 Seconds)

Say this in your own words:

> *"Hello! For this assignment, I built a simple and interactive **Automated Healthcare Insight Engine** using Python and Streamlit.*
>
> *Normally, healthcare data has lots of numbers, and it takes time to find problems manually. My application reads the monthly district dataset and automatically identifies three things:*
> 1. ***Month-over-month trends*** *(e.g., if an indicator dropped or increased significantly).*
> 2. ***Statistical outliers*** *(e.g., unusual spikes or drops using the standard IQR method).*
> 3. ***Correlations*** *(relationships between different indicators).*
>
> *Finally, it generates plain-English summary sentences with severity levels (High, Medium, Low) and lets users filter districts, adjust threshold sliders in real-time, and download the insights as CSV or JSON."*

---

## 📂 2. What Files Are in This Project?

Keep it simple:
- **`app.py`**: The main Python file (only ~200 lines). It contains all 5 calculation functions and the Streamlit frontend.
- **`analysis.ipynb`**: A clean Jupyter notebook showing the same calculations step-by-step with pandas.
- **`data/healthcare_data.csv`**: The sample healthcare dataset provided in the assignment PDF.
- **`requirements.txt`**: Libraries used (`pandas`, `numpy`, `streamlit`, `plotly`).

---

## 🧩 3. Explaining the Code in `app.py` (Line-by-Line Simplicity)

The entire code is divided into **5 simple functions**. If they ask you to walk through the code, explain these 5 functions:

### 1. `load_data(file_source)`
- **What it does:** Reads the CSV file using `pd.read_csv()`.
- **Validation:** Checks if the 6 required columns exist (`month`, `district`, `anc_coverage`, `institutional_delivery`, `immunization`, `high_risk_cases`).
- **Cleaning:** Strips any extra spaces from district names, formats months to `YYYY-MM`, converts indicators to numbers, and drops any accidental duplicate records.

### 2. `detect_trends(df, indicators, threshold)`
- **What it does:** Calculates month-over-month percentage change.
- **Formula:**
  $$\text{Percentage Change} = \frac{\text{Current Month} - \text{Previous Month}}{\text{Previous Month}} \times 100$$
- **Logic:** Groups data by district, compares the previous month with the current month, and if the absolute change is $\ge \text{threshold}$ (e.g. $10\%$), it flags it as a trend.

### 3. `detect_outliers(df, indicators, iqr_multiplier)`
- **What it does:** Finds unusually high or low values using the standard **IQR (Interquartile Range)** rule.
- **How IQR works:**
  - $Q1$ = 25th percentile, $Q3$ = 75th percentile.
  - $\text{IQR} = Q3 - Q1$.
  - $\text{Lower Bound} = Q1 - (1.5 \times \text{IQR})$.
  - $\text{Upper Bound} = Q3 + (1.5 \times \text{IQR})$.
  - Any number smaller than the lower bound or bigger than the upper bound is flagged as an outlier.

### 4. `detect_correlations(df, indicators, threshold)`
- **What it does:** Uses `df.corr(method="pearson")` to find relationships between numeric indicators.
- **Logic:** Checks which pairs have a correlation $|r| \ge 0.70$ (ignoring self-correlation like comparing a column to itself).

### 5. `generate_insights(trends, outliers, correlations, trend_thresh)`
- **What it does:** Takes the flagged math results and writes clean English sentences.
- **Severity Logic (Data-driven):**
  - For trends: If change $\ge 18\%$, severity is **High**; otherwise **Medium** or **Low**.
  - For outliers: Automatically marked as **High** because they are unusual extremes.
  - For correlations: If $|r| \ge 0.85$, marked as **High**; otherwise **Medium**.
- Assigns clean IDs: `INS-0001`, `INS-0002`...

---

## 🔍 4. Key Stories to Show from the Company's Data

During the interview, point out these real patterns that the engine discovered in the sample data:

1. **Ahmedabad ANC Coverage Drop:**
   - In 2026-07 it was $85\%$, but in 2026-08 it dropped to $69\%$ (a **-18.8% drop**). The engine flags this as a **High Severity Trend**.
2. **Mehsana Extreme Outlier:**
   - In 2026-08, Mehsana had an ANC coverage of only **$42\%$** (state average was around $78\%$). The engine flags this as a **High Severity Outlier**.
3. **Mehsana High-Risk Spike:**
   - In the same month, Mehsana's high-risk cases jumped from **11 to 28** ($+154\%$).
4. **Negative Correlation ($r = -0.93$):**
   - ANC coverage and high-risk cases have a strong inverse relationship: when ANC coverage drops, high-risk cases spike.

---

## 🎯 5. Top 4 Interview Questions & Easy Answers

### Q1: "Why did you use Streamlit?"
> **Answer:** *"Streamlit is written in pure Python, so I didn't need to build a complicated frontend in React or HTML. It lets you create interactive filters and charts very quickly and cleanly."*

### Q2: "Why did you choose the IQR method for outliers?"
> **Answer:** *"Because healthcare data can have extreme values. Z-scores assume a bell-shaped normal curve, whereas IQR uses percentiles (Q1 and Q3) and the median, so it doesn't get distorted by extreme numbers."*

### Q3: "Did you hardcode any district names in your text?"
> **Answer:** *"No, none! All district names, indicators, numbers, and percentages are inserted dynamically using Python f-strings based on whatever data is uploaded."*

### Q4: "What happens if someone uploads a CSV with missing values?"
> **Answer:** *"The app handles it safely with `pd.to_numeric(errors='coerce')` and `dropna()`, so it skips missing numbers instead of crashing."*

---

## 🖥️ 6. How to Demo in 2 Minutes (Screen Share Steps)

1. Open terminal and run:
   ```bash
   streamlit run app.py
   ```
2. **Show the Metrics:** Point to the top metric cards (Total Insights, Trends, Outliers, Correlations).
3. **Show Tab 1 (Automated Insights):**
   - Scroll through the table. Point to `INS-0001` and explain that the sentences are created automatically.
   - Click **Download Insights CSV** to show that exports work.
4. **Move a Slider (The Best Part):**
   - In the left sidebar, move the **Significant Trend Threshold slider** from `10%` to `20%`.
   - Show how the table updates instantly in real-time.
5. **Show Tab 2 (Visualizations):**
   - Show the **Severity Bar Chart** (High, Medium, Low).
   - Show the **Correlation Heatmap**.
   - Show the **District Trend Line Chart** (pick `anc_coverage` and point out Ahmedabad's drop).
