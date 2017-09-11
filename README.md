# kib
Kubernetes image builder is simple service capable to build custom images and push them to registry. It is using [Custom resources](https://kubernetes.io/docs/concepts/api-extension/custom-resources/) and custom controller.

## Instalation

1. Create custom resources

```
kubectl apply -f resources/
```

2. Run controller

```
python kib/main.py
```
