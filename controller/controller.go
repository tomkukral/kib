package controller

import (
	"context"
	"fmt"
	"log"
	"sort"

	apiv1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/fields"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/cache"

	dockerclient "github.com/docker/docker/client"
	"github.com/mceloud/kib/crd"
	"github.com/mceloud/kib/docker"
)

const ImageResourcePlural = "images"

type ImageController struct {
	ImageClient *rest.RESTClient
	ImageScheme *runtime.Scheme
}

func (c *ImageController) Run(ctx context.Context, dockerConfig docker.DockerConfig) error {
	log.Println("Watch Image objects")
	_, err := c.watchImages(ctx, dockerConfig)

	if err != nil {
		fmt.Printf("Failed to register watch for Image resource: %v", err)
		return err
	}

	<-ctx.Done()
	return ctx.Err()
}

func (c *ImageController) watchImages(ctx context.Context, dockerConfig docker.DockerConfig) (cache.Controller, error) {
	source := cache.NewListWatchFromClient(
		c.ImageClient,
		ImageResourcePlural,
		apiv1.NamespaceAll,
		fields.Everything())

	_, controller := cache.NewInformer(
		source,
		&crd.Image{},
		0,
		cache.ResourceEventHandlerFuncs{
			AddFunc:    c.onAdd,
			UpdateFunc: c.onUpdate,
			DeleteFunc: c.onDelete,
		})

	go controller.Run(ctx.Done())
	return controller, nil
}

func (c *ImageController) onAdd(obj interface{}) {
	image := obj.(*crd.Image)
	log.Printf("Adding %s", image.ObjectMeta.SelfLink)

	cli, err := dockerclient.NewEnvClient()
	if err != nil {
		log.Println(err)
	}
	defer cli.Close()

	imageList := docker.DockerList(cli)

	var tags [][]string
	for tag := range imageList {
		sort.Strings(imageList[tag].RepoTags)
		tags = append(tags, imageList[tag].RepoTags)
	}
	switch image.Spec.ImageCreatePolicy {
	case "Always":
		err = docker.ImageCreate(cli, image)
		if err != nil {
			log.Println(err)
		}
	default:
		equal, err := docker.DockerSearch(cli, image)
		if err != nil {
			log.Println(err)
		}
		if equal == false {
			err = docker.ImageCreate(cli, image)
			if err != nil {
				log.Println(err)
			}
			log.Printf("Image %s created", image.ObjectMeta.SelfLink)
		} else {
			log.Printf("Image %s already created", image.ObjectMeta.SelfLink)
		}
	}

}

func (c *ImageController) onUpdate(oldObj, newObj interface{}) {
	//oldImage := oldObj.(*crd.Image)
	newImage := newObj.(*crd.Image)
	log.Printf("Image %s to be updated", newImage.ObjectMeta.SelfLink)

	cli, err := dockerclient.NewEnvClient()
	if err != nil {
		log.Println(err)
	}
	defer cli.Close()

	err = docker.ImageCreate(cli, newImage)
	if err != nil {
		log.Println(err)
	}
	log.Printf("Image %s updated", newImage.ObjectMeta.SelfLink)
}

func (c *ImageController) onDelete(obj interface{}) {
	image := obj.(*crd.Image)
	switch image.Spec.PersistentImage {
	case true:
		log.Printf("Image %s deleted from Kuberentes API. Remains in registry.", image.ObjectMeta.SelfLink)
	default:
		cli, err := dockerclient.NewEnvClient()
		if err != nil {
			log.Println(err)
		}
		defer cli.Close()
		docker.ImageDelete(cli, image)
		if err != nil {
			log.Println(err)
		}
		log.Printf("Image %s deleted", image.ObjectMeta.SelfLink)
	}

}
