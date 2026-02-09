########################################################################################################################
########################################################################################################################
#####################                           IMPORTING LIBRAIRIES                               #####################
########################################################################################################################
########################################################################################################################


from kubernetes import config, client
from pathlib import Path
import json
import time
from pprint import pprint
from typing import List, Dict, Optional


########################################################################################################################
########################################################################################################################
#####################                           INITIAL CONFIGURATION                              #####################
########################################################################################################################
########################################################################################################################


KUBECONFIG_PATH = Path(__file__).parent / "kubeconfig"
RESOURCES_DETAILS_PATH = Path(__file__).parent / "k8s_resources.json"

config.load_kube_config(str(KUBECONFIG_PATH))

v1 = client.CoreV1Api()
apps = client.AppsV1Api()
rbac = client.RbacAuthorizationV1Api()
network = client.NetworkingV1Api()

with open(RESOURCES_DETAILS_PATH, "r") as f:
    resources = json.load(f)


########################################################################################################################
########################################################################################################################
#####################                                 PARENT CLASS                                 #####################
########################################################################################################################
########################################################################################################################


class Resource():
    def __init__(self, name: str, kind: str, namespace: str = ""):
        self.name = name
        self.namespace = namespace
        self.kind = kind 

    def __str__(self):
        if self.namespace:
            return f"{self.name} of type {self.kind} from {self.namespace} namespace."
        else:
            return f"Cluster resource {self.name} of type {self.kind}."
        
    def _check_exists(self):
        try:
            self.get_resource()
            return True
        except:
            return False
        
    def get_resource(self): 
        if self.namespace:
            func = identify_api(api_descr=self.kind, prefix="read_namespaced_") # identify_api returns getattr(k8s_api_client_instance, function to run)
            return func(name=self.name, namespace=self.namespace) # type: ignore
        else:
            func = identify_api(api_descr=self.kind, prefix="read_")
            return func(name=self.name) # type: ignore
        
    def delete_resource(self):
        if self.namespace:
            func = identify_api(api_descr=self.kind, prefix="delete_namespaced_")
            try:
                func(name=self.name, namespace=self.namespace) # type: ignore
                return True
            except:
                print("Cannot delete resource for xyz.")
                return False
        else:
            func = identify_api(api_descr=self.kind, prefix="delete_namespaced_")
            try:
                func(name=self.name) # type: ignore
                return True
            except:
                print("Cannot delete resource for xyz.")
                return False 


########################################################################################################################
########################################################################################################################
#####################                                  POD CLASS                                   #####################
########################################################################################################################
########################################################################################################################


class Pod(Resource):
    def __init__(self, name: str, namespace: str):
        super().__init__(name=name, namespace=namespace, kind="pod")

       
    def get_status(self):
        if super()._check_exists():
            status = super().get_resource().status.phase 
            print(f"Pod {self.name} status is : {status}.")
            return True
        else:
            print(f"The pod {self.name} doesn't exist in namespace {self.namespace}.")
            return False    
        
    def _check_cont_status(self, conts: list):
        pod = super().get_resource()
        i = 0
        while i < len(pod.spec.containers): # type: ignore
            if pod.status.container_statuses[i].state.waiting: # type: ignore
                if pod.status.container_statuses[i].state.waiting.reason == "ImagePullBackOff" or pod.status.container_statuses[i].state.waiting.reason == "ErrImagePull": # type: ignore
                    print(f"Container image {pod.spec.containers[i].image} cannot be fetched.") # type: ignore
                    return False
            print(f"Found container image {pod.spec.containers[i].image}") # type: ignore
            i += 1
        return True
    
    """ def _get_pod_containers(self):
        pod = v1.read_namespaced_pod(name=self.name, namespace=self.namespace)
        containers = []
        for cont in pod.spec.containers: # type: ignore
            containers.append(cont.name)
        return containers """
        
    def create(self, cont_image: str, labels: Optional[Dict] = None, storage: Optional[List[Dict]] = None):
        if not super()._check_exists():
            try: 
                print(f"Creating pod {self.name} in namespace {self.namespace}...")
                pod_metadata = client.V1ObjectMeta(name=self.name, namespace=self.namespace, labels=labels)
                pod_container = client.V1Container(name=self.name, image=cont_image)
                containers = [pod_container]
                pod_spec = client.V1PodSpec(containers=containers)
                pod_body = client.V1Pod(api_version="v1", kind="Pod", metadata=pod_metadata, spec=pod_spec)
                v1.create_namespaced_pod(self.namespace, body=pod_body)

                time.sleep(5)
                if not self._check_cont_status(containers):
                    print("Failed to create the pod, image cannot be found, deleting pod...")
                    super().delete_resource()
                    return False
            except client.ApiException as err:
                if "namespace" in err.body and "not found" in err.body: # type: ignore
                    print(f"Cannot create pod as namespace {self.namespace} doesn't exist.")
                    return False
            else:
                print("Succesfully created pod...")
                return True
        else:
            print(f"The pod {self.name} already exist in namespace {self.namespace}, skipping...")
            return False


########################################################################################################################
########################################################################################################################
#####################                              GENERAL  FUNCTIONS                              #####################
########################################################################################################################
########################################################################################################################       


def list_all_namespace_pods(namespace):
    return [ pod.metadata.name for pod in v1.list_namespaced_pod(namespace=namespace).items ]

def list_all_resources(resource: str, namespace: str=""):
    if namespace:
        func = identify_api(api_descr=resource, prefix="list_namespaced_")
        return [ rsr.metadata.name for rsr in func(namespace).items ] # type: ignore
    else:
        func = identify_api(api_descr=resource, prefix="list_")
        return [ rsr.metadata.name for rsr in func().items ] # type: ignore

def list_all_namespaces():
    return [ ns.metadata.name for ns in v1.list_namespace().items ]

def identify_api(api_descr: str, prefix: str):
    """
    Gets the API type and generates command based on it 
    v1 = client.CoreV1Api() 
    => in v1, can find all functions for API v1, including pods, svcs, secrets etc...
    => f_name looks like : prefix+k : list_namespaced_ + the key in json file, which is always set to same syntax as function from v1
    => getattr(v1, f_name) : generates a function like : v1.list_namespaced_pod 
    => when calling it : var = identify_api(pod, list_namespaced_)) : identify api references the actual function : v1.list_namespaced_pod as var() 
    => so when calling var(), actually calling v1.list_namespaced_pod, which takes one argument, the namespace
    """
    for k, v in resources.items():
        if api_descr in v["names"]:
            f_name = f"{prefix}{k}"
            if v["api"] == "CoreV1":
                return getattr(v1, f_name)
            elif v["api"] == "AppsV1":
                return getattr(apps, f_name)
            elif v["api"] == "RbacAuthorizationV1":
                return getattr(rbac, f_name)
            elif v["api"] == "NetworkingV1":
                return getattr(network, f_name)


########################################################################################################################
########################################################################################################################
#####################                               FOR TESTING ONLY                               #####################
########################################################################################################################
########################################################################################################################


if __name__ == "__main__":
    a = Resource(name="view", kind="clusterrole")
    b = Resource(name="nginx", kind="deploy", namespace="default")
    c = Pod(name="test", namespace="default")

    common_labels = {
        "project": "python",
        "app-type": "web"
    }
    #print(a._check_exists()) # type: ignore

    c.create(cont_image="nginx", labels=common_labels)
    c.get_status()

    #b.delete_resource()

