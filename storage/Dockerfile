FROM ubuntu:20.04

LABEL maintainer="abinepal@my.bcit.ca"

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

RUN apt-get install -y curl && \
    curl -LJO https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x wait-for-it.sh

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]