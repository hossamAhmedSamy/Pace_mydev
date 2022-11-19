 while [[ $started -eq 0 ]];
        do
         docker logs etcd | grep 'successfully notified init daemon'
         if [ $? -eq 0 ];
         then
                 started=1
         else
                 sleep 1
         fi
 done
