FROM ubuntu:18.04


ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt install python3-pip postgresql postgresql-server-dev-10 -y

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

EXPOSE 80
CMD python3 /src/manage.py start_polling
