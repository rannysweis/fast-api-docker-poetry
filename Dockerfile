FROM python:3.11.3-alpine as python-base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"\
    POETRY_VERSION=1.4.2

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
RUN apk add bash libstdc++

# create user
RUN addgroup --gid 1000 -S appuser && adduser --uid 1000 -S appuser -G appuser

RUN apk add bash \
    build-base \
    linux-headers \
    git \
    gcc  \
    musl-dev  \
    python3-dev  \
    libffi-dev  \
    openssl-dev \
    curl

WORKDIR $PYSETUP_PATH

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-dev

# ------------------------------------------------------------------------------------
# 'test' stage installs all dev deps and can be used to develop code
FROM python-base as test

# Copy in the venv
COPY --from=python-base --chown=appuser $POETRY_HOME $POETRY_HOME
COPY --from=python-base --chown=appuser $PYSETUP_PATH $PYSETUP_PATH

USER appuser

# install dev libs
WORKDIR $PYSETUP_PATH
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install

WORKDIR /home/appuser

COPY --chown=appuser . .
RUN chmod +x scripts/*

EXPOSE 8009
ENTRYPOINT ["/home/appuser/scripts/docker-entrypoint.sh"]
CMD ["python", "-m", "app.main"]

# ------------------------------------------------------------------------------------
# 'development' stage installs all dev deps and can be used to develop code
FROM python-base as development

# Copy in the venv
COPY --from=python-base --chown=appuser $POETRY_HOME $POETRY_HOME
COPY --from=python-base --chown=appuser $PYSETUP_PATH $PYSETUP_PATH

USER appuser

# install dev libs
WORKDIR $PYSETUP_PATH
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install
RUN opentelemetry-bootstrap --action=install

WORKDIR /home/appuser

COPY --chown=appuser . .
RUN chmod +x scripts/*

EXPOSE 8009
ENTRYPOINT ["/home/appuser/scripts/docker-entrypoint.sh"]
CMD ["opentelemetry-instrument", "python", "-m", "app.main"]

# ------------------------------------------------------------------------------------
# 'release' stage uses the clean 'python-base' stage and copies
# in only our runtime deps that were installed in the 'python-base'
FROM python-base as release

COPY --from=python-base --chown=appuser $VENV_PATH $VENV_PATH

USER appuser

RUN opentelemetry-bootstrap --action=install

WORKDIR /home/appuser

COPY --chown=appuser . .
RUN chmod +x scripts/*

EXPOSE 8009
ENTRYPOINT ["/home/appuser/scripts/docker-entrypoint.sh"]
CMD ["opentelemetry-instrument", "python", "-m", "app.main"]
