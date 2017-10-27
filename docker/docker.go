package docker

import (
	"archive/tar"
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"reflect"
	"sort"

	"github.com/docker/docker/api/types"
	"github.com/heroku/docker-registry-client/registry"
	"github.com/mceloud/kib/crd"

	dockerclient "github.com/docker/docker/client"
)

var ctx context.Context = context.Background()

type DockerConfig struct {
	Registry string
	User     string
	Password string
}

func DockerBuild(cli *dockerclient.Client, im *crd.Image) error {

	buf := new(bytes.Buffer)
	tw := tar.NewWriter(buf)
	defer tw.Close()

	dockerFileReader, err := http.Get(im.Spec.Source)
	if err != nil {
		return err
	}

	readDockerFile, err := ioutil.ReadAll(dockerFileReader.Body)
	if err != nil {
		return err
	}

	tarHeader := &tar.Header{
		Size: int64(len(readDockerFile)),
		Name: "dockerfile",
	}

	err = tw.WriteHeader(tarHeader)
	if err != nil {
		return err
	}

	_, err = tw.Write(readDockerFile)
	if err != nil {
		return err
	}

	dockerFileTarReader := bytes.NewReader(buf.Bytes())

	buildOptions := types.ImageBuildOptions{
		Tags:    []string{im.Spec.Name},
		Context: dockerFileTarReader,
		Remove:  true}

	vars, err := cli.ImageBuild(ctx, dockerFileTarReader, buildOptions)
	if err != nil {
		return err
	}
	defer vars.Body.Close()
	fmt.Println(vars)
	_, err = io.Copy(os.Stdout, vars.Body)
	if err != nil {
		return err
	}
	return err
}

func DockerList(cli *dockerclient.Client) []types.ImageSummary {
	ctx := context.Background()

	listOptions := types.ImageListOptions{
		All: true}

	imageList, err := cli.ImageList(ctx, listOptions)
	if err != nil {
		log.Fatal(err)
	}

	return imageList
}

func ImageExists(image *crd.Image, tags [][]string) bool {
	var images []string
	for im := range image.Spec.Tags {
		images = append(images, image.Spec.Name+":"+image.Spec.Tags[im])
	}
	sort.Strings(images)
	fmt.Println(tags, images)
	return false
}

func DockerTag(cli *dockerclient.Client, im *crd.Image) ([]string, error) {
	var imList []string
	var image string
	var err error
	var registry string

	if im.Spec.Destination != "" {
		registry = im.Spec.Destination
	} else {
		registry = "127.0.0.1:5000"
	}

	for i := range im.Spec.Tags {
		image = registry + "/" + im.Spec.Name + ":" + im.Spec.Tags[i]
		err = cli.ImageTag(ctx, im.Spec.Name, image)
		if err != nil {
			return imList, err
		}
		imList = append(imList, image)
	}
	return imList, err
}

func DockerPush(cli *dockerclient.Client, imList []string) error {

	authConfig := types.AuthConfig{
		Username: "dummy",
		Password: "dummy",
	}
	encodedJSON, err := json.Marshal(authConfig)
	if err != nil {
		return err
	}
	authStr := base64.URLEncoding.EncodeToString(encodedJSON)

	pushOptions := types.ImagePushOptions{
		RegistryAuth: authStr}

	for im := range imList {
		fmt.Println(imList[im])
		vars, err := cli.ImagePush(ctx, imList[im], pushOptions)
		if err != nil {
			return err
		}

		_, err = io.Copy(os.Stdout, vars)
		if err != nil {
			return err
		}
	}
	return err
}

func DockerSearch(cli *dockerclient.Client, im *crd.Image) (bool, error) {
	var url string
	var equal bool

	if im.Spec.Destination != "" {
		url = "http://" + im.Spec.Destination + "/"
	} else {
		url = "http://127.0.0.1:5000/"
	}

	username := ""
	password := ""
	hub, err := registry.New(url, username, password)
	if err != nil {
		return equal, err
	}

	repositories, err := hub.Repositories()
	if err != nil {
		return equal, err
	}
	for rep := range repositories {
		if repositories[rep] == im.Spec.Name {
			tags, _ := hub.Tags(repositories[rep])
			sort.Strings(tags)
			sort.Strings(im.Spec.Tags)
			equal = reflect.DeepEqual(tags, im.Spec.Tags)
			return equal, err
		}
	}
	return false, err
}

func ImageCreate(cli *dockerclient.Client, im *crd.Image) error {
	err := DockerBuild(cli, im)
	if err != nil {
		return err
	}

	imList, err := DockerTag(cli, im)
	if err != nil {
		return err
	}

	DockerPush(cli, imList)
	if err != nil {
		return err
	}
	return err
}

func ImageDelete(cli *dockerclient.Client, im *crd.Image) error {
	var err error
	return err
}
