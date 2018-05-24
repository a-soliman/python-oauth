from flask import Flask, request, jsonify
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests
import random, string

# refrencing the client secret file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

@app.route('/login')
def showLogin():
    #define and generate session token and send it to the FE to save
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    response = {'state': state} 
    return jsonify(response)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # parse the sesstion token
    if request.json['session_state']:
        client_session_state = request.json['session_state']
    else:
        response = {'message': 'Invalid Request, No session state detected.'}
        return jsonify(response), 401
        
    # check if the session token is correct and up to date
    if client_session_state != login_session['state']:
        response = {'message': 'Invalid state parameters'}
        return jsonify(response), 401

    # Collect the login data
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_url = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = {'message': 'Failed to upgrade the authorization code'}
        return jsonify(response), 401
    
    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = {'message': result.get('error')}
        return jsonify(response), 500
    
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['used_id'] != gplus_id:
        response = {'message': 'Token user ID dos not match given user ID.'}
        return jsonify(response), 401
    
    # Check if the user is already logged in
    '''
        Complete later
    '''

    # Store the access token in the session for later user.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    response = {"success": "true", "email": login_session['email'], "username": login_session['username'], "picture": login_session['picture']}
    return response, 200




@app.route('/')
def get_home():
    return 'Hello there'


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(port=5555, debug=True)