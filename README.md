# pfsense_exporter
Prometheus exporter for pfSense, exports stats for pf and ipsec

## Install
The exporter is built to require no extra dependencies except python3. It's not packaged as a regular pfSense package and must be installed in the shell.

Get the files in the repository to the server in what ever way that you want.

```
$ mv pfsense_exporter.sh /usr/local/etc/rc.d/ 
$ chmod 555 /usr/local/etc/rc.d/pfsense_exporter.sh
$ mv pfsense_exporter.\* /usr/local/bin/
$ chmod 555 /usr/local/bin/pfsense_exporter.py
```

Changes to the service can be done in /etc/rc.conf.local

Name     | Description | Options | Default
---------|------------|-----------|------
pfsense_exporter_enable | Set service to start at boot | YES/NO | NO
pfsense_exporter_ip | IP to listen to | string | 0.0.0.0
pfsense_exporter_port | Port to listen to | string | 9988

## Collectors
The exporter collects a number of statistics from the server:
```
# HELP ipsec_status Status of the ipsec tunnel 0 down, 1 established and 2 installed
# TYPE ipsec_status counter
# HELP ipsec_bytes_in Bytes in for the tunnel
# TYPE ipsec_bytes_in counter
# HELP ipsec_packets_in Packets in for the tunel
# TYPE ipsec_packets_in counter
# HELP ipsec_bytes_out Bytes out for the tunnel
# TYPE ipsec_bytes_out counter
# HELP ipsec_packets_out Packets out for the tunnel
# TYPE ipsec_packets_out counter
# HELP pf_pass_in_packets_total Total packets passed in by pf
# TYPE pf_pass_in_packets_total counter
# HELP pf_pass_in_bytes_total Total bytes passed in by pf
# TYPE pf_pass_in_bytes_total counter
# HELP pf_block_in_packets_total Total packets blocked in by pf
# TYPE pf_block_in_packets_total counter
# HELP pf_block_in_bytes_total Total bytes blocked in by pf
# TYPE pf_block_in_bytes_total counter
# HELP pf_pass_out_packets_total Total packets pass out by pf
# TYPE pf_pass_out_packets_total counter
# HELP pf_pass_out_bytes_total Total bytes pass out by pf
# TYPE pf_pass_out_bytes_total counter
# HELP pf_block_out_packets_total Total packets blocked out by pf
# TYPE pf_block_out_packets_total counter
# HELP pf_block_out_bytes_total Total bytes blocked out by pf
# TYPE pf_block_out_bytes_total counter
```
