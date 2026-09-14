ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apk add --no-cache python3 tzdata

COPY capture.py scheduler.py web.py main.py /
COPY run.sh /
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
