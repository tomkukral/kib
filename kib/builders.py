from requests import get
from docker import APIClient
import tempfile


class DockerBuilder:
    def __init__(self, image):
        print('Starting builder for image ' + image['metadata']['name'])

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
        print(self.dockerfile_url)

        # download dockerfile
        response = get(self.dockerfile_url)
        with open(self.dockerfile_dest, 'wb') as f:
            f.write(response.content)

    def build(self):
        # build first image
        b = self.docker_client.build(
            path=self.tempdir.name,
            tag=self.images[0],
            encoding='utf-8'
        )

        for line in b:
            print(line)

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
                    print('Added tag {}'.format(tag))
                else:
                    print('FAILED adding tag {}'.format(tag))

    def push(self):

        # push images with tags to registry
        for image in self.images:
            b = self.docker_client.push(
                image,
                stream=True,
                insecure_registry=True
            )
            for line in b:
                print(line)

    def clean(self):
        self.tempdir.cleanup()
