import subprocess
import pkg_resources

class vagrant:
    """
    Vagrant subdeployer

    Deploys vagrant containers via the Vagrantfile
    The Vagrant containers provide a Debian environment
    from which Singularity deployment is then executed

    The Vagrant deployment is a legacy feature that
    was used originally to test Singularity deployment
    for root environments
    """
    def __init__(self):
        """
        Constructor for the Vagrant subdeployer
        """
        # get the location of the vagrant directory
        self.pkgName = __name__
        self.vagrantPath = '/'.join(('.', 'vagrant'))
        self.vagrantDir = pkg_resources.resource_filename(self.pkgName, 
                                                          self.vagrantPath)

    def vagrantDeploy(self, args):
        """
        Deploy ga4gh via singularity through a vagrant container

        We should also have an option that deploys them directly via singularity
        This would require us to test it in a linux environment

        Parameters:

        argsObject args - object containing the command-line arguments

        Returns: None
        """

        # set environment variables for vagrant deployment
        os.environ["VAGRANT_IP"] = args.vagrantIP # ip address
        os.environ["KEYCLOAK_PORT"] = args.keycloakPort # keycloak port
        os.environ["GA4GH_PORT"] = args.ga4ghPort # ga4gh port

        # execute the VagrantFile
        # launches the Vagrant container
        subprocess.call(["vagrant", "up"], cwd=self.vagrantDir) 
