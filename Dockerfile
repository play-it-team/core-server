FROM alpine
MAINTAINER Abhimanyu Saharan <desk.abhimanyu@gmail.com>

ENV PRJ_SRC /opt/playit

RUN apk update
RUN apk add --virtual .build-deps gcc git jpeg-dev libffi-dev libpq musl-dev make zlib-dev

COPY . $PRJ_SRC
WORKDIR $PRJ_SRC

RUN pip install -r requirements/local.txt

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]