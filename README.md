# CLI

    python -m plagdet_vi.cli.compare --a path/to/A.pdf --b path/to/B.docx --out reports/

# API

    uvicorn plagdet_vi.services.api.main:app --host 0.0.0.0 --port 8000
    curl -X POST "http://localhost:8000/compare?a=path/to/A.pdf&b=path/to/B.docx&out=reports"
