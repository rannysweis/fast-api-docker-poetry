FROM python:3.11.3-slim-bullseye as python-base

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
ENV PYTHONPATH="${PYTHONPATH}:${PYSETUP_PATH}"

RUN apt-get update && apt-get upgrade -y
RUN apt-get install --no-install-recommends -y curl

#make lsb-release wget gnupg curl build-essential gcc libpq-dev
#RUN apk add -y bash libstdc++ build-essential linux-headers-generic git gcc musl-dev python3-dev libffi-dev curl

# create user
RUN addgroup --gid 1000 appuser && adduser --uid 1000 --system --ingroup appuser appuser

WORKDIR $PYSETUP_PATH

RUN chown -R appuser /opt
USER appuser

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-dev

# ------------------------------------------------------------------------------------
# 'development' stage installs all dev deps and can be used to develop code
FROM python-base as development

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
# 'release' stage uses the clean 'python-base' stage and copies
# in only our runtime deps that were installed in the 'python-base'
FROM python-base as release

WORKDIR /home/appuser

COPY --chown=appuser . .
RUN chmod +x scripts/*

EXPOSE 8009
ENTRYPOINT ["/home/appuser/scripts/docker-entrypoint.sh"]
CMD ["python", "-m", "app.main"]
