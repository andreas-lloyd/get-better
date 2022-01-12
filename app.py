# Refer to https://developers.google.com/identity/protocols/oauth2/web-server
import os

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
import  google.oauth2.credentials
import googleapiclient.discovery
import flask

import config

# Set up the environment
load_dotenv()

HOSTNAME = os.environ.get('HOSTNAME', 'localhost')
PORT = int(os.environ.get('PORT', 8080))
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

if DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

KEY_CREDENTIALS = 'credentials'

# Define some Google helpers
def identify_app(redirect_uri, state=None):
    """ Identify what the app is and wat it wants to do in preparation for the authorisation request. 
    
    Returns app flow that we request authorisation with
    """
    flow = Flow.from_client_secrets_file(config.GOOGLE_APP_SECRET_LOC, scopes=config.SCOPES, state=state)
    flow.redirect_uri = redirect_uri

    return flow

def authorise_app(flow):
    """ Now we request the authorisation URL from Google after we have authorised. 
    We have to re-direct them to this URL where they will authorise the scopes we asked for.

    Returns authorisation URL to redirect to and state
    """
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    return authorization_url, state

def build_api(credentials):
    """ Build the gmail api to work with, given we have the access credentials 
    
    Returns an api object
    """
    return googleapiclient.discovery.build(config.API_SERVICE_NAME, config.API_VERSION, credentials=credentials)

# Some flask helpers
def check_authorised():
    return KEY_CREDENTIALS in flask.session

def save_credentials(credentials):
    flask.session[KEY_CREDENTIALS] = credentials_to_dict(credentials)

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

# Summary helpers
def summarise_emails(gmail):
    threads = gmail.users().threads().list(userId='me').execute()
    num_threads = threads['resultSizeEstimate']

    while 'nextPageToken' in threads:
        threads = gmail.users().threads().list(userId='me', pageToken=threads['nextPageToken']).execute()
        num_threads += threads['resultSizeEstimate']
    
    summary = f'You have {num_threads} email threads'
    return summary


# Define the Flask app
app = flask.Flask(__name__)
app.secret_key = 'secret'

@app.route('/')
def index():
    """ The index - reroute to authorise if not already so. """
    if check_authorised():
        return '<p>Hello and welcome to the email summariser - if you want to summarise your email click <a href="/summarise">here</a></p>'
    else:
        return flask.redirect('authorize')

@app.route('/summarise')
def summarise():
    """ This is where we actually access the email and summarise what is going on. """
    if not check_authorised():
        return flask.redirect('authorize')
    
    # First thing is to load in the credentials that we have saved
    credentials = google.oauth2.credentials.Credentials(**flask.session[KEY_CREDENTIALS])

    # Now actually get the gmail api
    gmail = build_api(credentials)

    # And resave credentials in case they changed
    save_credentials(credentials)

    # Now do something with the api
    summary = summarise_emails(gmail)

    return f'<p>{summary}</p>'


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
    save_credentials(credentials)

    # And send them back to where we want them to go
    return flask.redirect(flask.url_for('index'))

if __name__ == '__main__':
    app.run(HOSTNAME, PORT, debug=DEBUG)