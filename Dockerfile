FROM python:3.9

WORKDIR /app

COPY ./app/req.txt ./

RUN pip install -r req.txt

RUN spotdl --download-ffmpeg

COPY ./app ./

CMD ["python3", "spotdl_bot.py"]
