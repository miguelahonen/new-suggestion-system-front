# Finto-Suggestion / Front

## How to run:

### Without Docker from the console:

How to install:
1) sudo apt-get install python3-pip
2) sudo pip3 -V
3) sudo pip3 install -r requirements.txt

OR

1) sudo pip3 install --user flask
2) sudo pip3 install gunicorn

Then:

sudo gunicorn -w 4 --reload -b localhost:5000 "app.main:create_app(testing=False)"


### With Docker:

In a root folder:

docker build --tag flask-app .

docker run -p 5000:5000 --net="host" flask-app


### By running the docker-compose:
How to install docker-compose:
https://docs.docker.com/compose/install/

In a root folder run:
docker-compose build && docker-compose up


## How to access the container:

While the container is running:
- docker ps
- docker exec -it [name of your container] sh
