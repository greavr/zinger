FROM python:3
#FROM debian

MAINTAINER Rick Greaves "rgreaves@google.com"

#RUN apt-get update -y
#RUN apt-get install -y python3-pip python3-dev
#RUN apt-get autoremove -y

COPY /code /app

WORKDIR /app
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python3", "index.py"]
