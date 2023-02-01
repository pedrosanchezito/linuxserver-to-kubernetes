from yaml import load_all, dump_all, YAMLError

try:
    from yaml import CLoader as Loader, CDumper as Dumper

    with open('app_list.yaml', 'r') as input:
        data = load_all(input, Loader=Loader)
        for content in data:
            app = []
            # create namespace
            app.append({
                    'apiVersion': 'v1',
                    'kind': 'Namespace',
                    'metadata': {
                        'name': content['appName']
                    }
                })

            # create persistentVolumeClaims
            for volume in content['volumes']:
                if volume['volumeType'] == 'pvc':
                    app.append(
                        {
                            'apiVersion': 'v1',
                            'kind': 'PersistentVolumeClaim',
                            'metadata': {
                                'name': f"longhorn-{content['appName']}-{volume['volumeName']}-pvc",
                                'namespace': content['appName']
                            },
                            'spec': {
                                'accessModes': [
                                    'ReadWriteOnce'
                                ],
                                'storageClassName': 'longhorn',
                                'resources': {
                                    'requests': {
                                        'storage': f"{volume['volumeStorageInGi']}Gi"
                                    }
                                }
                            }
                        }
                    )

            # create deployment
            if 'envVars' in content:
                env = [{'name': var['name'], 'value': var['value']} for var in content['envVars']]
            else:
                env = None
            ports = [{'containerPort': port['port']} for port in content['ports']]
            volumeMounts = [{'mountPath': volume['volumeMountPath'], 'name': volume['volumeName']} for volume in content['volumes']]
            volumes = []
            for volume in content['volumes']:
                if volume['volumeType'] == 'pvc':
                    volumes.append({
                        'name': volume['volumeName'],
                        'persistentVolumeClaim': {'claimName': f"longhorn-{content['appName']}-{volume['volumeName']}-pvc"}
                    })
                else:
                    volumes.append({
                        'name': volume['volumeName'],
                        'hostPath': {'path': volume['volumeHostPath']}
                    })                    
            app.append({
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': f"{content['appName']}-deployment",
                    'namespace': content['appName'],
                    'labels': {
                        'app': f"{content['appName']}-deployment"
                    }
                },
                'spec': {
                    'replicas': 1,
                    'selector': {
                        'matchLabels': {
                            'app': content['appName']
                        }
                    },
                    'strategy': {
                        'type': 'Recreate'
                    },
                    'template': {
                        'metadata': {
                            'labels': {
                                'app': content['appName']
                            }                        
                        },
                        'spec': {
                            'containers': [{
                                'env': env,
                                'name': content['appName'],
                                'image': content['image'],
                                'ports': ports,
                                'volumeMounts': volumeMounts
                            }],
                            'restartPolicy': 'Always',
                            'volumes': volumes
                        }
                    }
                }
            })

            # create service
            ports = [{'name': port['name'], 'protocol': port['protocol'], 'port': port['port']} for port in content['ports']]

            app.append({
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': f"{content['appName']}-service",
                    'namespace': content['appName'],
                    'labels': {
                        'app': content['appName']
                    }
                },
                'spec': {
                    'selector': {
                        'app': content['appName']
                    },
                    'ports': ports,
                    'type': 'LoadBalancer'
                }
            })

            with open(f"apps/{content['appName']}.yaml", 'w') as output:
                dump_all(app, output, Dumper=Dumper)

        print('Configuration files created in /apps')

except YAMLError as e:
    if hasattr(e, 'problem_mark'):
        mark = e.problem_mark
        print(f'Syntax error in input file at position: ({mark.line+1}:{mark.column+1})')
