import pytest
import os
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kube import Pod, Deploy

@pytest.fixture()
def default_pod():
    return Pod(name="test", namespace="default")

@pytest.fixture()
def default_deploy():
    return Deploy(name="testdeploy", namespace="default")

### Pod testing

def test_pod_create_works(default_pod):
    assert isinstance(default_pod.create(cont_image="nginx", labels={'app': 'test'}), Pod)

def test_pod_create_existing(default_pod):
    assert isinstance(default_pod.create(cont_image="nginx", labels={'app': 'test'}), Pod)

def test_get_pod_status(default_pod):
    assert isinstance(default_pod.get_status(), dict)

def test_pod_delete_works(default_pod):
    assert default_pod.delete_resource() is None

def test_pod_delete_already_gone(default_pod):
    assert default_pod.delete_resource() is None

def test_pod_create_ns_error():
    pod = Pod(name="test", namespace="doesnotexist")
    with pytest.raises(RuntimeError):
        pod.create(cont_image="nginx") 

def test_pod_create_img_error():
    pod = Pod(name="test2", namespace="default")
    with pytest.raises(RuntimeError):
        pod.create(cont_image="doesnotexist")

### Deploy testing

def test_deploy_create_works(default_deploy):
    assert isinstance(default_deploy.create(image="nginx", deploy_labels={'app': 'deploytest'}), Deploy)

def test_deploy_create_existing(default_deploy):
    assert isinstance(default_deploy.create(image="nginx", deploy_labels={'app': 'deploytest'}), Deploy)

def test_delete_deploy_works(default_deploy):
    assert default_deploy.delete_resource() is None

def test_delete_deploy_already_gone(default_deploy):
    assert default_deploy.delete_resource() is None

def test_create_deploy_ns_error():
    d = Deploy(name="testdeployns", namespace="doesnotexist")
    with pytest.raises(RuntimeError):
        d.create(image="nginx")