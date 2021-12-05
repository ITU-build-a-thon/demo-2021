#!/usr/bin/python3
#############################################################################################################################
#  Author : Abhishek Dandekar
#  Description : This file polls a1mediator for policy and writes the policy to YAML file which is used to orchestrate xapp.
#############################################################################################################################

# Todo: Add logging, exception handling, programmatic instantiation of orchestrator

import os
import polling2
import requests
from ruamel.yaml import YAML 


def test(response):
    return response.status_code != 404

def orchestrate():
    """
    Sends the updated yaml file to xopera to orchestrate
    """
    headers={'Content-Type':'application/json'}
    url= 'http://localhost:8080/deploy'
    data='{"service_template": "near-rt-ric/cl-orch/basic_three_node/service.yaml"}'
    requests.post(url, data=data, headers=headers)

def writetoyaml(a1policy):
    """
    Writes pipeline parameters from A1 policy to yaml file
    """
    yaml = YAML()
    file_name = os.getenv('ORCH_PATH')+"/cl-orch/basic_three_node/servicetemplate.yaml"
    nodes = yaml.load(open(file_name))

    nodes['node_types']['sourceNode']['attributes']['source_uri_attribute']['default'] = a1policy.json()["source"]
    nodes['node_types']['modelNode']['attributes']['model_name_attribute']['default'] = a1policy.json()["modelname"]   
    nodes['node_types']['modelNode']['attributes']['model_server_attribute']['default'] = a1policy.json()["modelserver"]   
    nodes['node_types']['modelNode']['attributes']['model_version_attribute']['default'] = a1policy.json()["modelversion"]   
    nodes['node_types']['sinkNode']['attributes']['sink_uri_attribute']['default'] = a1policy.json()["sink"]

    with open(os.getenv('ORCH_PATH')+'/cl-orch/basic_three_node/service.yaml', 'w') as fp:
        yaml.dump(nodes, fp)


def main():
    print("Polling A1 mediator...")
    headers={'Content-Type':'application/json'}
    url= 'http://10.110.47.10:10000/a1-p/policytypes/20008/policies/tsapolicy145'
    # Keep polling A1 mediator until a valid policy instance is detected (when NOT 404)
    result=polling2.poll(lambda: requests.get(url, headers=headers) , 
                            step=3, 
                            poll_forever=True, 
                            check_success=test)
    
    writetoyaml(result)
    orchestrate()
    print ("Exiting successfully...")


if __name__=='__main__':
    main()