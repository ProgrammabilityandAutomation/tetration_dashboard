#!/usr/bin/env python2.7
import httplib2,subprocess,requests,os
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()


ACI_host = #<set ACI host IP here> 
protocol = "http"
os.environ['no_proxy'] = ACI_host

def checkandupdate(sdk):
	if "aci"+sdk in file.get("href"):
		new_version = file.get("href")
		installed_version = subprocess.check_output("pip show aci"+sdk+" |grep Location |awk -F'/' '{print $NF}'", shell=True).strip(' \t\n\r')
		if new_version != installed_version:
			print("moving from "+installed_version+" to "+new_version)
			subprocess.check_output("curl --insecure -O "+url+file.get("href"),shell=True)
			if installed_version != '':
				subprocess.check_output("pip uninstall -y aci"+sdk, shell=True)
			subprocess.check_output("easy_install -Z ./"+new_version, shell=True)
			subprocess.check_output("rm -f ./"+new_version, shell=True)
		else:
			print("ACI "+sdk+" is up to date: "+new_version)

http = httplib2.Http(disable_ssl_certificate_validation=True)
url = protocol+"://"+ACI_host+"/cobra/_downloads/"
response, content = http.request(url)
if int(response['status']) != 200:
	print "Return code "+response['status']+" --> Error on operation "+opName+", with data: "+opData
	print "Full response: "+response
	print "Full content: "+content
	sys.exit(1)

soup = BeautifulSoup(content, "html.parser")

for acisdk in ["cobra", "model"]:
	for file in soup.find_all("a"):
		checkandupdate(acisdk)
