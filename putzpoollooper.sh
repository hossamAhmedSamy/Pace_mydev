#!/usr/bin/sh
putzpoolpy() {
cd /pace
/putzpool/putzpool.py
}
until putzpoolpy; do
 echo "'putzpool' crashed with exit code $?. Restarting..." >&2
    sleep 5 
done

