#!/usr/bin/sh
fapipy() {
cd /TopStor
/TopStor/fapi.py 1>/root/fapi.log 2>/root/fapierr.log 
}
until fapipy; do
 echo "'fapi' crashed with exit code $?. Restarting..." >&2
    sleep 1
done

