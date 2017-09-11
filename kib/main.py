from kubernetes import client, config
from pprint import pprint

config.load_kube_config()

api = client.CustomObjectsApi()
print("List custom images")

try:
    group = 'k8s.6shore.net'
    version = 'v1'
    namespace = 'default'
    plural = 'images'
    ret = api.list_namespaced_custom_object(group, version, namespace, plural)
    pprint(ret)
except client.rest.ApiException:
    pass
