## Finto-Suggestion / Front

How to install:
1) sudo apt-get install python3-pip
2) sudo pip3 -V

3) sudo pip3 install -r requirements.txt

OR

1) sudo pip3 install --user flask
2) sudo pip3 install gunicorn

How to run:

Nooo!
export FLASK_APP="app.main:create_app"
flask run

OR

python3 frontTest1.py

Yes!
sudo gunicorn -w 4 --reload -b localhost:5000 "app.main:create_app(testing=False)"
