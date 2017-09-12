from kubernetes import client, config, watch


class KubeAPI:
    def __init__(self, group='k8s.6shore.net', version='v1', namespace='default'):
        config.load_kube_config()

        self.api = client.CustomObjectsApi()
        self.group = group
        self.version = version
        self.namespace = namespace

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
        for event in w.stream(query):
            handle(event)
