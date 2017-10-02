from .builders import DockerBuilder
from .kubeapi import KubeAPI
from .registry import Registry

import os
import logging

# define logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Kib:
    def __init__(self):
        self.config_load_config = os.environ.get('KIB_CONFIG', 'incluster')
        self.config_build_missing = os.environ.get('KIB_START_CHECK_MISSING', '1') == '1'
        self.config_watch = os.environ.get('KIB_WATCH', '1') == '1'

        # connect to Kubernetes API
        self.api = KubeAPI(load_config=self.config_load_config)
        logger.debug('Connected to Kubernetes API: {}'.format(self.api))

        # check for missing images
        if self.config_build_missing:
            logger.debug('Building missing images')
            self.build_missing()

        # start watching
        if self.config_watch:
            logger.debug('Started watching for images')
            self.start()

    def build_missing(self):
        """
        Build all missing images in repository
        """

        for image in self.api.get_images():
            if self.check_missing(image):
                self.build_image(image)

    def check_missing(self, image):
        build = False
        dest = image['spec'].get('dest', 'localhost:5000')
        registry = Registry(registry_url='http://{}'.format(dest))
        existing = registry.get_all_images()

        for tag in image['spec'].get('tags', ['latest']):
            if '{}:{}'.format(image['spec']['name'], tag) not in existing:
                build = True
                break

        return build

    def build_image(self, image):
        try:
            DockerBuilder(image)
        except Exception as exc:
            logger.error('Error building image {}: {}'.format(image['metadata']['name'], exc))

    def handle_event(self, event):

        if event['type'] in ['ADDED', 'MODIFIED']:
            self.build_image(event['object'])
        else:
            logger.debug(event)

    def start(self):
        """
        Watch for new resources and build them
        """

        # watch for images
        self.api.watch_namespaced_custom_resource('images', self.handle_event)


def main():
    Kib()
