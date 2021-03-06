FROM alpine

LABEL maintainer Knut Ahlers <knut@ahlers.me>

COPY build.sh         /src/
COPY requirements.txt /src/

RUN set -ex \
 && apk --no-cache add bash \
 && /src/build.sh

COPY . /src
WORKDIR /src

EXPOSE 53/udp 53

VOLUME ["/src/zones"]

ENTRYPOINT ["/src/docker-entrypoint.sh"]
CMD ["named", "-g"]
