FROM python:3.10

WORKDIR /webapp

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./src ./src
COPY ./start.py ./

EXPOSE 8080
VOLUME /webapp/storage
ENV DB_URL="sqlite:////webapp/storage/db.sqlite"

CMD ["python", "start.py"]
