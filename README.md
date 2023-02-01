# Linuxserver to Kubernetes

## What and why
[LinuxServer.io](https://www.linuxserver.io/) offers standard and simple [Docker](https://www.docker.com/) images for many apps. As I use [Kubernetes](https://kubernetes.io/) (k8s) at home, and because I am super lazy, I created this script to create config files to run with `kubectl apply -f <file>` from LinuxServer docker images.

[x] YES, I know that [Helm](https://helm.sh/) exists, but I prefer managing deployments myself instead of having a bunch of files to read and verify

[x] YES, I know that [Kompose](https://kompose.io/) exists, but I am not a huge fan of the result (even if it seems super powerful)

You can check the input in [app_list.yaml](https://github.com/pedrosanchezito/linuxserver-to-kubernetes/blob/master/app_list.yaml) and the output in [apps/TEMPLATE-myAppName.yaml](https://github.com/pedrosanchezito/linuxserver-to-kubernetes/blob/master/apps/TEMPLATE-myAppName.yaml)

## Default config (well, my homelab)
- a working [k3s](https://k3s.io/) (or k8s cluster including a CNI and LB)
- [Longhorn](https://longhorn.io/) for persistent storage
- mounted NFS drives on each nodes

## How to use
```bash
git clone git@github.com:pedrosanchezito/linuxserver-to-kubernetes.git
cd linuxserver-to-kubernetes
virtualenv venv # keep your main env clean!
(windows) source venv/Script/activate
(linux) source bin/activate
pip install pyyaml
```

Open `app_list.yaml` and add as many apps you want, separated by `---` for yaml to understand they are separated files (see the template in the file)

Example:
```yaml
appName: # the name of your app, will be used to name resources (namespace, deployment, pvc, service)
image: # the linuxserver image you want to use (lscr.io/linuxserver/repo:tag)
envVars: # list of environment variables, see the app description in linuxserver
  - name: varName
    value: value
  - name: var2Name
    value: value
ports: # list of ports to expose, see the app description in linuxserver
  - name: portName
    protocol: TCP
    port: portNumber
volumes: # list of volumes needed by the app, see the app description in linuxserver.
# 2 types available: 
  # pvc for persistent storage on nodes through longhorn (usually for configuration)
  # nfs to access content on a NAS or any network storage
  - volumeName: volumeName
    volumeMountPath: /path-in-pod
    volumeType: pvc # pvc for longhorn persistent storage
    volumeStorageInGi: volumeSize # only for pvc
  - volumeName: volumeName
    volumeMountPath: /path-in-pod
    volumeHostPath: /path-of-mounted-volume-on-host # only for nfs
    volumeType: nfs # nfs to connect to a nfs shared storage
```

When your `app_list.yaml` is ready, run the script:
```bash
python create_config_files.py
```

You will find one file per app in the `apps` folder. On your master node, run the following command to deploy the wanted app
```bash
kubectl apply -f apps/<name of an app>.yaml
```

Check that the deployment is working as expected with:
```bash
kubectl get all -n <appName> -o wide --watch
```

## License
Bwahahahah.

No license. If you think this is useful for your usage, just use it. If you want to thank me, add a star on this repo.

If you copy the script for a blog / medium article, be nice and add a link to the original content