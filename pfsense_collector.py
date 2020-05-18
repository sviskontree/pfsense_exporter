import subprocess
import re

def status_check(inpt):
	#0 = down, 1 = established, 2 = installed
	ipsec_established = re.compile(r"\[\d+\]:\s+ESTABLISHED")
	ipsec_installed = re.compile(r"\{\d+\}:\s+INSTALLED")
	
	if ipsec_established.search(inpt):
		if ipsec_installed.search(inpt):
			return 2
		return 1
	
	return 0

def get_algos(inpt):
	ipsec_algo = re.compile(r"\{\d+\}:\s+([^,]+), \d+ bytes_i")
	result = {"hash":"unknown","encryption":"unknown"}
	search_result = ipsec_algo.search(inpt)

	if search_result:
		try:
			split_string = search_result.group(1).split("/")
			result["encryption"] = split_string[0]
			result["hash"] = split_string[1]
		except IndexError as e:
			result["hash"] = "unknown"
			result["encryption"] = "unknown"
	return result
		
def get_bytes_pkts(inpt,direction):
	#returns bytes_ and pkts_, either i for in or o for out
	ipsec_bytes = re.compile(r"(\d+) bytes_{}( \((\d+) pkts, \d+s ago)?".format(direction))
	result = []
	search_result = ipsec_bytes.search(inpt)
	try:
		result.append(int(search_result.group(1)))
	except (IndexError, AttributeError, TypeError) as e:
		result.append(0)

	try:
		result.append(int(search_result.group(3)))
	except (IndexError, AttributeError, TypeError) as e:
		result.append(0)

	return result

def get_ipsec():
        #The ipsec.conf path should be a variable...
	metrics = ("ipsec_status","ipsec_bytes_in","ipsec_packets_in","ipsec_bytes_out","ipsec_packets_out")
	found_connections = []

	#Find all defined connections
	con_match = re.compile(r"conn \S+$")
	with open("/usr/local/etc/ipsec.conf", "r") as ipsec_conf:
		for line in ipsec_conf:
			if con_match.match(line):
				if 'bypasslan' in line:
					continue
				found_connections.append(line.strip().split()[-1])

	all_values = []
	all_values.append("# HELP ipsec_status Status of the ipsec tunnel 0 down, 1 established and 2 installed\n# TYPE ipsec_status counter\n")
	all_values.append("# HELP ipsec_bytes_in Bytes in for the tunnel\n# TYPE ipsec_bytes_in counter\n")
	all_values.append("# HELP ipsec_packets_in Packets in for the tunel\n# TYPE ipsec_packets_in counter\n")
	all_values.append("# HELP ipsec_bytes_out Bytes out for the tunnel\n# TYPE ipsec_bytes_out counter\n")
	all_values.append("# HELP ipsec_packets_out Packets out for the tunnel\n# TYPE ipsec_packets_out counter\n")

	#Loop over the found connections
	for conn in found_connections:	
		temp_output = subprocess.run("ipsec statusall {}".format(conn), shell=True, check=True, capture_output=True)
		output = str(temp_output.stdout)
		algos = get_algos(output)
		value = int(status_check(output))
		all_values[0] += '{0}{{connection_name="{1}",connection_hash="{2}",connection_encryption="{3}"}} {4}\n'.format(metrics[0],conn,algos['hash'],algos['encryption'],value)

		temp = get_bytes_pkts(output,"i")
		all_values[1] += '{0}{{connection_name="{1}"}} {2}\n'.format(metrics[1],conn,temp[0]) 
		all_values[2] += '{0}{{connection_name="{1}"}} {2}\n'.format(metrics[2],conn,temp[1]) 

		temp = get_bytes_pkts(output,"o")
		all_values[3] += '{0}{{connection_name="{1}"}} {2}\n'.format(metrics[3],conn,temp[0]) 
		all_values[4] += '{0}{{connection_name="{1}"}} {2}\n'.format(metrics[4],conn,temp[1]) 
	return all_values

def get_pf():
	#Define all the metric names in a tuple
	metrics = ("pf_pass_in_packets_total","pf_pass_in_bytes_total","pf_block_in_packets_total","pf_block_in_bytes_total","pf_pass_out_packets_total","pf_pass_out_bytes_total","pf_block_out_packes_total","pf_block_out_bytes_total")
	all_values = []
	#Pass in
	all_values.append("# HELP pf_pass_in_packets_total Total packets passed in by pf\n# TYPE pf_pass_in_packets_total counter\n")
	all_values.append("# HELP pf_pass_in_bytes_total Total bytes passed in by pf\n# TYPE pf_pass_in_bytes_total counter\n")
	#Block in
	all_values.append("# HELP pf_block_in_packets_total Total packets blocked in by pf\n# TYPE pf_block_in_packets_total counter\n")
	all_values.append("# HELP pf_block_in_bytes_total Total bytes blocked in by pf\n# TYPE pf_block_in_bytes_total counter\n")
	#Pass out
	all_values.append("# HELP pf_pass_out_packets_total Total packets pass out by pf\n# TYPE pf_pass_out_packets_total counter\n")
	all_values.append("# HELP pf_pass_out_bytes_total Total bytes pass out by pf\n# TYPE pf_pass_out_bytes_total counter\n")
	#Block out
	all_values.append("# HELP pf_block_out_packets_total Total packets blocked out by pf\n# TYPE pf_block_out_packets_total counter\n")
	all_values.append("# HELP pf_block_out_bytes_total Total bytes blocked out by pf\n# TYPE pf_block_out_bytes_total counter\n")

	get_interfaces = subprocess.run("pfctl -s Interfaces | grep -G '[0-9]$' | grep -v \"lo\|pflog\|pfsync\"", shell=True, check=True, capture_output=True)
	interfaces = [str(gi) for gi in get_interfaces.stdout.decode("utf-8").strip().split('\n')]
	ipv4_regex = re.compile(r"\sIn4\/Pass:\s+\[ Packets: (\d+)\s+Bytes: (\d+)\s+]\s+In4\/Block:\s+\[ Packets: (\d+)\s+Bytes: (\d+)\s+]\s+Out4\/Pass:\s+\[ Packets: (\d+)\s+Bytes: (\d+)\s+]\s+Out4\/Block:\s+\[ Packets: (\d+)\s+Bytes: (\d+)\s+]")
	if not interfaces:
		return
	#loop over them like a god
	for interface in interfaces:
		interface_stats = subprocess.run("pfctl -vv -s Interfaces -i {}".format(interface), shell=True, check=True, capture_output=True)
		search_result = ipv4_regex.findall(interface_stats.stdout.decode("utf-8"))
		#always going packets then bytes. groups should be in pass 1+2, in block 3+4, out pass 5+6, out block 7+8 
		for index, value in enumerate(search_result[0]):
			all_values[index] += '{0}{{interface="{1}"}} {2}\n'.format(metrics[index],interface,value)
	return all_values

def collect():
	html = ""
	for i in get_ipsec():
		html += i 
	for i in get_pf():
		html += i
	return html
