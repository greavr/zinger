FROM debian

MAINTAINER Rick Greaves "rgreaves@google.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev
RUN apt-get autoremove -y

COPY /code /app

WORKDIR /app
RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["python3", "index.py"]
