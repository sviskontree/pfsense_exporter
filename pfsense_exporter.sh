#!/bin/sh

# PROVIDE: pfsense_exporter
# REQUIRE: LOGIN
# KEYWORD: shutdown
#
# Add the following lines to /etc/rc.conf.local or /etc/rc.conf
# to enable this server: 
# pfsense_exporter_enable (bool): YES or NO
# pfsense_exporter_ip (string): An ip, default is 0.0.0.0
# pfsense_exporter_port (string): A port, default is 9988 

. /etc/rc.subr

name=pfsense_exporter
rcvar=pfsense_exporter_enable

: ${pfsense_exporter_enable:="NO"}
: ${pfsense_exporter_ip:="0.0.0.0"}
: ${pfsense_exporter_port:="9988"}

command="/usr/local/bin/pfsense_exporter.py"
command_args="-i ${pfsense_exporter_ip} -p ${pfsense_exporter_port}"
command_interpreter="/usr/local/bin/python3.7"

start_cmd="/usr/sbin/daemon $command"

load_rc_config $name
run_rc_command "$1"
