FROM golang:alpine

ADD ./build.sh /usr/local/bin/build.sh
RUN set -ex \
 && apk --no-cache add git bash \
 && bash /usr/local/bin/build.sh

FROM alpine

LABEL maintainer Knut Ahlers <knut@ahlers.me>

COPY --from=0 /go/bin/coredns /usr/local/bin/

ADD . /src
WORKDIR /src

EXPOSE 53/udp 53

ENTRYPOINT ["/usr/local/bin/coredns"]
CMD ["--"]
