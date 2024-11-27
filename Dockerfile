# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

# Copyright (C) 2024 Ibrahem Mouhamad
#
# SPDX-License-Identifier: MIT

ARG PIP_VERSION=22.0.2
ARG BASE_IMAGE=ubuntu:22.04

FROM ${BASE_IMAGE} as build-image-base

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get --no-install-recommends install -yq \
    curl \
    libsasl2-dev \
    nasm \
    git \
    pkg-config \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

ARG PIP_VERSION
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN --mount=type=cache,target=/root/.cache/pip/http \
    python3 -m pip install -U pip==${PIP_VERSION}

FROM build-image-base AS build-image

COPY simple_rag/requirements/ /tmp/simple_rag/requirements/

ARG SIMPLE_RAG_CONFIGURATION="production"

RUN --mount=type=cache,target=/root/.cache/pip/http \
    python3 -m pip wheel --no-deps \
    -r /tmp/simple_rag/requirements/${SIMPLE_RAG_CONFIGURATION}.txt \
    -w /tmp/wheelhouse

FROM ${BASE_IMAGE}

ARG http_proxy
ARG https_proxy
ARG no_proxy=
ARG socks_proxy
ARG TZ="Etc/UTC"

ENV TERM=xterm \
    http_proxy=${http_proxy}   \
    https_proxy=${https_proxy} \
    no_proxy=${no_proxy} \
    socks_proxy=${socks_proxy} \
    LANG='C.UTF-8'  \
    LC_ALL='C.UTF-8' \
    TZ=${TZ}

ARG USER="django"
ARG SIMPLE_RAG_CONFIGURATION="production"
ENV DJANGO_SETTINGS_MODULE="simple_rag.settings.${SIMPLE_RAG_CONFIGURATION}"

# Install necessary apt packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get --no-install-recommends install -yq \
    bzip2 \
    ca-certificates \
    curl \
    git \
    libpython3.10 \
    libsasl2-2 \
    nginx \
    p7zip-full \
    python3 \
    python3-distutils \
    python3-venv \
    supervisor \
    tzdata \
    && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# Add a non-root user
ENV USER=${USER}
ENV HOME /home/${USER}
RUN adduser --shell /bin/bash --disabled-password --gecos "" ${USER}

ARG CLAM_AV="no"
RUN if [ "$CLAM_AV" = "yes" ]; then \
    apt-get update && \
    apt-get --no-install-recommends install -yq \
    clamav \
    libclamunrar9 && \
    sed -i 's/ReceiveTimeout 30/ReceiveTimeout 300/g' /etc/clamav/freshclam.conf && \
    freshclam && \
    chown -R ${USER}:${USER} /var/lib/clamav && \
    rm -rf /var/lib/apt/lists/*; \
    fi

# Install wheels from the build image
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
ARG PIP_VERSION
ARG PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m pip install -U pip==${PIP_VERSION}
RUN --mount=type=bind,from=build-image,source=/tmp/wheelhouse,target=/mnt/wheelhouse \
    python -m pip install --no-index /mnt/wheelhouse/*.whl

# install spaCy models
RUN python -m spacy download ru_core_news_sm

ENV NUMPROCS=1

# Install and initialize SIMPLE_RAG, copy all necessary files
COPY simple_rag/nginx.conf /etc/nginx/nginx.conf
COPY --chown=${USER} supervisord/ ${HOME}/supervisord
COPY --chown=${USER} wait-for-it.sh manage.py backend_entrypoint.sh wait-for-deps.sh ${HOME}/
COPY --chown=${USER} simple_rag/ ${HOME}/simple_rag

ARG COVERAGE_PROCESS_START
RUN if [ "${COVERAGE_PROCESS_START}" ]; then \
    echo "import coverage; coverage.process_startup()" > /opt/venv/lib/python3.10/site-packages/coverage_subprocess.pth; \
    fi

# RUN all commands below as 'django' user
USER ${USER}
WORKDIR ${HOME}

RUN mkdir -p data keys logs /tmp/supervisord statics

EXPOSE 8080
ENTRYPOINT ["./backend_entrypoint.sh"]