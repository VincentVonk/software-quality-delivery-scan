# Software Quality & Delivery Transformation Scan

A consultant-facing Streamlit tool to assess the current maturity of a client's software delivery and quality capability, identify gaps, and generate a practical transformation roadmap from AS-IS to TO-BE.

## Run

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Features

- Dashboard with weighted maturity score, domain averages, traffic-light statuses, and charts
- Assessment input page with 1-5 scoring and evidence notes
- Evidence checklist page
- Existing improvement roadmap page with prioritized actions
- Transformation Roadmap page with AS-IS overview, target-state selection, gap analysis, four-wave roadmap, benefits, and investment view
- Excel export using `openpyxl`
- PDF export using `matplotlib.backends.backend_pdf`

## Target States

- Basic Foundation: target maturity 2.0
- Professional Delivery: target maturity 3.0
- Managed Quality Engineering: target maturity 4.0
- Optimizing / Leading: target maturity 5.0
