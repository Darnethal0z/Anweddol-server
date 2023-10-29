#!/bin/bash

# Simple script that uninstalls the Anweddol server and its environment

if [ `id -u` -ne 0 ]; then 
	echo "Deleting system files ..."
	rm -rf /etc∕anweddol
	rm -rf /var/log/anweddol

	echo "Deleting user 'anweddol' ..."
	userdel anweddol

	echo "Deleting systemctl service ..."
	systemctl disable anweddol-server.service
	rm -rf /usr/lib/systemd/system/anweddol-server.service
	systemctl daemon-reload

else
	echo "WARN : The script is not launched as root, the 'anwdlserver' package will be uninstalled but affiliated files and users will still be present on the system"

fi

echo "Uninstalling 'anwdlserver' python package ... "
pip uninstall anwdlserver -y