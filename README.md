# kib
Kubernetes image builder is simple service capable to build custom images and push them to registry. It is using [Custom resources](https://kubernetes.io/docs/concepts/api-extension/custom-resources/) and image controller.

Image controller is listening for changes in Kubernetes API and build missing images.

## Instalation

1. Create custom resources

```
kubectl apply -f resources/
```

2. Run controller (directy integration into Kubernetes and running as pod will be available in next version)

```
python3 -m kib
```

3. Add Image resources and wait for them to get builded. Image examples can be found in `examples/`


## Demo

[![asciicast](https://asciinema.org/a/137445.png)](https://asciinema.org/a/137445)
