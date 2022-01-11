# Refer to https://developers.google.com/identity/protocols/oauth2/web-server
import os

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
import flask

import config

# Set up the environment
load_dotenv()

# Define some Google helpers
def identify_app(redirect_uri, state=None):
    """ Identify what the app is and wat it wants to do in preparation for the authorisation request. """
    flow = Flow.from_client_secrets_file(config.google_app_secret_loc, scopes=config.scopes, state=state)
    flow.redirect_uri = redirect_uri

    return flow

def authorise_app(flow):
    """ Now we request the authorisation URL from Google after we have authorised. 
    We have to re-direct them to this URL where they will authorise the scopes we asked for.
    """
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    return authorization_url, state

# Some flask helpers
def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

# Define the Flask app
app = flask.Flask(__name__)
app.secret_key = 'secret'

@app.route('/authorize')
def authorize():
    """ This is where we route the user to to request authorisation. """
    redirect_uri = flask.url_for('oauth2callback', _external=True)
    flow = identify_app(redirect_uri)

    authorization_url, state = authorise_app(flow)

    flask.session['state'] = state

    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    """ Now we define the callback for the redirection and actually get the access tokens. """
    redirect_uri = flask.url_for('oauth2callback', _external=True)
    flow = identify_app(redirect_uri, state=flask.session['state'])

    # Now use the response we got from the authorisation request
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # And save in our session for use later (should save to database in reality)
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    # And send them back to where we want them to go
    return flask.redirect(flask.url_for('index'))

# todo:
# define index
# check out other bits in google example
# test out app (run flask app)

print('Done!')