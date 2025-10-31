## Projecto Calidad de Software

Primera vez:
python -m pip install --upgrade pip
pip install poetry
poetry install

Run:
poetry run uvicorn src.projectocalidadsoftware.main:app --reload'

Run tests:
poetry run pytest -v

Run coverage:
poetry run pytest --cov=src.projectocalidadsoftware --cov-report=term-missing --cov-report=xml