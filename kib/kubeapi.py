from kubernetes import client
from kubernetes import config
from kubernetes import watch
from urllib3.exceptions import ProtocolError

import logging

# define logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class KubeAPI:
    def __init__(self, **kwargs):

        # load configuration
        if kwargs.get('load_config', 'incluster') == 'incluster':
            config.load_incluster_config()
        elif kwargs.get('load_config') == 'local':
            config.load_kube_config()

        self.api = client.CustomObjectsApi()
        self.group = kwargs.get('group', 'k8s.6shore.net')
        self.version = kwargs.get('version', 'v1')
        self.namespace = kwargs.get('namespace', 'default')

    def _get_namespaced_custom_resources(self, plural):
        return self.api.list_namespaced_custom_object(
            self.group,
            self.version,
            self.namespace,
            plural
        )

    def get_images(self):
        return self._get_namespaced_custom_resources('images')['items']

    def watch_namespaced_custom_resource(self, plural, handle):

        def query(*args, **kwargs):
            return self.api.list_namespaced_custom_object(
                self.group,
                self.version,
                self.namespace,
                plural,
                **kwargs
            )

        w = watch.Watch()
        while True:
            try:
                for event in w.stream(query):
                    handle(event)
            except ProtocolError:
                logger.warning('Watch failed, restarting')
                continue

            break
