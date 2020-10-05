from flask import session
import requests
import json

# The utilities will be used later on..

settings = json.load(open(f'{os.getcwd()}/conf/siteSettings.json'))

    def checkTokensAndRefresh2():
        print("aToken alussa:")
        print(session.get("aToken"))
        print("rToken alussa:")
        print(session.get("rToken"))
        headerForTokenTesting = settings['commonHeader']; headerForTokenTesting.update({"Authorization": session.get("aToken")}); responseForTokenTesting = requests.put('http://localhost:8080/api/suggestions/1/status/RECEIVED', headers=headerForTokenTesting)
        print(responseForTokenTesting.text)
        if '202' not in responseForTokenTesting.text:
            print("ei ole tokeneita")
            urlForRefresh = "http://localhost:8080/api/refresh"; headersForRefresh = settings['commonHeader']; headersForRefresh.update({'Authorization' : 'Bearer ' + session.get("rToken")}); dataForRefresh = {"refresh_token": session.get("rToken")}
            responseForRefresh = requests.post(urlForRefresh, data=json.dumps(dataForRefresh), headers=headersForRefresh).text
            seedDataForReLogin=json.loads(responseForRefresh)
            session['aToken'] = 'Bearer ' + seedDataForReLogin['access_token']
            session['rToken'] = seedDataForReLogin['refresh_token']
        else:
            print("Tokens are valid")
        print("aToken lopussa:")
        print(session.get("aToken"))
        print("rToken alussa:")
        print(session.get("rToken"))
        return None
