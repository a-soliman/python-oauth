from flask import Flask, request, jsonify
from flask_restful import Api, reqparse

from resources.login import Login # this is where the OUATH functionality come from.

app = Flask(__name__)

#Allows Origin for the front end to interact.
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

api = Api(app)

api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(port=5555, debug=True)