#!/bin/bash

# Simple script that uninstalls the Anweddol server

if [ `id -u` -eq 0 ]; then 

	echo "Deleting system files ..."
	rm -rf /etc∕anweddol
	rm -rf /var/log/anweddol

	echo "Deleting user 'anweddol' ..."
	userdel -r anweddol

	echo "Deleting anweddol-server systemctl service ..."
	systemctl disable anweddol-server.service
	rm -rf /usr/lib/systemd/system/anweddol-server.service

else

	echo "WARN : The script is not launched as root, the 'anwdlserver' package will be uninstalled but system files and users will still be present on the system"

fi

echo "Uninstalling 'anwdlserver' package ... "
pip uninstall anwdlserver -y