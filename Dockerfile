FROM python:3.6.6-alpine3.8
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install -r requirements.txt
ADD . /app
EXPOSE 5000
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app.main:create_app(testing=False)"]
