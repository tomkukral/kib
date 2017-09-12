from setuptools import setup, find_packages

version = '0.1'

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='kib',
    version=version,
    description='Kubernetes image builder',
    long_description=long_description,
    author='Tomáš Kukrál',
    author_email='tomas.kukral@6shore.net',
    license='MIT',
    url='https://github.com/tomkukral/kib/',
    download_url='https://github.com/tomkukral/kib/archive/v{}.tar.gz'.format(version),
    packages=find_packages(),
    zip_safe=False,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'kib = kib:main',
        ],
    },
)
