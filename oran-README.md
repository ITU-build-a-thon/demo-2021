# Steps for installing oran-sc near RT RIC 
This instructions are for installing Dawn realease on Ubuntu 18.04 machine.
## Get helm(v3)
```
sudo -i
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

```
## Install k8s, docker and RIC components
```
git clone http://gerrit.o-ran-sc.org/r/it/dep -b 
cd dep
git submodule update --init --recursive --remote
```

Replace *dep/ric-dep/helm/infrastructure/subcharts/kong/values.yaml* with the provided *values.yaml*

```
cd dep/tools/k8s/bin
./gen-cloud-init.sh
./<generated k8s file>
kubectl get pods -A (check if 9 pods are up)
```

```
cd dep/bin
./deploy-ric-platform -f ../RECIPE_EXAMPLE/PLATFORM/example_recipe_oran_dawn_release.yaml
kubectl get pods -n ricplt (16 pods should come up. all in running state except for influxdb)
```

## Install E2SIM
`sudo apt-get install -y build-essential git cmake libsctp-dev lksctp-tools autoconf automake libtool bison flex libboost-all-dev python3-pip`

```
git clone "https://gerrit.o-ran-sc.org/r/sim/e2-interface"
mkdir e2-interface/e2sim/build
cd e2-interface/e2sim/build
cmake ..
make package
cmake .. -DDEV_PKG=1
make package
cp e2sim*deb ../e2sm_examples/kpm_e2sm
cd ../e2sm_examples/kpm_e2sm
```

Get IP using: `'kubectl get svc -n ricplt | grep e2term-sctp-alpha | awk '{ print $3 }'`

Open *e2-interface/e2sim/e2sm_examples/kpm_e2sm/Dockerfile*

Change IP in front of CMD kpm_sim in last line of file

`docker build .`

This should return successfully built *imageid*

Run:

```
docker tag *imageid* e2simul:1.0.0
docker run -d e2simul:1.0.0
```

## Xapp
### Prerequisites
```
docker run --rm -u 0 -it -d -p 8090:8080 -e DEBUG=1 -e STORAGE=local -e STORAGE_LOCAL_ROOTDIR=/charts -v $(pwd)/charts:/charts chartmuseum/chartmuseum:latest
export CHART_REPO_URL=http://0.0.0.0:8090 
#Add above line to .bashrc 
git clone "https://gerrit.o-ran-sc.org/r/ric-plt/appmgr"
cd appmgr/xapp_orchestrater/dev/xapp_onboarder
python3 -m pip install ./
```

Start following *integration-README.md* from here --------------->

=========================================================================================
### Build Xapp
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

### Onboard and install Xapp
```
dms_cli onboard --config_file_path=lower-loop/ric-app-prbpred/prbpred/xapp-descriptor/config.json --shcema_file_path=lower-loop/embedded-schema.json

dms_cli onboard --config_file_path=lower-loop/ric-app-prbpred/alloc/xapp-descriptor/config.json --shcema_file_path=lower-loop/embedded-schema.json

dms_cli install --xapp_chart_name=prbpredxapp --version=0.0.2 --namespace=ricxapp

dms_cli install --xapp_chart_name=alloc --version=0.0.2 --namespace=ricxapp
```

Check if apps are running:

`kubectl get pods -n ricxapp`

### uninstall Xapp
```
dms_cli uninstall --xapp_chart_name=alloc --namespace=ricxapp

dms_cli uninstall --xapp_chart_name=prbpredxapp --namespace=ricxapp
```

## Initiate intent over A1
Get A1 med IP:port 

`kubectl get svc -n ricplt | grep a1mediator-http | awk '{ print $3 }{ print $5 }'`

Create policy (One time)

`curl -X PUT --header "Content-Type: application/json" -d @a1_policy_create.json 'http://10.110.47.10:10000/a1-p/policytypes/20008'`


Check if policy is created

`curl -X GET --header "Content-Type: application/json" 'http://10.110.47.10:10000/a1-p/policytypes/20008'`


Create policy instance (FGAN intent)

`curl -X PUT --header "Content-Type: application/json" -d @intent.json 'http://10.110.47.10:10000/a1-p/policytypes/20008/policies/tsapolicy145'`


Check if policy instance is created

`curl -X GET --header "Content-Type: application/json" 'http://10.110.47.10:10000/a1-p/policytypes/20008/policies/tsapolicy145'`


Delete policy and policy instance

`curl -X DELETE --header "Content-Type: application/json" 'http://10.110.47.10:10000/a1-p/policytypes/20008/policies/tsapolicy145'`

`curl -X DELETE --header "Content-Type: application/json" 'http://10.110.47.10:10000/a1-p/policytypes/20008'`


## Misc
Get all onboarded charts list: 

`dms_cli get_charts_list`

Check pod for errors:

`kubectl describe pod ricxapp-prbpredxapp-66bfd5bc55-5nx8v -n ricxapp`


Orchestrate a service template:
`curl -X POST localhost:8080/deploy -H "Content-Type: application/json" -d '{"service_template": "cl-orch/basic_three_node/service.yaml"}'`
 
