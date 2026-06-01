FROM python:3.12

RUN pip install --no-cache-dir poetry

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root --no-interaction --no-ansi

COPY . .

CMD ["python", "hw/main.py"]