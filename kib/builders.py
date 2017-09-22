from docker import APIClient
from requests import get

import json
import logging
import tempfile

# define logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DockerBuilder:
    def __init__(self, image):
        logger.debug('Starting builder for image ' + image['metadata']['name'])

        self.tempdir = tempfile.TemporaryDirectory()
        self.docker_client = APIClient(version='auto')

        # prepare image variables
        self._image = image
        self.dockerfile_url = image['spec']['source']
        self.dockerfile_dest = self.tempdir.name + '/Dockerfile'
        self.dest = image['spec'].get('dest', 'localhost:5000')
        self.image_name = image['spec']['name']
        self.tags = image['spec'].get('tags', ['latest'])

        self.images = ['{}/{}:{}'.format(self.dest, self.image_name, i) for i in self.tags]

        # workflow
        self.prepare()
        self.build()
        self.push()
        self.clean()

    def prepare(self):

        # download dockerfile
        response = get(self.dockerfile_url)
        with open(self.dockerfile_dest, 'wb') as f:
            f.write(response.content)

    def build(self):
        # build first image
        logger.debug('Building image {}'.format(self.images[0]))
        b = self.docker_client.build(
            path=self.tempdir.name,
            tag=self.images[0],
            encoding='utf-8'
        )

        for line in b:
            self._process_stream(line)

        # tag more images
        if len(self.images) > 1:
            for tag in self.tags[1:]:
                action = self.docker_client.tag(
                    self.images[0],
                    '{}/{}'.format(self.dest, self.image_name),
                    tag,
                    force=True,
                )

                if action:
                    logger.debug('Added tag {}'.format(tag))
                else:
                    logger.eror('FAILED adding tag {}'.format(tag))

    def push(self):

        # push images with tags to registry
        for image in self.images:
            b = self.docker_client.push(
                image,
                stream=True,
                insecure_registry=True
            )
            for line in b:
                self._process_stream(line)

    def clean(self):
        self.tempdir.cleanup()

    def _process_stream(self, line):
        l = line.decode('utf-8').strip()

        # try to decode json
        try:
            ljson = json.loads(l)

            if ljson.get('error'):
                msg = str(ljson.get('error', ljson))
                logger.error('Build failed: ' + msg)
                raise Exception('Image build failed: ' + msg)
            else:
                if ljson.get('stream'):
                    msg = 'Build output: {}'.format(ljson['stream'].strip())
                elif ljson.get('status'):
                    msg = 'Push output: {} {}'.format(
                        ljson['status'],
                        ljson.get('progress')
                    )
                elif ljson.get('aux'):
                    msg = 'Push finished: {}'.format(ljson.get('aux'))
                else:
                    msg = str(ljson)

                logger.debug(msg)

        except json.JSONDecodeError:
            print(l)
