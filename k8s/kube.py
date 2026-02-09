from kubernetes import config, client
from pathlib import Path
import json
import time

KUBECONFIG_PATH = Path(__file__).parent / "kubeconfig"
RESOURCES_DETAILS_PATH = Path(__file__).parent / "k8s_resources.json"

config.load_kube_config(str(KUBECONFIG_PATH))

v1 = client.CoreV1Api()
apps = client.AppsV1Api()
rbac = client.RbacAuthorizationV1Api()
network = client.NetworkingV1Api()

with open(RESOURCES_DETAILS_PATH, "r") as f:
    resources = json.load(f)

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
        
    def get_resource(self): 
        if self.namespace:
            func = identify_api(api_descr=self.kind, prefix="read_namespaced_") # identify_api returns getattr(k8s_api_client_instance, function to run)
            return func(name=self.name, namespace=self.namespace) # type: ignore
        else:
            func = identify_api(api_descr=self.kind, prefix="read_")
            return func(name=self.name) # type: ignore
    
    def _check_exists(self):
        try:
            self.get_resource()
            return True
        except:
            return False


class Pod():
    def __init__(self, name: str, namespace: str):
        self.name = name
        self.namespace = namespace

    def __str__(self):
        return f"Instance of pod {self.name} in namespace {self.namespace}"
    
    def _check_exists(self):
        try:
            pod = v1.read_namespaced_pod(name=self.name, namespace=self.namespace)
            return True
        except:
            return False        
    
    def get_status(self):
        if self._check_exists():
            for pod in v1.list_namespaced_pod(self.namespace).items:
                if pod.metadata.name == self.name:
                    print(f"{pod.metadata.name} - State : {pod.status.phase}") 
                    return True
        else:
            print(f"The pod {self.name} doesn't exist in namespace {self.namespace}.")
            return False    
        
    def _check_cont_status(self, conts: list):
        pod = v1.read_namespaced_pod(name=self.name, namespace=self.namespace)
        i = 0
        while i < len(pod.spec.containers): # type: ignore
            if pod.status.container_statuses[i].state.waiting: # type: ignore
                if pod.status.container_statuses[i].state.waiting.reason == "ImagePullBackOff" or pod.status.container_statuses[i].state.waiting.reason == "ErrImagePull": # type: ignore
                    print(f"Container image {pod.spec.containers[i].image} cannot be fetched.") # type: ignore
                    return False
            print(f"Found container image {pod.spec.containers[i].image}") # type: ignore
            i += 1
        return True
    
    def _get_pod_containers(self):
        pod = v1.read_namespaced_pod(name=self.name, namespace=self.namespace)
        containers = []
        for cont in pod.spec.containers: # type: ignore
            containers.append(cont.name)
        return containers
        
    def create(self, cont_image: str):
        if not self._check_exists():
            try:
                print(f"Creating pod {self.name} in namespace {self.namespace}...")
                pod_metadata = client.V1ObjectMeta(name=self.name, namespace=self.namespace)
                pod_container = client.V1Container(name=self.name, image=cont_image)
                containers = [pod_container]
                pod_spec = client.V1PodSpec(containers=containers)
                pod_body = client.V1Pod(api_version="v1", kind="Pod", metadata=pod_metadata, spec=pod_spec)
                v1.create_namespaced_pod(self.namespace, body=pod_body)

                time.sleep(5)
                if not self._check_cont_status(containers):
                    print("Failed to create the pod, image cannot be found, deleting pod...")
                    self.delete()
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
        
    def delete(self):
        if self._check_exists():
            print(f"Deleting pod {self.name} in namespace {self.namespace}...")
            v1.delete_namespaced_pod(name=self.name, namespace=self.namespace)
            return True
        else:
            print(f"Cannot delete pod {self.name} in namespace {self.namespace} as it doesn't exist.")
            return False

def list_all_namespace_pods(namespace):
    return [ pod.metadata.name for pod in v1.list_namespaced_pod(namespace=namespace).items ]

def list_all_resources(resource: str, namespace: str=""):
    if namespace:
        func = identify_api(api_descr=resource, prefix="list_namespaced_")
        print(func(namespace[*].names))
        return [ rsr.metadata.name for rsr in func(resource, namespace).items ] # type: ignore
    else:
        pass

def list_all_namespaces():
    return [ ns.metadata.name for ns in v1.list_namespace().items ]

def identify_api(api_descr: str, prefix: str):
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

if __name__ == "__main__":
    a = Resource(name="viededw", kind="clusterrole")
    b = Resource(name="argocd-server", kind="deploy", namespace="argocd")
    c = Resource(name="argdedocd-server", kind="deploy", namespace="argocd")
    #print(a._check_exists()) # type: ignore

    print(list_all_resources(resource="pod", namespace="argocd"))
