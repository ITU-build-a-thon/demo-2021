# Intent based orchestration for near-rt-ric (lower loop)
This doc assumes that o-ran-sc Near RT RIC (Dawn release) is running on Ubuntu 18.04

## Prerequisites
1. Make sure you have java v11.0.11 and python v3.7 or v3.8

    To check/set correct default python3 version:

        sudo update-alternatives --config python3

2. Install xopera-api:


        git clone https://github.com/xlab-si/xopera-api.git

        cd xopera-api

        ./generate.sh

        python3 -m venv env

        source env/bin/activate

        python3 -m pip install wheel

        python3 -m pip install -r requirements.txt


3. Get & install buildathon code 

        git clone https://github.com/ITU-build-a-thon/demo-2021.git

        cp -r near-rt-ric xopera-api/src

        cd xopera-api/src/near-rt-ric

        python3 -m pip install -r requirements.txt

        sudo apt install jq 

4. In */etc/environment* set path to the near-rt-ric directory. This is required to maintain correct paths for yaml service templates.

        ORCH_PATH=/home/ubuntu/xopera-api/src/near-rt-ric


### IP check
Check if A1 mediator IP is set correctly in *a1listner.py* and *undeploy.sh*. Replace this IP:Port in all A1 curl requests in rest of this document.

`kubectl get svc -n ricplt | grep a1mediator-http | awk '{ print $3 }{ print $5 }'`

Check if model server IP in *instance.json* matches IP where modelstore.py is running

### Build Xapp docker images
Run as root user

`sudo -s`

#### prbpred
```
cd xopera-api/src/near-rt-ric/lower-loop/ric-app-prbpred/prbpred
docker build -t prbpred:1.0 -f  Dockerfile .
docker tag prbpred:1.0 nexus3.o-ran-sc.org:10002/o-ran-sc/ric-app-prbpredxapp:0.0.2
```

#### alloc
```
cd xopera-api/src/near-rt-ric/lower-loop/ric-app-prbpred/alloc
docker build -t alloc:1.0 -f  Dockerfile .
docker tag alloc:1.0 nexus3.o-ran-sc.org:10002/o-ran-sc/ric-app-alloc:0.0.2
```


## Run

Run all commands as root 

`sudo -s`

1. In term 1 window start xopera 
        
        cd xopera
        
        source env/bin/activate 
        
        cd src

        python3 -m opera.api.cli

2. In term 2 start a1listner

         cd xopera-api/src/near-rt-ric

         python3 a1toyaml.py

3. In term 3 start model server
 
         cd xopera-api/src/near-rt-ric/lower-loop/ric-app-prbpred/modelstore

         python3 modelstore.py


4. In term 4 create a policy and send policy instance to a1mediator.  Ideally this should come from higher loop in ONAP. 

        cd xopera-api/src/near-rt-ric

        curl -X PUT --header "Content-Type: application/json" -d @policy.json 'http://10.110.47.10:10000/a1-p/policytypes/20008'

        # Policy setting only needs to be done one time

        curl -X PUT --header "Content-Type: application/json" -d @instance.json 'http://10.110.47.10:10000/a1-p/policytypes/20008/policies/tsapolicy145'

5. Check if xapps are running properly :

        kubectl get pods -n ricxapp

        kubectl logs <podnames> -n ricxapp

To debug orchestration

        curl localhost:8080/status

6. Stop xopera server by ctrl+c and undeploy using -

        bash undeploy.sh


## Pitfalls

dms_cli only runs if python3.6/3.7 is default python3(with warnings). Not if python3.8 is default python3. Python versions required by xopera and dms_cli may conflict with each other.

xopera generates .opera and .opera-cli directories which might contain cache. 

