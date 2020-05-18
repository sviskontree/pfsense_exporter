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


