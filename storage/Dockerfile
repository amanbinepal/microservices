FROM ubuntu:20.04

LABEL maintainer="abinepal@my.bcit.ca"

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

#ENTRYPOINT [ "python3" ]

#CMD [ "app.py" ]

# Set execute permissions for start.sh
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Use start.sh as entry point
ENTRYPOINT ["/app/start.sh"]