FROM python:3.10.12-slim-bullseye

ARG CADDY_VERSION=2.6.4
ARG S6_OVERLAY_VERSION=3.1.5.0
ARG TINI_VERSION=0.19.0

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install -y exiftool xz-utils \
    && pip install pdm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/caddy
ADD https://github.com/caddyserver/caddy/releases/download/v${CADDY_VERSION}/caddy_${CADDY_VERSION}_linux_amd64.tar.gz /tmp/caddy/caddy.tar.gz
RUN tar xpf ./caddy.tar.gz && mv ./caddy /usr/bin/caddy

WORKDIR /tmp/s6-overlay
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz

ADD https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini /tini
RUN chmod +x /tini

WORKDIR /opt/thanatosns
RUN rm -rf /tmp/caddy /tmp/s6-overlay-noarch.tar.xz /tmp/s6-overlay-x86_64.tar.xz
COPY ./deployment/s6-overlay /etc/services.d

ENV DJANGO_SETTINGS_MODULE=thanatosns.settings.production

COPY . /opt/thanatosns
RUN mv ./deployment/* ./ && rm -rf ./deployment
RUN pdm install --prod

WORKDIR /opt/thanatosns/thanatosns
RUN pdm run manage.py collectstatic

ENTRYPOINT ["/tini", "--"]
EXPOSE 3000 5555
VOLUME /data/thanatosns/export
