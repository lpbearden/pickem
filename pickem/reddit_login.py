#!/usr/bin/env python
from flask import abort, request
from uuid import uuid4
from pickem import app
import requests
import urllib.parse
import json
import logging

logging.basicConfig(filename="sample.log", level=logging.INFO)

REDIRECT_URI = "http://localhost:65010/reddit_callback"

def get_keys():
    logging.info("In get keys")
    with open('pickem/config.json') as data_file:
        data = json.load(data_file)
    global CLIENT_SECRET, CLIENT_ID
    CLIENT_SECRET = data["client-secret"]
    CLIENT_ID = data["client-id"]


def user_agent():
    '''reddit API clients should each have their own, unique user-agent
    Ideally, with contact info included.

    e.g.,
    return "oauth2-sample-app by /u/%s" % your_reddit_username

    '''
    return "oauth2-sample-app by /u/ogagent"


def base_headers():
    return {"User-Agent": user_agent()}


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    logging.info("In make_authorization_url, calling get_keys()")
    get_keys()
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI,
              "duration": "temporary",
              "scope": "identity"}
    url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.parse.urlencode(params)
    return url


# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache.
def save_created_state(state):
    pass


def is_valid_state(state):
    return True


@app.route('/reddit_callback')
def reddit_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    access_token = get_token(code)
    # Note: In most cases, you'll want to store the access token, in, say,
    # a session for use in other parts of your web app.
    return "Your reddit username is: %s" % get_username(access_token)


def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = base_headers()
    response = requests.post("https://ssl.reddit.com/api/v1/access_token",
                             auth=client_auth,
                             headers=headers,
                             data=post_data)
    token_json = response.json()
    return token_json["access_token"]


def get_username(access_token):
    headers = base_headers()
    headers.update({"Authorization": "bearer " + access_token})
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    me_json = response.json()
    return me_json['name']


