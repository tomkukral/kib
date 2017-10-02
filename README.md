# kib

[![Build Status](https://travis-ci.org/tomkukral/kib.svg?branch=master)](https://travis-ci.org/tomkukral/kib)
[![PyPI version](https://badge.fury.io/py/kib.svg)](https://badge.fury.io/py/kib)
[![Coverage Status](https://coveralls.io/repos/github/tomkukral/kib/badge.svg?branch=master)](https://coveralls.io/github/tomkukral/kib?branch=master)

Kubernetes image builder is simple service capable to build custom images and push them to registry. It is using [Custom resources](https://kubernetes.io/docs/concepts/api-extension/custom-resources/) and image controller.

Image controller is listening for changes in Kubernetes API and build missing images.

## Installation

1. Create custom resources

```
kubectl apply -f resources/
```

2. Run controller

* in Kubernetes cluster

```
kubectl apply -f deploy.yml
```

* directly

```
python3 -m kib
```

* install from PyPi

```
pip3 install kib
kib
```

3. Add Image resources and wait for them to get builded. Image examples can be found in `examples/`

## Configuration

Configuration options are defined by environment variables.

Name | Default | Description
--- | --- | ---
`KIB_CONFIG` | `incluster` | Define how to load configuration
`KIB_BUILD_MISSING` | `1` | Build missing images on start
`KIB_WATCH` | `1` | Keep watching for new images

## Demo

[![asciicast](https://asciinema.org/a/137445.png)](https://asciinema.org/a/137445)
