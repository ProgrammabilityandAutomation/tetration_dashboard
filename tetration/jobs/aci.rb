require 'json'

source = "pyscripts/sources.conf"

SCHEDULER.every '1m' do
	result = eval "%x( pyscripts/aci_health.py #{source} )"
	result = JSON.parse(result)

	fabric_health = Hash.new({ value: 0 })
	epgs_health = Hash.new({ value: 0 })
		
	result['fabric_health'].each do |pod|
		pod.each do |key, value|
			fabric_health[key] = { label: key, value: value }
		end
	end
	result['EPGs_health'].each do |epg|
		epg.each do |key, value|
			epgs_health[key] = { label: key, value: value }
		end
	end
	puts "[aci.rb] "+ String(fabric_health.values)
	puts "[aci.rb] "+ String(epgs_health.values)
	send_event('fabric_health', { items: fabric_health.values })
	send_event('epgs_health', { items: epgs_health.values })
end
