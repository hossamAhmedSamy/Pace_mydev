#!/usr/bin/sh
fapipy() {
cd /TopStor
 docker exec flask /TopStor/fapi.py 
}

while true;
do
 fapipy
 sleep 3 
done

