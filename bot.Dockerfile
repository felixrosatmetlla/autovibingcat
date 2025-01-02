FROM jjanzic/docker-python3-opencv:latest

WORKDIR /autovibingcat

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./autovibingcat.py ./bot.py ./requirements.txt ./
ADD resources resources

RUN pip3 install -r ./requirements.txt

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "python", "-m", "bot" ]