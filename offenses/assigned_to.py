#!/usr/bin/env python3
# usage: assigned_to.py -u MYUSERID
#        assigned_to.py -u UNASSIGNED
import json, os, sys, importlib, optparse

sys.path.append(os.path.realpath('../modules'))
client_module = importlib.import_module('RestApiClient')
SampleUtilities = importlib.import_module('SampleUtilities')

columnpadding_id=6
columnpadding_userid=6
type_srcip=0
type_srcip_name="SrcIP"
type_dstip=1
type_dstip_name="DstIP"
type_user=3
type_user_name="User "
base_url="siem/offenses"
columns='''id,status,description,offense_type,offense_source,assigned_to'''

class Offense:
	def __init__(self,id,status,description,type,source,assigned_to):
		self.id=id
		self.status=status
		self.description=description
		self.type=type
		self.source=source
		self.assigned_to=assigned_to
	@staticmethod
	def object_decoder(obj):
		return Offense(obj['id'], obj['status'], obj['description'], obj['offense_type'], obj['offense_source'], obj['assigned_to'])

def build_api_call(userid):
	assigned_to_filter="assigned_to%20is%20null" if userid=="UNASSIGNED" else "assigned_to=" + userid
	status_filter="status=OPEN"
	filter="{0}%20and%20{1}".format(status_filter, assigned_to_filter)
	api_call = "{0}?fields={1}&filter={2}".format(base_url, columns, filter)
	return api_call

def query_api(userid):
	client = client_module.RestApiClient(version='5.0')
	response = client.call_api(build_api_call(userid), 'GET')

	if (response.code != 200):
		print('Failed to query api')
		SampleUtilities.pretty_print_response(response)
		sys.exit(1)
	
	return response.read().decode('utf-8')

def load_offenses(api_response):
	offenses = json.loads(api_response, object_hook=Offense.object_decoder)
	offenses.sort(key=lambda x: x.id, reverse=True)
	return offenses

def print_offenses(offenses):
	for offense in offenses:
		if offense.assigned_to == "None":
			offense.assigned_to = ""
		if offense.type == type_srcip:
			print("id:{0} [{1}] {2}={3}".format(str(offense.id).ljust(columnpadding_id), "".ljust(columnpadding_userid) if offense.assigned_to == None else offense.assigned_to.ljust(columnpadding_userid), type_srcip_name, offense.source))
		if offense.type == type_dstip:
			print("id:{0} [{1}] {2}={3}".format(str(offense.id).ljust(columnpadding_id), "".ljust(columnpadding_userid) if offense.assigned_to == None else offense.assigned_to.ljust(columnpadding_userid), type_dstip_name, offense.source))
		if offense.type == type_user:
			print("id:{0} [{1}] {2}={3}".format(str(offense.id).ljust(columnpadding_id), "".ljust(columnpadding_userid) if offense.assigned_to == None else offense.assigned_to.ljust(columnpadding_userid), type_user_name, offense.source))

def main(userid):
	offenses = load_offenses(query_api(userid))
	print_offenses(offenses)

if __name__ == "__main__":
	opt = optparse.OptionParser()
	opt.add_option('--userid', '-u', default='UNASSIGNED')
	options, args = opt.parse_args()
	main(options.userid)
