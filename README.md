# CLI

    python -m plagdet_vi.cli.compare --a path/to/A.pdf --b path/to/B.docx --out reports/

# API

    uvicorn plagdet_vi.services.api.main:app --host 0.0.0.0 --port 8000
    curl -X POST "http://localhost:8000/compare?a=path/to/A.pdf&b=path/to/B.docx&out=reports"

```
src
 ┣ plagdet_vi
 ┃ ┣ __pycache__
 ┃ ┃ ┗ __init__.cpython-310.pyc
 ┃ ┣ align
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┗ smith_waterman.cpython-310.pyc
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┗ smith_waterman.py
 ┃ ┣ cli
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┗ compare.cpython-310.pyc
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┗ compare.py
 ┃ ┣ config
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┗ settings.cpython-310.pyc
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┗ settings.py
 ┃ ┣ embeddings
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┣ biencoder.cpython-310.pyc
 ┃ ┃ ┃ ┗ reranker.cpython-310.pyc
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┣ biencoder.py
 ┃ ┃ ┗ reranker.py
 ┃ ┣ fingerprint
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┣ shingles.cpython-310.pyc
 ┃ ┃ ┃ ┗ simhash.cpython-310.pyc
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┣ shingles.py
 ┃ ┃ ┗ simhash.py
 ┃ ┣ io
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┣ extract_docx.cpython-310.pyc
 ┃ ┃ ┃ ┣ extract_pdf.cpython-310.pyc
 ┃ ┃ ┃ ┣ figures_pdf.cpython-310.pyc
 ┃ ┃ ┃ ┣ ocr.cpython-310.pyc
 ┃ ┃ ┃ ┗ tables_pdf.cpython-310.pyc
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┣ extract_docx.py
 ┃ ┃ ┣ extract_pdf.py
 ┃ ┃ ┗ ocr.py
 ┃ ┣ pipeline
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┗ compare.cpython-310.pyc
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┗ compare.py
 ┃ ┣ preprocess
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┣ normalize.cpython-310.pyc
 ┃ ┃ ┃ ┗ segment.cpython-310.pyc
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┣ normalize.py
 ┃ ┃ ┗ segment.py
 ┃ ┣ report
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┣ highlight.cpython-310.pyc
 ┃ ┃ ┃ ┗ html.cpython-310.pyc
 ┃ ┃ ┣ templates
 ┃ ┃ ┃ ┗ report.html.j2
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┣ highlight.py
 ┃ ┃ ┗ html.py
 ┃ ┣ scoring
 ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┗ aggregate.cpython-310.pyc
 ┃ ┃ ┣ __init__.py
 ┃ ┃ ┗ aggregate.py
 ┃ ┣ services
 ┃ ┃ ┗ api
 ┃ ┃ ┃ ┣ __pycache__
 ┃ ┃ ┃ ┃ ┣ __init__.cpython-310.pyc
 ┃ ┃ ┃ ┃ ┗ main.cpython-310.pyc
 ┃ ┃ ┃ ┣ __init__.py
 ┃ ┃ ┃ ┗ main.py
 ┃ ┗ __init__.py
 ┗ reports
 ┃ ┣ report.html
 ┃ ┗ report.json

```
