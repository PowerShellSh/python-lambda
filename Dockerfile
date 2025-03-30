FROM python:3.12-slim

ENV POETRY_HOME=/opt/poetry
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Poetryのインストール
RUN pip install poetry==2.1.1

# Poetryの設定と依存関係のインストール
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry update before poetry install --with dev --no-interaction --no-ansi

# 作業ディレクトリの設定
WORKDIR /app

# Lambda関数のエントリーポイント
COPY lambda/ /app/lambda

CMD ["python", "-m", "lambda.app"]
