# Term Deposit Campaign Intelligence

Interactive Streamlit dashboard and machine-learning analysis for prioritizing bank term-deposit campaigns. The project turns historical campaign records into descriptive campaign insights and model-evaluation evidence for outreach planning.

> This is a decision-support project. It helps rank and prioritize campaign contacts; it does not make automatic approval/rejection decisions or establish causal effects.

## Project objectives

- Explore historical patterns associated with term-deposit subscriptions.
- Identify campaign segments, contact channels, and timing patterns that merit further testing.
- Compare classification approaches for the imbalanced subscription target.
- Evaluate a pre-call prioritization model without using post-call information.
- Present the findings in a filterable dashboard for non-technical stakeholders.

## Repository contents

- `Bank_Term_Deposit_Prediction.ipynb` - the main analytical notebook: business framing, data checks, EDA, feature preparation, model comparison, threshold scenarios, and recommendations.
- `bank-additional-full.csv` - source campaign dataset. It is semicolon-delimited and contains 41,188 campaign observations with 21 columns.
- `app.py` - Streamlit decision-support dashboard built from the notebook findings.
- `requirements.txt` - runtime dependencies required to launch the dashboard.
- `bank_term_deposit_prediction_input.csv` - an exported prediction-input dataset. It is provided as a project artifact; the dashboard can generate a filter-specific export during use.
- `Bank_Term_Deposit_Presentation_Minimalist_v9.pptx` and `Bank_Term_Deposit_v1_final.pdf` - presentation deliverables.

## Notebook guide

Open `Bank_Term_Deposit_Prediction.ipynb` to review the complete analysis. Its flow is:

1. **Business understanding** - defines the use case as pre-call campaign prioritization and explains why the positive class is imbalanced.
2. **Data understanding and quality checks** - examines the 41,188 campaign observations, target distribution, missing values, duplicates, and field meanings.
3. **Exploratory data analysis** - investigates historical patterns by month, contact channel, job, previous campaign outcome, contact frequency, and other candidate signals.
4. **Leakage-aware feature preparation** - engineers relevant historical-contact signals and excludes invalid features from scoring.
5. **Model evaluation** - compares candidate models and imbalance treatments using stratified validation. Average Precision (AP) is the primary model-selection metric because subscriptions are the minority class.
6. **Threshold scenarios** - contrasts threshold `0.50` and `0.60` as operating choices rather than claiming one universal financial optimum.
7. **Recommendations and limitations** - translates associations and model performance into testable campaign actions and monitoring needs.

### Important modelling decisions

- `duration` is excluded from the production-oriented feature set. It becomes known after a call is completed, so using it for pre-call scoring would leak outcome-related information.
- `pdays=999` is handled as a no-prior-contact signal, rather than being interpreted as an ordinary number of days.
- Preprocessing and random oversampling are performed within training folds only, protecting validation/test evaluation from leakage.
- The selected configuration is **Gradient Boosting + Random Oversampling**, selected by 5-fold cross-validation AP of **0.4634**. The untouched test set reports **ROC-AUC 0.8140** and **AP 0.4810**.
- At threshold `0.60`, the notebook reports a more selective scenario: precision **43.81%**, recall **61.42%**, and **1,301 of 8,238** test contacts targeted. Actual contact cost, campaign capacity, and customer value are not available, so this is not presented as a financially optimized threshold.

## Dashboard features

The Streamlit app provides:

- Campaign KPIs for the active filter context.
- Month, contact-channel, and job filters.
- Key campaign insight cards with the supporting sample size.
- Tabs for overview, campaign performance, customer segments, model results, and data exploration.
- CSV export of the current filter's prediction-input fields.

The dashboard displays notebook-validated model results. It does **not** retrain a model, persist a scoring model, or produce live customer-level predictions.

## Run the dashboard locally

Use Python 3.10+ in the project folder:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Streamlit will show a local URL in the terminal. Keep `app.py` and `bank-additional-full.csv` in the same folder.

## Re-running the notebook

The dashboard dependencies are intentionally lightweight and are sufficient for `app.py`. To rerun all machine-learning cells in the notebook, use an environment with Jupyter plus its additional analysis packages:

```powershell
py -m pip install jupyter scikit-learn imbalanced-learn category-encoders matplotlib seaborn
py -m jupyter notebook
```

Then open `Bank_Term_Deposit_Prediction.ipynb`, confirm the CSV is in the same directory, and use **Run All**. The notebook includes a historical stored `PicklingError` output from a parallel oversampling attempt; clear outputs and rerun in a compatible environment before treating a fresh run as verified.

## Interpretation notes and limitations

- Dashboard charts describe historical associations in the selected data; they do not prove that a segment or month causes subscription.
- March/December or other smaller segments should always be interpreted with the displayed sample size.
- The model should support human campaign planning and eligibility rules, not replace them.
- Before operational use, validate performance with a pilot/A-B test and monitor drift, response rate, precision, recall, and campaign workload.
- Threshold selection should be revisited once contact capacity, conversion value, and false-positive/false-negative costs are available.

## Data source

The project uses the UCI Bank Marketing additional campaign dataset, distributed locally here as `bank-additional-full.csv`.
