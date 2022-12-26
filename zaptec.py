import requests
import json
from datetime import datetime,timedelta
from icecream import ic

zaptec_initalized = False
constants = None
observation_lookup = {}

class ZaptecAuth:
	def __init__(self,username,password):
		self.auth(username,password)
	
	def parse_auth_data(self, auth_data):
		self.auth_data = auth_data 
		#self.auth_expiry = datetime.strptime(auth_data['.expires'],"%a, %d %b %Y %H:%M:%S %Z")
		self.auth_expiry = datetime.now() + timedelta(seconds=int(auth_data['expires_in'])) 
		self._auth_header = {'Authorization': 'Bearer ' + auth_data['access_token']}
	
	def auth(self,username,password):
		payload = { 
			'grant_type': 'password',
			'username': username,
			'password': password
		}

		r = requests.post('https://api.zaptec.com/oauth/token', data=payload)

		self.parse_auth_data(json.loads(r.text))

		return self

	def expired(self):
		return datetime.now() > self.auth_expiry

	@property
	def auth_header(self):
		if(self.expired()):
			self.auth()
		
		return self._auth_header

def init():
	global zaptec_initalized
	if zaptec_initalized:
		return True

	parse_constants()

	zaptec_initalized = True

def parse_constants():
	r = requests.get('https://api.zaptec.com/api/constants')
	
	constants = json.loads(r.text)

	for observation,value in constants['Observations'].items():
		observation_lookup[value] = observation

def auth(username,password):
	return ZaptecAuth(username,password)

def lookup_observation(observation):
	if(observation in observation_lookup):
		return observation_lookup[observation]
	else:
		return observation

init()
