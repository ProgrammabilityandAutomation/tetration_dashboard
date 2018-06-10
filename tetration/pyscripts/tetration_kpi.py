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

# All durations are converted from µs to ms.
def collection_avg(coll):
	coll_sum = sum(coll)
	coll_len = len(coll)
	if coll_len == 0:
		return 0.0
	else:
		return round(coll_sum/coll_len/1000,1)

# Open connection to TA API
rc = RestClient(API_ENDPOINT, credentials_file = API_CREDENTIALS, verify=False)

timestamp = sys.argv[2]

# We will have to do some paginated requests as API is limited to 5k observations / query
loop = True
offset = 0

# Initialization of counters
srtt_collection = list()
app_latency_collection = list()		
net_latency_collection = list()
handshake_collection = list()
net_const_obs = 0
app_const_obs = 0
rst_count = 0
syn_count = 0
retransmits = 0
packets = 0
obs = 0

while loop:
	print("JP loop")
	if offset == 0:
		req_payload = {
		"t0": timestamp,
		"t1": ""+(datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:00.000Z') + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:00.000Z")+"",
		"filter": {},
		"scopeName" : SCOPE,
		"metrics" : ['fwd_tcp_bottleneck', 'rev_tcp_bottleneck','fwd_rst_count','rev_rst_count','fwd_syn_count','fwd_tcp_pkts_retransmitted','rev_tcp_pkts_retransmitted','fwd_pkts','rev_pkts','fwd_tcp_handshake_usec','srtt_usec','server_app_latency_usec','total_network_latency_usec'],
		}
	else:
		req_payload = {
		"t0": timestamp,
		"t1": ""+(datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:00.000Z') + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:00.000Z")+"",
		"filter": {},
		"scopeName" : SCOPE,
		"metrics" : ['fwd_tcp_bottleneck', 'rev_tcp_bottleneck','fwd_rst_count','rev_rst_count','fwd_syn_count','fwd_tcp_pkts_retransmitted','rev_tcp_pkts_retransmitted','fwd_pkts','rev_pkts','fwd_tcp_handshake_usec','srtt_usec','server_app_latency_usec','total_network_latency_usec'],
		"offset" : offset               	
		}
	#print(req_payload)
	try:
		resp = rc.post('/flowsearch', json_body=json.dumps(req_payload))
	except:
		raw_input("Connection to Tetration Cluster API faild. Please ensure connectivity, check credentials and hit enter/return to try again.")

	#print("tetration API response to console for debug")
	#print( "   Tetration API response: " + str(resp))

	if resp.status_code == 200:
		#print TA json response for debug
		#print(resp.content)

		result = json.loads(resp.content.decode("utf-8"))

		if(result['results'] == None):
			print("No result")
			sys.exit(1)
		else:
			if "offset" in result:
				offset = result['offset']
			else:
				loop = False
			for r in result['results']:
				if int(r["srtt_usec"]) != 0:
					srtt_collection.append(r["srtt_usec"])
				if int(r["server_app_latency_usec"]) != 0:
					app_latency_collection.append(r["server_app_latency_usec"])
				if int(r["total_network_latency_usec"]) != 0:
					net_latency_collection.append(r["total_network_latency_usec"])
				if int(r["fwd_tcp_handshake_usec"]) != 0:
					handshake_collection.append(r["fwd_tcp_handshake_usec"])
				if r["rev_tcp_bottleneck"] == "BOTTLENECK_NETWORK" or r["fwd_tcp_bottleneck"] == "BOTTLENECK_NETWORK":
					net_const_obs+=1
				if r["rev_tcp_bottleneck"] == "BOTTLENECK_APP" or r["fwd_tcp_bottleneck"] == "BOTTLENECK_APP":
					app_const_obs+=1
				if r["rev_tcp_bottleneck"] == "BOTTLENECK_BOTH" or r["fwd_tcp_bottleneck"] == "BOTTLENECK_BOTH":
					app_const_obs+=1
					net_const_obs+=1

				rst_count += (r["rev_rst_count"]+r["fwd_rst_count"])
				syn_count += r["fwd_syn_count"]

				retransmits += (r["rev_tcp_pkts_retransmitted"]+r["fwd_tcp_pkts_retransmitted"])
				packets += (r["rev_pkts"]+r["fwd_pkts"])

			obs += len(result['results'])

	else:
		print("response code was "+str(resp.status_code))
		sys.exit(2)

# All durations are converted from µs to ms.
srtt_avg = collection_avg(srtt_collection)
if srtt_avg != 0:
	srtt_max = round(max(srtt_collection)/1000,1)
else:
	srtt_max = 0.0

#This will be in msecs becasue of conversion
app_avg = collection_avg(app_latency_collection)
if app_avg != 0:
        # msecs here
	app_max = round(max(app_latency_collection)/1000,1)
	print("JP", app_latency_collection)
else:
	app_max = 0.0

net_avg = collection_avg(net_latency_collection)
if net_avg != 0:
	net_max = round(max(net_latency_collection)/1000,1)
else:
	net_max = 0.0

handshake_avg = collection_avg(handshake_collection)
if handshake_avg != 0:
	handshake_max = round(max(handshake_collection)/1000,1)
else:
	handshake_max = 0.0

data = {}
data['timestamp'] = result['results'][0]['timestamp']
data['obs_count'] = obs
data['srtt_avg'] = srtt_avg
data['srtt_max'] = srtt_max
data['app_avg'] = app_avg
data['app_max'] = app_max
data['net_avg'] = net_avg
data['net_max'] = net_max
data['handshake_avg'] = handshake_avg
data['handshake_max'] = handshake_max
data['retransmits'] = retransmits
data['packets'] = packets
data['app_const_obs'] = app_const_obs
data['net_const_obs'] = net_const_obs
data['syn_count'] = syn_count
data['rst_count'] = rst_count

print(json.dumps(data))
