from pprint import pprint
from .kubeapi import KubeAPI
# from .registry import Registry
from .builders import DockerBuilder


def handle(event):
    if (event['type'] in ['ADDED', 'MODIFIED']):
        DockerBuilder(event['object'])
    else:
        pprint(event)


def main():
    api = KubeAPI()
    api.watch_namespaced_custom_resource('images', handle)

    # print('Images in registry:')
    # registry = Registry()
    # registry_images = registry.get_all_images()

    # # look for missing images
    # for image in api_images:
    #     pprint(image)
    #     spec = image['spec']
    #     tags = spec.get('tags', ['latest'])
    #     for tag in tags:
    #         image_url = image['spec']['name'] + ':' + tag
    #         print('Checking image ' + image_url)
    #         if image_url not in registry_images:
    #             DockerBuilder(image)


if __name__ == '__main__':
    main()
