from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from internals.log import log, app_title
from os import environ


class Kubernetes():
    def __init__(self, namespace: str):
        self.namespace = namespace

    def _k8s_client_setup(self):
        if not hasattr(self, 'core_api') or not hasattr(self, 'batch_api'):
            log.info(
                f'{{'
                f'"module":"k8s",'
                f'"action":"k8s_client_setup",'
                f'"message":"k8s client setup initiated."'
                f'}}'
            ) 
            try:
                config.load_kube_config(
                    config_file=environ.get("KUBECONFIG", "/usr/team/.kube/kubeconfig"),
                    context=environ.get("KUBECONTEXT"),
                )
                self.core_api = client.CoreV1Api()
                self.batch_api = client.BatchV1Api()
                self._createNamespace()
            except config.ConfigException:
                log.critical(
                    f'{{'
                    f'"module":"k8s",'
                    f'"action":"load_kube_config",'
                    f'"message":"kubeconfig could not be found, please add it to the environment."'
                    f'}}'
                )

    def _createNamespace(self):      
        #Check if namespace exists in the cluster and if not create it
        try:
            self._k8s_client_setup()
            k8s_client = self.core_api
            namespaces = k8s_client.list_namespace()
            if not any(namespace.metadata.name == str(self.namespace) for namespace in namespaces.items):
                log.info(
                    f'{{'
                    f'"module":"k8s",'
                    f'"action":"create_namespace",'
                    f'"message":"Created k8s namespace,{ self.namespace } as a matching one was not found."'
                    f'}}'
                ) 
                namespace_metadata = client.V1ObjectMeta(name = self.namespace)
                self.core_api.create_namespace(
                    client.V1Namespace(metadata = namespace_metadata)
                )
            else:
                log.info(
                    f'{{'
                    f'"module":"k8s",'
                    f'"action":"create_namespace",'
                    f'"message":"Existing k8s namespace, { self.namespace } will be used for the { app_title }."'
                    f'}}'
                )
            self.namespace_defined = True
        except ApiException as exception:
            log.critical(
                f'{{'
                f'"module":"k8s",'
                f'"action":"create_namespace",'
                f'"An unknown error ocurred when trying to check the k8s namespace, { self.namespace }. Exception: { exception }."'
                f'}}'
            ) 
            self.namespace_defined = False

    def createPodContainer(self, image, container_name, pull_policy, args = [], commands = [], volume_list = [], env_list = []):
        try:
            self._k8s_client_setup()
            volume_mounts = []
            if volume_list:
                for item in volume_list:
                    volume_mounts.append(
                        client.V1VolumeMount(
                            name = str(item.get("volume_name")),
                            mount_path = str(item.get("volume_mount_path")),
                        )
                    )

            env = []
            if env_list:
                for item in env_list:
                    if item.get("value") != None and item.get("value") != "":
                        env.append(
                            client.V1EnvVar(
                                name=str(item.get("name")),
                                value=str(item.get("value"))
                            )
                        )
                    elif item.get("secret_key") != None and item.get("secret_key") != "":
                        env.append(
                            client.V1EnvVar(
                                name = str(item.get("name")),
                                value_from = client.V1EnvVarSource(
                                    secret_key_ref = client.V1SecretKeySelector(
                                        key = str(item.get("secret_key")),
                                        name = str(item.get("name")),
                                        optional = False
                                    )
                                )
                            )
                        )


            container = client.V1Container(
                image = image,
                name = container_name,
                image_pull_policy = pull_policy,
                args = args,
                command = commands,
                volume_mounts = volume_mounts,
                env = env
            )

            log.info(
                f'{{'
                f'"module":"k8s",'
                f'"action":"create_container",'
                f'"message":"Created k8s container with name: { container.name }, image: { container.image }, args: { container.args }."'
                f'}}'
            )
            return container
        except Exception as exception:
            log.critical(
                f'{{'
                f'"module":"k8s",'
                f'"action":"create_pod_container",'
                f'"An unknown error ocurred when trying to create the k8s pod container, { container_name }. Exception: { exception }."'
                f'}}'
            )

    #The resulting template specification object defines the pods that will be created from this pod template.
    def createPodTemplateSpec(self, pod_name, container, volume_list = []):
        try:
            self._k8s_client_setup()
            image_pull_secrets = []
            volumes = []
            if volume_list:
                for item in volume_list:
                    volumes.append(
                        client.V1Volume(
                            name = str(item.get("volume_name")),
                            secret = client.V1SecretVolumeSource(
                                secret_name = str(item.get("secret_name")),
                                items = [
                                    client.V1KeyToPath(
                                        key = str(item.get("secret_key")),
                                        path = str(item.get("secret_path"))
                                    )
                                ]
                            )
                        )
                    )

            
            if str(item.get("secret_key")) == ".dockerconfigjson":
                image_pull_secrets.append(client.V1LocalObjectReference(str(item.get("secret_name"))))
            pod_template = client.V1PodTemplateSpec(
                spec = client.V1PodSpec(
                    restart_policy="Never",
                    containers = [container],
                    volumes = volumes,
                    image_pull_secrets = image_pull_secrets
                ),
                metadata = client.V1ObjectMeta(
                    name=pod_name,
                    labels = {"pod_name": pod_name}
                )
            )
            log.info(
                f'{{'
                f'"module":"k8s",'
                f'"action":"create_pod_template_spec",'
                f'"message":"Created k8s pod template spec with name: {pod_name}."'
                f'}}'
            )
            return pod_template
        except Exception as exception:
            log.critical(
                f'{{'
                f'"module":"k8s",'
                f'"action":"create_pod_template_spec",'
                f'"An unknown error ocurred when trying to create the k8s pod template spec, { pod_name }. Exception: { exception }."'
                f'}}'
            )

    def createJob(self, job_name, pod_template):
        try:
            self._k8s_client_setup()
            self.job_name = job_name
            metadata = client.V1ObjectMeta(name = job_name, labels = {"job_name": job_name})
            job = client.V1Job(
                api_version = "batch/v1",
                kind = "Job",
                metadata = metadata,
                spec = client.V1JobSpec(backoff_limit = 0, template = pod_template),
            )
            log.info(
                f'{{'
                f'"module":"k8s",'
                f'"action":"create_job",'
                f'"message":"Created k8s job with name: {job_name}."'
                f'}}'
            )
            return job
        except Exception as exception:
            log.critical(
                f'{{'
                f'"module":"k8s",'
                f'"action":"create_job",'
                f'"An unknown error ocurred when trying to create the k8s job, { job_name }. Exception: { exception }."'
                f'}}'
            )

    def executeJob(self, namespace, job):
        try:
            self._k8s_client_setup()
            k8s_batch_client = self.batch_api
            k8s_job = k8s_batch_client.create_namespaced_job(namespace, job)
            log.info(
                f'{{'
                f'"module":"k8s",'
                f'"action":"execute_job",'
                f'"message":"Started executing k8s job with name: {self.job_name}."'
                f'}}'
            )
            return k8s_job
        except Exception as exception:
            log.critical(
                f'{{'
                f'"module":"k8s",'
                f'"action":"execute_job",'
                f'"An unknown error ocurred when trying to execute the k8s job, { self.job_name }. Exception: { exception }."'
                f'}}'
            )

    def getNamespaceSecret(self, secret_name, namespace):      
        try:
            self._k8s_client_setup()
            k8s_client = self.core_api
            k8s_secret = k8s_client.read_namespaced_secret(f"{ secret_name }", f"{ namespace }")
            log.info(
                f'{{'
                f'"module":"k8s",'
                f'"action":"read_namespaced_secret",'
                f'"message":"A k8s secret with the name of: { secret_name }, was requested."'
                f'}}'
            )
            return k8s_secret
        except Exception as exception:
            log.critical(
                f'{{'
                f'"module":"k8s",'
                f'"action":"read_namespaced_secret",'
                f'"An unknown error ocurred when trying to request a k8s secret, { secret_name }. Exception: { exception }."'
                f'}}'
            )

#Create/Get k8s namespace
namespace = f"team-automation"
k8s_client = Kubernetes(namespace)
