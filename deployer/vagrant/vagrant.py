

import subprocess
import pkg_resources

class vagrant:

    def __init__(self):

        self.pkgName = __name__
        self.vagrantPath = '/'.join(('.', 'vagrant'))


    def vagrantDeploy(self, args):
        """
        Deploy ga4gh via singularity through a vagrant container

        We should also have an option that deploys them directly via singularity
        This would require us to test it in a linux environment

        Parameters:

        string vagrantDir
        argsObject args

        Returns: None
        """

        os.environ["VAGRANT_IP"] = args.vagrantIP
        os.environ["KEYCLOAK_PORT"] = args.keycloakPort
        os.environ["GA4GH_PORT"] = args.ga4ghPort

        vagrantDir = pkg_resources.resource_filename(self.pkgName, self.vagrantPath)
        subprocess.call(["vagrant", "up"], cwd=vagrantDir) 

