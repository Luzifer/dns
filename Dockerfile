FROM golang:alpine

ARG COREDNS_VERSION=v1.0.5

ADD ./build.sh /usr/local/bin/build.sh
ADD ./cron_generate.go /src/cron_generate.go
RUN set -ex \
 && apk --no-cache add git bash \
 && bash /usr/local/bin/build.sh

FROM alpine

LABEL maintainer Knut Ahlers <knut@ahlers.me>

COPY --from=0 /go/bin/coredns /usr/local/bin/

ADD ./requirements.txt /src/requirements.txt
RUN set -ex \
 && apk --no-cache add python3 \
 && pip3 install -r /src/requirements.txt

ADD . /src
WORKDIR /src

EXPOSE 53/udp 53

VOLUME ["/src/zones"]

ENTRYPOINT ["/usr/local/bin/coredns"]
CMD ["--"]
