FROM jjanzic/docker-python3-opencv:latest

WORKDIR /autovibingcat

COPY . .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y \
    && pip3 install -r ./requirements.txt

ENV QT_DEBUG_PLUGINS=1

ENTRYPOINT [ "python", "-m", "autovibingcat" ]