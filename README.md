# kib
Kubernetes image builder is simple service capable to build custom images and push them to registry. It is using [Custom resources](https://kubernetes.io/docs/concepts/api-extension/custom-resources/) and image controller.

Image controller is listening for changes in Kubernetes API and build missing images.

## Instalation

1. Create custom resources

```
kubectl apply -f resources/
```

2. Run controller (running in container/pod will be available in next version)

```
python3 -m kib
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
