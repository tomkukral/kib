from docker_registry_client import DockerRegistryClient


class Registry:
    def __init__(self, registry_url='http://localhost:5000', verify_ssl=False):
        self.registry_client = DockerRegistryClient(registry_url, verify_ssl=verify_ssl)

    def get_repositories(self):
        return self.registry_client.repositories()

    def get_all_images(self):
        images = []

        for repo_name, repo in self.get_repositories().items():
            for tag in repo.tags():
                images.append(repo_name + ':' + tag)

        return images
