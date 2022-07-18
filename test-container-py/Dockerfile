FROM alpine:3.15.4

RUN apk update &&\
    apk upgrade &&\
    apk add bash jq curl python3 py3-pip &&\
    pip3 install yq pika &&\
    rm -rf /var/cache/apk/*

COPY rmq-recv.py entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]