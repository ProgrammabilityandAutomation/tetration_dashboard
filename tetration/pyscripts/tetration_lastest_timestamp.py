#!/usr/bin/env python3
import sys,json,urllib3
#urllib3.disable_warnings()

from datetime import datetime, timedelta
from tetpyclient import RestClient
from configparser import SafeConfigParser

parser = SafeConfigParser()
parser.read(sys.argv[1])

API_ENDPOINT=parser.get('TA', 'API_ENDPOINT')
API_CREDENTIALS=parser.get('TA', 'API_CREDENTIALS')
SCOPE=parser.get('TA', 'SCOPE')

# How far should we look back to get at least 1 timestamp? Should be > pipeline latency
MINUTES_BACK = 20

# Open connection to TA API
rc = RestClient(API_ENDPOINT, credentials_file = API_CREDENTIALS, verify=False)

t1 = datetime.utcnow()
t0 = t1 - timedelta(minutes=MINUTES_BACK)

req_payload = {
"t0": "" + t0.strftime("%Y-%m-%dT%H:%M:%S+00:00") + "",
"t1": "" + t1.strftime("%Y-%m-%dT%H:%M:%S+00:00") + "",
"filter": {},
"scopeName" : SCOPE,
"metrics" : [],
"limit" : 1,
"descending" : True
}
#print(req_payload)

try:
	resp = rc.post('/flowsearch', json_body=json.dumps(req_payload))
except:
	raw_input("Connection to Tetration Cluster API faild. Please ensure connectivity, check credentials and hit enter/return to try again.")

#print tetration API response to console for debug
#print("   Tetration API response: " + str(resp))

if resp.status_code == 200:
	#print TA json response for debug
	#print(resp.content)
	result = json.loads(resp.content.decode("utf-8"))

	if(result['results'] == None):
		print("No result")
		sys.exit(1)
	else:
		data = {}
		data['timestamp'] = result['results'][0]['timestamp']

else:
	print("response code was "+str(resp.status_code))
	sys.exit(2)

print(json.dumps(data))
