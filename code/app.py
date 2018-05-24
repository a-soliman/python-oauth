from flask import Flask, request, jsonify
from flask import session as login_session
from flask_restful import Resource, Api, reqparse
# from flask_cors import CORS
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests
import random, string

# refrencing the client secret file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
# CORS(app)

#Allows Origin for the front end to interact.
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response
api = Api(app)


login_session_state = ''

class Login(Resource):
    def get(self):
        #define and generate session token and send it to the FE to save
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        login_session['state'] = state
        login_session_state = state
        response = {'state': login_session_state} 
        return response, 200

class Gconnect(Resource):
    
    def post(self):
        data = request.data
        args = json.loads(data)

        #check if data were passed
        if args['state'] is None or args['code'] is None:
            return {'success': False, 'Message': 'Invalid request.'}, 400

        # Collect the login data
        state = args['state']
        code = args['code']

        print(code)

        try:
            #upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
            access_token = credentials.access_token
            print("\n \n \n \n \n ================")
            print(access_token)
            print("\n \n \n \n \n ================")
    
        except FlowExchangeError:
            return {'Success': False, 'Message': 'Faild to upgrade the authorization code.'}, 401
        
        #Check that the access token is valid
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        
        # if there was an error in the access token info, abort
        if result.get('error') is not None:
            return {'Sucess': False, 'Message': result.get('error')}, 500

        # Verify that the access token is used for the intended user
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            return {'Success': False, 'Message': "Token's user ID dosn't match given user ID."}, 401

        # Verify that the access token is valid for this app
        if result['issued_to'] != CLIENT_ID:
            return {'Success': False, 'Message': "Token's client ID does not match app's"}, 401
        
        # Check to see if user is already logged in
        ''' Code this later '''

        # Store the access Token in the session for later use
        ''' Code this later '''

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': access_token}
        answer = requests.get(userinfo_url, params=params)
        data = json.loads(answer.text)

        # Store User info
        name = data['name']
        email = data['email']
        picture = data['picture']

        return { 'Success': True, 'name': name, 'email': email, 'picture': picture}

api.add_resource(Login, '/login')
api.add_resource(Gconnect, '/gconnect')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(port=5555, debug=True)