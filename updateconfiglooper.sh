#!/usr/bin/sh
updateConfig() {
	/TopStor/collectNodeConfig.py $1 $2 
}

while true;
do
 updateConfig $1 $2
 sleep 2
done

