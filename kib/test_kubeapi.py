from .kubeapi import KubeAPI
from kubernetes.config.config_exception import ConfigException

import pytest


@pytest.mark.skip('TODO')
def test_init_local():
    api = KubeAPI(load_config='local')
    print(api)


@pytest.mark.skip('TODO')
def test_init_incluster(monkeypatch):
    monkeypatch.setenv('KUBERNETES_SERVICE_HOST', '10.254.0.1')
    monkeypatch.setenv('KUBERNETES_SERVICE_PORT', '443')

    with pytest.raises(ConfigException):
        api = KubeAPI(load_config='incluster')
        print(api)
