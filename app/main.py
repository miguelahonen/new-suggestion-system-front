from flask import Flask, redirect, url_for, render_template, request, session
import requests
import json
import os


def create_app(testing: bool = True):
    app = Flask(__name__, template_folder='../templates')
    settings = json.load(open(f'{os.getcwd()}/conf/siteSettings.json')) # Check if the opened file should be closed
    baseURL = settings['apiBasePath']
    app.secret_key = str(settings['secretKey'])

    @app.route("/")
    def index():
        testing = True
        return f'Will be a main page: {testing}'
        # return render_template("index.html", testing=testing)

    @app.route("/suggestionlisting/<sorting>")
    def suggestion_list(sorting):
# f'{baseURL}users'
        tempArray = []
        if 'DEFAULT' in sorting:
            # responseForAll = requests.get(f'{baseURL}suggestions?limit=25&search=bell')
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25')
        elif 'CREATED_DESC' in sorting:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25&sort=CREATED_DESC')
        elif 'CREATED_ASC' in sorting:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25&sort=CREATED_ASC')
        elif 'COMMENTS_DESC' in sorting:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25&sort=COMMENTS_DESC')
        elif 'COMMENTS_ASC' in sorting:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25&sort=COMMENTS_ASC')
        else:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25')

        seedData=json.loads(responseForAll.text)
        for suggestion in seedData['data']:
            tempDict = {}
            # tempDict['entire'] = suggestion
            tempDict['id'] = suggestion['id']
            tempDict['created'] = suggestion['created']
            tempDict['modified'] = suggestion['modified']
            tempDict['description'] = suggestion['description']
            # tempDict['exactMatches'] = suggestion['exactMatches']
            tempDict['events'] = suggestion['events']
            tempDict['preferred_labels'] = suggestion['preferred_label']
            tempArray.append(tempDict)
        return render_template("index.html", response=tempArray,
        sortingAtThePage=sorting)
        # textBoxForComment="hei")

    @app.route("/testurl")
    def common_tester_for_developers():
        checkTokensAndRefresh(True)
        headerForAPITesting = settings['commonHeader']; headerForAPITesting.update({"Authorization": session.get("aToken")}); responseForAPITesting = requests.put('http://localhost:8080/api/suggestions/1/status/RECEIVED', headers=headerForAPITesting)
        print('Just for test purposes:\n' + responseForAPITesting.text)

        testing = True
        return f'Just for test purposes: {responseForAPITesting.text}'

    @app.route("/login/", methods=['GET', 'POST'])
    def login():
        # utilities.checkTokensAndRefresh2()
        print(request.form.getlist("newUser"))
        if request.method == "POST":
            # Logout: Uses API Enpoint /logout
            # Payload (dataForLogout) must carry both tokens (access_token without Bearer prefix)
            # Header (headerForLogout) needs "Content-type": "application/json", "Accept": "application/json", "Authorization": access_token
            # After the POST, errors and notifications will be passed to the template via the tokens
            # Result: The user is successfully logged out with the dropped tokens
            if 'logout' in request.form.getlist("logout"):
                dataForLogout = {"access_token": str(session.get("aToken")).replace("Bearer ",""),
                "refresh_token": session.get("rToken")}
                headerForLogout = settings['headerForLogin']
                headerForLogout.update({"Authorization": session.get("aToken")})
                seedDataForLogout=requests.post(f'{baseURL}logout', data=json.dumps(dataForLogout),    headers=headerForLogout)
                if '200' in seedDataForLogout.text:
                    session["aToken"], session["rToken"] = ('tokenNotUsedAnymore','tokenNotUsedAnymore')
                else:
                    session["aToken"], session["rToken"] = ('couldNotExpireTheToken', 'couldNotExpireTheToken')
                return render_template("login.html", access=session.get("aToken"), refresh=session.get("rToken"))
            # Login: Uses API Enpoint /login
            # Payload (dataForLogin) must carry the username and password
            # Header (headerForLogin) needs "Content-type": "application/json", "Accept": "application/json"
            # After the POST, new tokens are created (in the session) or errors are passed to the template via the tokens
            # Result: The user is successfully logged in with new tokens in session
            elif 'login' in request.form.getlist("login"):
                dataForLogin = {"email": str(request.form.getlist("userName"))[2:-2],
                "password": str(request.form.getlist("passWord"))[2:-2]}
                seedDataForLogin=json.loads(requests.post(f'{baseURL}login', data=json.dumps(dataForLogin),       headers=settings['headerForLogin']).text)
                if seedDataForLogin['code'] == 200:
                    session["aToken"], session["rToken"] = (f'Bearer {seedDataForLogin["access_token"]}', seedDataForLogin['refresh_token'])
                else:
                    session["aToken"], session["rToken"] =('tokenError', 'tokenError')
                return render_template("login.html", access=session.get("aToken"), refresh=session.get("rToken"))
            elif 'newUser' in request.form.getlist("newUser"):
            # Login: Uses API Enpoint /users
            # Payload (dataForLogin) must carry at least the username (email), name and password
            # Header (headerForLogin) needs "Content-type": "application/json", "Accept": "application/json"
            # After the POST, a new user will be created or errors are passed to the template via the tokens
            # Result: The user is successfully created and the user can log in
                print("Testi")
                dataForNewUser = {}
                dataForNewUser.update({"email": str(request.form.getlist("userName"))[2:-2]})
                dataForNewUser.update({"imageUrl": str(request.form.getlist("imageUrl"))[2:-2] if session.get("imageUrl") != "" else ""})
                dataForNewUser.update({"name": str(request.form.getlist("name"))[2:-2]})
                dataForNewUser.update({"organization": str(request.form.getlist("organization"))[2:-2] if session.get("organization") != "" else ""})
                dataForNewUser.update({"password": str(request.form.getlist("password"))[2:-2]})
                dataForNewUser.update({"title": str(request.form.getlist("title"))[2:-2] if session.get("title") != "" else ""})
                print(dataForNewUser)
                headerForNewUser = settings['headerForRegistration']
                seedDataForNewUser=requests.post(f'{baseURL}users', data=json.dumps(dataForNewUser),    headers=headerForNewUser)
                if '201' in seedDataForNewUser.text:
                    session["aToken"], session["rToken"] = ('userRegistrationSucceed','userRegistrationSucceed')
                else:
                    session["aToken"], session["rToken"] = ('userRegistrationFailed', 'userRegistrationFailed')
                return render_template("login.html", access=session.get("aToken"), refresh=session.get("rToken"))
            else:
                return render_template("login.html", access='LoginOperationFailed', refresh='LoginOperationFailed')
        else:
            return render_template("login.html", access='userCredentialsOperationFailed', refresh='userCredentialsOperationFailed')

    def checkTokensAndRefresh(writeALog = False):
        # The function is used to check whether the access_token is expired or if the user is allowed to perform actions in API
        # The function is used every time you use POST, PUT or PATCH API calls
        # If the access_token is expired, the refresh_token is used to get a new access_token
        if len(session.get("aToken")) > 100:
            if writeALog == True:
                print("Before the check: access_token / refresh_token"); print(session.get("aToken")); print(session.get("rToken"))
            headerForTokenTesting = settings['commonHeader']; headerForTokenTesting.update({"Authorization": session.get("aToken")}); responseForTokenTesting = requests.put('http://localhost:8080/api/suggestions/1/status/RECEIVED', headers=headerForTokenTesting)
            if '202' not in responseForTokenTesting.text:
                print("No valid tokens")
                urlForRefresh = "http://localhost:8080/api/refresh"; headersForRefresh = settings['commonHeader']; headersForRefresh.update({'Authorization' : 'Bearer ' + session.get("rToken")}); dataForRefresh = {"refresh_token": session.get("rToken")}
                responseForRefresh = requests.post(urlForRefresh, data=json.dumps(dataForRefresh), headers=headersForRefresh).text
                seedDataForReLogin=json.loads(responseForRefresh)
                session['aToken'] = 'Bearer ' + seedDataForReLogin['access_token']
            else:
                print("Tokens are valid")
            if writeALog == True:
                print("After the check: access_token / refresh_token"); print(session.get("aToken")); print(session.get("rToken"))
            return None
        else:
            print("No tokens found")

    # @app.route("/nimi/<name>")
    # def test(name):
    #     print(baseURL)
    #     return render_template("index.html", name=name)

    return app
