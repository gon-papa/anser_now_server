FROM python:3.12.3

SHELL ["/bin/bash", "-c"]

# 作業ディレクトリの設定
WORKDIR /src

RUN apt-get update && \
    apt-get install -y build-essential libffi-dev && \
    apt-get install -y sqlite3

RUN pip install --upgrade pip

# 必要なファイルのコピー
COPY ./pyproject.toml /src/pyproject.toml
COPY ./poetry.lock /src/poetry.lock

# Poetryのインストール
RUN curl -sSL https://install.python-poetry.org | python -

# 環境変数の設定
ENV MAKE_ENV=container
ENV PATH="/root/.local/bin:$PATH"

# Poetryの設定と依存関係のインストール
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

# アプリケーションの起動コマンドを設定
ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]