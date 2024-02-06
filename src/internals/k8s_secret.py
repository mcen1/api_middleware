from internals.k8s import k8s_client, namespace
from internals.log import log
from base64 import b64decode

class Ks8Secret():
    def __init__(self, k8s_client: k8s_client):
        #get infrastructure secret from k8s
        self._secret_name = f"team-infrastructure"
        self._secret_data = None
        self.set_k8s_env()
        
    def set_k8s_env(self):
        if not self._secret_data:
            self._k8s_secret = k8s_client.getNamespaceSecret(
                str(self._secret_name),
                str(namespace)
            )
            if hasattr(self._k8s_secret, 'data'):
                log.info(
                    f'{{'
                    f'"module":"/team_infrastructure/webhook",'
                    f'"action":"retrieve_secrets",'
                    f'"message":"The required k8s secret, `{ self._secret_name }` was found in the `{ namespace }` namespace."'
                    f'}}'
                )
                self._secret_data = self._k8s_secret.data
            else:
                log.critical(
                    f'{{'
                    f'"module":"/team_infrastructure/webhook",'
                    f'"action":"retrieve_secrets",'
                    f'"message":"The required k8s secret, `{ self._secret_name }` could not be found in the `{ namespace }` namespace. Please ensure it exists and includes `git_username`, `git_access_token` and `awx_access_token`, `awx_host` and `awx_env`."'
                    f'}}'
                )
            
    def get_git_username(self):
        git_username = None
        self.set_k8s_env()
        if self._secret_data and 'git_username' in self._secret_data:
            git_username = b64decode(self._secret_data['git_username']).decode('utf-8').rstrip()
        return git_username

    def get_git_access_token(self):
        git_access_token = None
        self.set_k8s_env()
        if self._secret_data and 'git_access_token' in self._secret_data:
            git_access_token = b64decode(self._secret_data['git_access_token']).decode('utf-8').rstrip()
        return git_access_token

    def get_awx_development_access_token(self):
        awx_access_token = None
        self.set_k8s_env()
        if self._secret_data and 'awx_development_access_token' in self._secret_data:
            awx_access_token = b64decode(self._secret_data['awx_development_access_token']).decode('utf-8').rstrip()
        return awx_access_token

    def get_awx_staging_access_token(self):
        awx_access_token = None
        self.set_k8s_env()
        if self._secret_data and 'awx_staging_access_token' in self._secret_data:
            awx_access_token = b64decode(self._secret_data['awx_staging_access_token']).decode('utf-8').rstrip()
        return awx_access_token

    def get_awx_production_access_token(self):
        awx_access_token = None
        self.set_k8s_env()
        if self._secret_data and 'awx_production_access_token' in self._secret_data:
            awx_access_token = b64decode(self._secret_data['awx_production_access_token']).decode('utf-8').rstrip()
        return awx_access_token

    def get_awx_env(self):
        awx_env = None
        self.set_k8s_env()
        if self._secret_data and 'awx_env' in self._secret_data:
            awx_env = b64decode(self._secret_data['awx_env']).decode('utf-8').rstrip().lower()
        return awx_env

    def get_awx_host_data(self):
        awx_env = self.get_awx_env()
        awx_host = ""
        awx_instance = "Not Defined"
        if awx_env == "development":
            awx_host = "ap-dev.domain.CompanyCompany.com"
            awx_instance = "AWX Development"
        elif awx_env == "staging":
            awx_host = "ap-staging.domain.CompanyCompany.com"
            awx_instance = "AWX Staging"
        elif awx_env == "production":
            awx_host = "ap.domain.CompanyCompany.com"
            awx_instance = "AWX Production"
        return awx_host, awx_instance


#Create/Get k8s secrets
k8s_secret = Ks8Secret(k8s_client)
