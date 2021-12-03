#!/bin/bash
curl -X DELETE --header "Content-Type: application/json" 'http://10.110.47.10:10000/a1-p/policytypes/20008/policies/tsapolicy145'
dms_cli uninstall --xapp_chart_name=alloc --namespace=ricxapp
dms_cli uninstall --xapp_chart_name=prbpredxapp --namespace=ricxapp
rm -r ../.opera ../.opera-api/
rm /home/ubuntu/xopera-api/src/near-rt-ric/cl-orch/basic_three_node/service.yaml
#curl -X DELETE --header "Content-Type: application/json" 'http://10.110.47.10:10000/a1-p/policytypes/20008'

