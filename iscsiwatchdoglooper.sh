#!/usr/bin/sh
iscsiwatchdogsh() {
cd /pace
/pace/iscsiwatchdoglooper.sh 
}
until iscsiwatchdogsh; do
 echo "'iscsiwatchdogsh' crashed with exit code $?. Restarting..." >&2
    sleep 10 
done

