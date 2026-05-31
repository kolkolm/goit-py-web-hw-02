FROM python:3.12

RUN pip install --no-cache-dir poetry

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-only main --no-interaction --no-ansi

COPY . .

CMD ["/bin/bash"]