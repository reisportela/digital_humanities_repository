# digital_humanities_repository

Protótipo para mapear dissertações e relatórios sobre Humanidades Digitais a partir do RCAAP, com recolha de metadados, download de PDFs, extração de texto e dashboard exploratório.

## Como correr

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m digital_humanities_repository.pipeline
streamlit run dashboard/app.py
```

## Saídas principais

- `data/raw/rcaap_search_hits_latest.csv`
- `data/raw/rcaap_records_enriched_latest.csv`
- `data/processed/dashboard_documents.csv`
- `data/processed/dashboard_summary.json`

## Critério de inclusão

O dataset final só inclui registos com a expressão `humanidades digitais` no título, resumo ou keywords, e apenas nos tipos documentais definidos em [AGENTS.md](AGENTS.md).
