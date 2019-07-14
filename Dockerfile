FROM ubuntu:18.04


ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN apt update && \
    apt install curl postgresql postgresql-server-dev-10 libzbar0 -y

RUN apt-get install wget python3-pip build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev -y && \
    wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz && \
    tar xzf Python-3.7.4.tgz && cd Python-3.7.4 && ./configure --enable-optimizations && make altinstall

RUN apt install python3-pip


COPY requirements.txt /
RUN pip3.7 install -r /requirements.txt

EXPOSE 80
CMD python3.7 /src/manage.py start_polling
