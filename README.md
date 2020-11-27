# Finto-Suggestion / Front

## Without Docker from the console:

How to install:
1) sudo apt-get install python3-pip
2) sudo pip3 -V
3) sudo pip3 install -r requirements.txt

OR

1) sudo pip3 install --user flask
2) sudo pip3 install gunicorn

How to run:

sudo gunicorn -w 4 --reload -b localhost:5000 "app.main:create_app(testing=False)"


## With Docker:

In root folder:

docker build --tag flask-app .

docker run -p 5000:5000 --net="host" flask-app
