# Software Quality & Delivery Capability Scan

A Streamlit application for consultants to assess software delivery maturity across seven domains, identify improvement priorities, and export client-ready outputs.

## Run

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Features

- Dashboard with weighted maturity score, domain averages, traffic-light statuses, and charts
- Assessment input page with 1-5 scoring and evidence notes
- Roadmap page with improvement priorities and suggested actions
- Evidence checklist page
- Excel export using `openpyxl`
- PDF export using `matplotlib.backends.backend_pdf`

