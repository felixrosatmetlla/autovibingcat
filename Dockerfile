FROM jjanzic/docker-python3-opencv:latest

WORKDIR /autovibingcat

COPY . .

RUN pip3 install --upgrade pip
RUN pip3 install ffmpeg-python==0.2.0
RUN pip3 install moviepy==1.0.3
RUN pip3 install pytube==10.8.5
RUN pip3 install youtube-search-python==1.4.0
RUN pip3 install matplotlib==3.3.4
RUN pip3 install scipy==1.6.1
RUN pip3 install PyWavelets==1.1.1

ENTRYPOINT [ "python", "-m", "autovibingcat" ]
