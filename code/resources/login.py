from flask import Flask, request, jsonify
from flask import session as login_session
from flask_restful import Resource, reqparse
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests
import random, string

# refrencing the client secret file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
    
class Login(Resource):
    login_session_state = None
    stored_access_token = ''
    stored_user = {"name": "", "username": "", "picture": ""}

    def get(self):
        #define and generate session token and send it to the FE to save
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        login_session['state'] = state
        Login.login_session_state =  state
        response = {'state': Login.login_session_state} 
        return response, 200
    
    def post(self):
        data = request.data
        args = json.loads(data)

        #check if data were passed
        if args['state'] is None or args['code'] is None:
            return {'success': False, 'Message': 'Invalid request.'}, 400

        # Collect the login data
        state = args['state']
        code = args['code']

        # Compare the state with the saved state
        if state != Login.login_session_state:
            return {'Success': False, 'Message': "Passed STATE doesn't match the session STATE"}, 401

        try:
            #upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
            access_token = credentials.access_token
    
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

        # Store the access Token in the session for later use
        Login.stored_access_token = access_token

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