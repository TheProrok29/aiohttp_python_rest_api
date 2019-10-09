FROM python:3.7.3-alpine3.9

WORKDIR /app
ENV PYTHONPATH=/app

RUN apk --update \
    add --no-cache --virtual build_dependencies \
        alpine-sdk=1.0-r0 \
        libc-dev=0.7.1-r0 \
        libffi-dev=3.2.1-r6 \
        libressl-dev=2.7.5-r0 \
        python3-dev=3.6.8-r2 && \
    pip install --upgrade pip==19.0.3

COPY requirements.txt ./
RUN pip install -r requirements.txt && \
        rm -rf requirements.txt

RUN apk del build_dependencies && rm -rf /root/.cache
RUN apk add --no-cache tini=0.18.0-r0 && addgroup -S app && adduser -S app -G app

COPY run.sh logging.conf ./
COPY helion ./helion

USER app:app

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["./run.sh"]
