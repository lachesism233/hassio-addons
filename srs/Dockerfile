ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# jq: 解析 /data/options.json；tzdata: 支持 timezone 选项
RUN apt-get update \
    && apt-get install -y --no-install-recommends jq tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY run.sh /run.sh
RUN chmod +x /run.sh

WORKDIR /usr/local/srs

CMD [ "/run.sh" ]
