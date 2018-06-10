#!/usr/bin/env python2.7

import os,sys,requests,json
requests.packages.urllib3.disable_warnings()
from cobra.mit.session import LoginSession
from cobra.mit.access import MoDirectory
from cobra.mit.request import ClassQuery,DnQuery

from configparser import SafeConfigParser
parser = SafeConfigParser()
parser.read(sys.argv[1])

# APIC Credentials
APIC_IP = parser.get('ACI', 'IP')
APIC_Username = parser.get('ACI', 'username')
APIC_Password = parser.get('ACI', 'password')
APIC_Proto = parser.get('ACI', 'protocol')
EPGs = parser.get('ACI', 'EPG_list').split()
os.environ['no_proxy'] = APIC_IP

Login_Session = LoginSession(APIC_Proto+'://'+APIC_IP, APIC_Username, APIC_Password)
moDir = MoDirectory(Login_Session)
moDir.login()

fabric_health = []
getInfo = ClassQuery('fabricHealthTotal')
FabricHealth = moDir.query(getInfo)
for obj in FabricHealth:
	if str(obj.dn) == "topology/health":
		fabric_health.append({"Global" : int(obj.cur)})
	else:
		fabric_health.append({str(obj.dn).replace("topology/","").replace("/health","") : int(obj.cur)})

EPGs_health = []
for EPG_dn in EPGs:
	getInfo = DnQuery('uni/'+EPG_dn+'/health')
	EPGHealth = moDir.query(getInfo)
	for obj in EPGHealth:
		# I only keep EPG name, to avoid a long string in the dashboard...
		EPGs_health.append({EPG_dn.split('/')[-1].replace("epg-","") : int(obj.cur)})

data = {}
data['fabric_health'] = fabric_health
data['EPGs_health'] = EPGs_health

print(json.dumps(data))

moDir.logout()
