FROM python:3.6.6-alpine3.8
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install -r requirements.txt
ADD . /app
ENV PYTHONUNBUFFERED 0
ENV TZ "Europe/Helsinki"
EXPOSE 5000
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "--log-config", "logging.conf", "--log-level", "debug", "app.main:create_app(testing=False)"]
