package main

import (
	"context"
	"flag"
	"time"

	"github.com/mceloud/kib/controller"
	"github.com/mceloud/kib/crd"
	"github.com/mceloud/kib/docker"

	apiextcs "k8s.io/apiextensions-apiserver/pkg/client/clientset/clientset"

	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

func GetClientConfig(kubeconfig string) (*rest.Config, error) {
	if kubeconfig != "" {
		return clientcmd.BuildConfigFromFlags("", kubeconfig)
	}
	return rest.InClusterConfig()
}

func main() {
	kubeconf := flag.String("kubeconf", "admin.conf", "Path to a kube config. Only required if out-of-cluster.")
	registry := flag.String("registry", "127.0.0.1:5000", "Address of private registry")
	username := flag.String("username", "", "Username for Docker Registry")
	password := flag.String("password", "", "Password for Docker Registry")
	flag.Parse()

	config, err := GetClientConfig(*kubeconf)
	if err != nil {
		panic(err.Error())
	}

	dockerConfig := docker.DockerConfig{
		Registry: *registry,
		User:     *username,
		Password: *password}

	clientset, err := apiextcs.NewForConfig(config)
	if err != nil {
		panic(err.Error())
	}

	err = crd.CreateCRD(clientset)
	if err != nil {
		panic(err)
	}

	time.Sleep(3 * time.Second)

	crdcs, scheme, err := crd.NewClient(config)
	if err != nil {
		panic(err)
	}

	controller := controller.ImageController{
		ImageClient: crdcs,
		ImageScheme: scheme,
	}

	ctx, cancelFunc := context.WithCancel(context.Background())
	defer cancelFunc()
	go controller.Run(ctx, dockerConfig)
	select {}

}
