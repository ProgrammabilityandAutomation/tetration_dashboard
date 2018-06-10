require 'json'

# We will keep these much minutes
counter = 120
# We are UTC+1h 
timezone_offset = 1

# Create a dummy entry 10 minutes in the past (10>ingestion pipeline) not to deform the graph on startup
init_timestamp = Time.now.to_i - 600 + 3600*timezone_offset

# Config file for python script
config = "pyscripts/sources.conf"

# Initialization
srtt_avg_points = [{x: init_timestamp, y:0}]
srtt_max_points = [{x: init_timestamp, y:0}]
app_latency_avg_points = [{x: init_timestamp, y:0}]
app_latency_max_points = [{x: init_timestamp, y:0}]
net_latency_avg_points = [{x: init_timestamp, y:0}]
net_latency_max_points = [{x: init_timestamp, y:0}]
handshake_avg_points = [{x: init_timestamp, y:0}]
handshake_max_points = [{x: init_timestamp, y:0}]
app_const_obs_points = [{x: init_timestamp, y:0}]
net_const_obs_points = [{x: init_timestamp, y:0}]
rst_count_points = [{x: init_timestamp, y:0}]
syn_count_points = [{x: init_timestamp, y:0}]
obs_count_points = [{x: init_timestamp, y:0}]
packets_points = [{x: init_timestamp, y:0}]
retransmits_points = [{x: init_timestamp, y:0}]

# :first_in sets how long it takes before the job is first run. In this case, it is run immediately
SCHEDULER.every '30s' do
	result = eval "%x(pyscripts/tetration_lastest_timestamp.py #{config})"
	result = JSON[result]
	timestamp_string = result['timestamp']
	cur_timestamp = Time.parse(timestamp_string).to_i + 3600*timezone_offset
	#print(Time.at(cur_timestamp))
	last_timestamp = Integer(srtt_avg_points[-1][:x])

	if last_timestamp >= cur_timestamp
		puts "[tet.rb] Same timestamp, exiting"

	else 
		puts "[tet.rb] New timestamp, updating"

		#puts "[tet.rb] "+String(srtt_avg_points.count)	
		if srtt_avg_points.count >= counter
			srtt_avg_points.shift
			srtt_max_points.shift
			app_latency_avg_points.shift
			app_latency_max_points.shift
			net_latency_avg_points.shift
			net_latency_max_points.shift
			handshake_avg_points.shift
			handshake_max_points.shift
			app_const_obs_points.shift
			net_const_obs_points.shift
			rst_count_points.shift
			syn_count_points.shift
			obs_count_points.shift
			packets_points.shift
			retransmits_points.shift
		end

		result = eval "%x(pyscripts/tetration_kpi.py #{config} #{timestamp_string})"
		result = JSON[result]
		puts "[tet.rb] "+String(result)
		srtt_avg = Float(result['srtt_avg'])
		srtt_max = Float(result['srtt_max'])
		app_avg = Float(result['app_avg']/1000).round(3)
		app_max = Float(result['app_max']/1000).round(3)
		#app_avg = Float(result['app_avg'])
		#app_max = Float(result['app_max'])
		net_avg = Float(result['net_avg'])
		net_max = Float(result['net_max'])
		handshake_avg = Float(result['handshake_avg'])
		handshake_max = Float(result['handshake_max'])
		rst_count = Integer(result['rst_count'])
		syn_count = Integer(result['syn_count'])
		app_const_obs = Integer(result['app_const_obs'])
		net_const_obs = Integer(result['net_const_obs'])
		obs_count = Integer(result['obs_count'])
		packets = Integer(result['packets'])
		retransmits = Integer(result['retransmits'])
		
		srtt_avg_points << { x: cur_timestamp, y: srtt_avg}
		srtt_max_points << { x: cur_timestamp, y: srtt_max}
		app_latency_avg_points << { x: cur_timestamp, y: app_avg}
		app_latency_max_points << { x: cur_timestamp, y: app_max}
		net_latency_avg_points << { x: cur_timestamp, y: net_avg}
		net_latency_max_points << { x: cur_timestamp, y: net_max}
		handshake_avg_points << { x: cur_timestamp, y: handshake_avg}
		handshake_max_points << { x: cur_timestamp, y: handshake_max}
		app_const_obs_points << { x: cur_timestamp, y: app_const_obs}
		net_const_obs_points << { x: cur_timestamp, y: net_const_obs}
		rst_count_points << { x: cur_timestamp, y: rst_count}
		syn_count_points << { x: cur_timestamp, y: syn_count}
		obs_count_points << { x: cur_timestamp, y: obs_count}
		packets_points << { x: cur_timestamp, y: packets}
		retransmits_points << { x: cur_timestamp, y: retransmits}

		send_event('srtt_avg', points: srtt_avg_points)
		send_event('srtt_max', points: srtt_max_points)
		send_event('app_latency_avg', points: app_latency_avg_points)
		send_event('app_latency_max', points: app_latency_max_points)
		send_event('handshake_avg', points: handshake_avg_points)
		send_event('handshake_max', points: handshake_max_points)
		send_event('net_latency_avg', points: net_latency_avg_points)
		send_event('net_latency_max', points: net_latency_max_points)
                send_event('app_const_obs', points: app_const_obs_points)
                send_event('net_const_obs', points: net_const_obs_points)
                send_event('rst_count', points: rst_count_points)
                send_event('syn_count', points: syn_count_points)
                send_event('obs_count', points: obs_count_points)
                send_event('packets', points: packets_points)
                send_event('retransmits', points: retransmits_points)
                send_event('synergy_avg_app_latency', value: app_avg)
                send_event('synergy_avg_net_latency', value: net_avg)
                send_event('synergy_retransmits', value: retransmits)
                send_event('synergy_flows', value: obs_count)
	end
end
