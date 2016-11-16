import os
import json
from flask import Flask, request
from twilio.jwt.access_token import AccessToken, VoiceGrant
from twilio.rest import Client
import twilio.twiml

ACCOUNT_SID = 'AC64d6a7fa1eb934e5ed068f57e4ac16f9'
API_KEY = 'SK798c3d34afc34d650b1465606ccf640e'
API_KEY_SECRET = 'BM9ohnBeTGb3z9NJFGhsigG7TeDxhjCl'
PUSH_CREDENTIAL_SID = 'CR17e1e242557f010ad8739c0ccabe29bb'
APP_SID = 'AP5dadf62e0240fad9dc927308b7dadc46'
AUTH_TOKEN = 'e1b308b76f84d974c871bb87719249bc'
CONTAST_LIST = [{'userName': 'Twilio Demo 1'}, {'userName': 'Twilio Demo 2'}, {'userName': 'Twilio Demo 3'}, {'userName': 'Twilio Demo 4'}, {'userName': 'Twilio Demo 5'}, {'userName': 'Twilio Demo 6'}, {'userName': 'Twilio Demo 7'}, {'userName': 'Twilio Demo 8'}, {'userName': 'Twilio Demo 9'}, {'userName': 'Twilio Demo 10'}, {'userName': 'Twilio Demo 11'}, {'userName': 'Twilio Demo 12'}, {'userName': 'Twilio Demo 13'}, {'userName': 'Twilio Demo 14'}, {'userName': 'Twilio Demo 15'}]

IDENTITY = 'voice_test'
CALLER_ID = 'quick_start'

app = Flask(__name__)

@app.route('/accessToken', methods=['GET', 'POST'])
def token():
  client_name = request.values.get('client')
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)
  push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID", PUSH_CREDENTIAL_SID)
  app_sid = os.environ.get("APP_SID", APP_SID)
  if client_name:
     IDENTITY = client_name
  grant = VoiceGrant(
    push_credential_sid=push_credential_sid,
    outgoing_application_sid=app_sid
  )

  token = AccessToken(account_sid, api_key, api_key_secret, IDENTITY)
  token.add_grant(grant)

  return str(token)

@app.route('/outgoing', methods=['GET', 'POST'])
def outgoing():
  resp = twilio.twiml.Response()
  from_value = request.values.get('From')
  to = request.values.get('To')
  if not (from_value and to):
    resp.say("Invalid request")
    return str(resp)
  from_client = from_value.startswith('client')
  caller_id = os.environ.get("CALLER_ID", CALLER_ID)
  if not from_client:
    # PSTN -> client
    resp.dial(callerId=from_value).client(CLIENT)
  elif to.startswith("client:"):
    # client -> client
    resp.dial(callerId=from_value).client(to[7:])
  else:
    # client -> PSTN
    resp.dial(to, callerId=caller_id)
  # if call end or failed
  # resp.say("The call failed, or the remote party hung up. Goodbye.")
  return str(resp)

@app.route('/callLog', methods=['GET', 'POST'])
def callLog():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  client_name = request.values.get('client')
  result = []
  for call in client.calls.list(to="client:"+client_name):
    if call.direction != "inbound":
      tmp = {'from':call.from_formatted, 'to':call.to_formatted, 'status':call.status, 'duration':call.duration, 'starttime':str(call.start_time)}
      result.append(tmp)
  for call in client.calls.list(from_="client:"+client_name):
    if call.direction != "inbound":
      tmp = {'from':call.from_formatted, 'to':call.to_formatted, 'status':call.status, 'duration':call.duration, 'starttime':str(call.start_time)}
      result.append(tmp)
  k = {'Call': result}
  return json.dumps(k)

@app.route('/contactList', methods=['GET', 'POST'])
def contactList():
  return json.dumps({'contact': CONTAST_LIST})

@app.route('/', methods=['GET', 'POST'])
def welcome():
  resp = twilio.twiml.Response()
  resp.say("Welcome to Twilio")
  return str(resp)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
