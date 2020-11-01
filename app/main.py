from flask import Flask, redirect, url_for, render_template, request, session
from itertools import chain
import requests
import json
import os
# import re


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

    @app.route("/suggestionlisting/<sorting>/<filters>/<searchString>")
    def suggestion_list(sorting, filters, searchString):
        # Testing area
        statusUrl = f'{baseURL}suggestions/1/status/RECEIVED'
        changeTheStatusAsATest('PUT', statusUrl)

        # Use the next following url information to compose a comprehensive comment section
        # http://localhost:5000/suggestionlisting/DEFAULT/tluafed/tluafed
        # http://localhost:8080/suggestions/?filters=status:received|type:new|tags:slm musiikki&search=sovit&sort=CREATED_ASC
        # http://localhost:8080/suggestions/?filters=status%3Areceived%7Ctype%3Anew%7Ctags%3Aslm%08musiikki&search=sovit&sort=CREATED_ASC
        # noArguments
        # noSearchStringSubmitted
        isSearch = False
        if 'tluafed' not in searchString and 'noSearchStringSubmitted' not in searchString:
            isSearch = True
            searchString = f'&search={searchString}'
        else:
            searchString = ''
            filtersForUrl = ''
        isFilter = False
        if 'tluafed' not in filters and 'noArguments' not in filters:
            isFilter = True
            filtersForUrl = '&filters='
            if 'a:' in filters:
                filtersForUrl = filtersForUrl + 'status%3A' + filters[filters.find('a:')+len('a:'):filters.rfind('|')].lower()
            if 'b:' in filters:
                filtersForUrl = filtersForUrl + '%7Ctype%3A' + filters[filters.find('b:')+len('b:'):filters.rfind('¤')].lower()
            if '*' in filters:
                filtersForUrl = filtersForUrl + '%7Ctags%3A' + filters.partition('*')[2].replace('*','%08').lower()
        else:
            print("oli tluafed tai noArguments filtersissä")

        tempArray = []
        if 'DEFAULT' in sorting:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25')
        elif 'CREATED_DESC' in sorting:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25{filtersForUrl}{searchString}&sort=CREATED_DESC')
        elif 'CREATED_ASC' in sorting:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25{filtersForUrl}{searchString}&sort=CREATED_ASC')
        elif 'COMMENTS_DESC' in sorting:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25{filtersForUrl}{searchString}&sort=COMMENTS_DESC')
        elif 'COMMENTS_ASC' in sorting:
            responseForAll = requests.get(f'{baseURL}suggestions?limit=25{filtersForUrl}{searchString}&sort=COMMENTS_ASC')
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

        labelListFromBE = json.loads(requests.get(f'{baseURL}tags').text)['data']
        labelListForTheModel = []
        for labelDict in labelListFromBE:
            labelListForTheModel.append(labelDict['label'])

        return render_template("index.html", response=tempArray, sortingAtThePage=sorting, labelList=labelListForTheModel)

    @app.route("/testurl")
    def common_tester_for_developers():
        headerForAPITesting = settings['commonHeader']; headerForAPITesting.update({"Authorization": session.get("aToken")}); responseForAPITesting = requests.put('http://localhost:8080/api/suggestions/1/status/RECEIVED', headers=headerForAPITesting)
        print('Checking and maintaining the authorization: \n' + responseForAPITesting.text)
        testing = True
        return f'Checking and maintaining the authorization: {responseForAPITesting.text}'

    @app.route("/suggestion/<suggestionId>", methods=["POST", "GET"])
    def suggestion(suggestionId):
        allData = json.loads(requests.get(f'{baseURL}suggestions/{suggestionId}').text)['data']
        alternativeLabels = {}
        langPrefLabelsDict = {}
        prefLabelsArray = []
        preferredLabel = allData['preferred_label']
        if 'fi' in preferredLabel:
            langPrefLabelsDict['finnish'] = allData['preferred_label']['fi']['value']
        if 'sv' in preferredLabel:
            langPrefLabelsDict['swedish'] = allData['preferred_label']['sv']['value']
        if 'en' in preferredLabel:
            langPrefLabelsDict['english'] = allData['preferred_label']['en']['value']
        prefLabelsArray.append(langPrefLabelsDict)
        tagsForSug = allData['tags']
        alternativeLabels = allData['alternative_labels']
        broaderLabels = allData['broader_labels']
        creat = allData['created']
        modif = allData['modified']
        desc = allData['description']
        events = allData['events']
        commentsToBeShownInFront = []
        comments = {}
        for event in events:
            if 'COMMENT' in event['event_type']:
                comments['created'] = event['created']
                comments['text'] = event['text']
                comments['value'] = event['value']
                comments['user_id'] = event['user_id']
                comments['reactions'] = event['reactions']
                comments['tags'] = event['tags']
                commentsToBeShownInFront.append(comments)
        return render_template("suggestion.html",
        prefLabels = prefLabelsArray,
        suggestionId=suggestionId,
        altLabels = alternativeLabels,
        brdLabels = broaderLabels,
        created = creat,
        modified = modif,
        description = desc,
        eves = events,
        commentsToBeShown = commentsToBeShownInFront,
        tagsForSugInFront = tagsForSug,
        )

    @app.route("/login/", methods=['GET', 'POST'])
    def login():
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

    def refresh_tokens_if_not_202(original_function):
        def wrapper_function(*args, **kwargs):
            if len(session.get("aToken")) > 100:
                if '202' not in original_function(*args, **kwargs):
                    print("No valid tokens")
                    urlForRefresh = "http://localhost:8080/api/refresh"
                    headersForRefresh = settings['commonHeader']
                    headersForRefresh.update({'Authorization' : 'Bearer ' + session.get("rToken")})
                    dataForRefresh = {"refresh_token": session.get("rToken")}
                    responseForRefresh = requests.post(urlForRefresh, data=json.dumps(dataForRefresh), headers=headersForRefresh).text
                    print(responseForRefresh)
                    seedDataForReLogin=json.loads(responseForRefresh)
                    session['aToken'] = 'Bearer ' + seedDataForReLogin['access_token']
                    print("After the check: access_token / refresh_token"); print(session.get("aToken"))
                    print(session.get("rToken"))
                else:
                    print("Tokens are valid")
            else:
                print("No tokens found. The function cannot be run")
            return original_function(*args, **kwargs)
        return wrapper_function

    @refresh_tokens_if_not_202
    def changeTheStatusAsATest(method, url):
        responseForTokenTesting = requests.request(method, url)
        return responseForTokenTesting

    return app
