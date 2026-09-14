ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apk add --no-cache python3

COPY server.py /
COPY run.sh /
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
