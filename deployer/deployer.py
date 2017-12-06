"""
This program deploys the keycloak and ga4gh server in docker containers

The deployment procedure can be configured using command line arguments
"""

import subprocess
import sys
import pkg_resources

import cmdparse as cmdparse
import funnel.funnel as funnel
import vagrant.vagrant as vagrant
import keycloak.keycloak as keycloak
import ga4gh.ga4gh as ga4gh


class deployer:
    """
    The deployer class manages the control flow and 
    passing of arguments for the deployment 
    sequence of the CanDIG project.
    """

    def __init__(self):
        """
        Constructor for the deployer class
        
        Initializes attributes for the deployer class
        including default filepaths
        Starts the command-line argument parser
        and configures attributes and arguments accordingly 
        Passes control to the deployment router method

        Parameters: None

        Returns: deployer
        """

        dataArg = "default"

        # set the pathing names
        pkgName = __name__
        vagrantPath = '/'.join(('.', 'vagrant'))
        self.vagrantDir = pkg_resources.resource_filename(pkgName, vagrantPath)

        # initialize the objects composed with the deployer
        self.keycloak = keycloak.keycloak()
        self.ga4gh = ga4gh.ga4gh()
        self.cmdparse = cmdparse.cmdparse()
        self.funnel = funnel.funnel()
        self.vagrant = vagrant.vagrant()        

        # get the command line arguments
        args = self.cmdparse.commandParser(sys.argv[1:])

        postArgs = self.argsPostProcess(args)

        # set the dataArg based on whether more or no data
        # for the ga4gh server was requested
        if postArgs.noData:
            dataArg = "none"
        elif postArgs.extraData:
            dataArg = "extra"

        # initiate the deployment procedure 
        self.routeDeploy(postArgs, dataArg)

        # print deployment information
        self.printDeploy(postArgs)

        exit()


    def argsPostProcess(self, args):
        """
        Post-process the arguments with additional logic
        based on the command-line arguments themselves
        """
        if args.vagrant:
            args.keycloakIP = args.ga4ghIP = args.vagrantIP

        # override the other ip address if ip specified
        if args.ip:
            args.keycloakIP = args.ga4ghIP = args.funnelIP = args.ip

        return args


    def routeDeploy(self, args, dataArg):
        """
        Chooses which deployment scheme to use based on the arguments provided

        The deployment router selects between the following configurations:

        1. Keycloak
           a. Docker
           b. Singularity

        2. GA4GH
           a. Docker
           b. Singularity

        3. Funnel
           a. Docker

        4. Vagrant
           a. Keycloak via Singularity
           b. GA4GH via Singularity

        The GA4GH deployment is overidden by the Vagrant deployment if enabled.

        The router will also establish a GA4GH source code repoistory to push to containers if not available
        """

        # remove duplicate containers
        self.containerTeardown(args.keycloakContainerName, args.ga4ghContainerName, args.funnelContainerName)

        if args.vagrant:
            self.vagrant.vagrantDeploy(args)
        else:
            # deploy keycloak
            self.keycloak.route(args)
            # deploy ga4gh
            self.ga4gh.route(args, dataArg)
            # deploy funnel
            self.funnel.route(args)


    def containerTeardown(self, keycloakContainerName, ga4ghContainerName, funnelContainerName):
        """
        Remove up any duplicate containers currently running or stopped that may conflict with deployment

        Removes:
        1. Docker containers running Keycloak
        2. Docker containers running GA4GH 
        3. Vagrant containers

        Parameters:

        string keycloakContainerName - The name of the Docker container which holds the Keycloak server
        string ga4ghContainerName - The name of the Docker container which holds the GA4GH server
        string vagrantDir - The path of the directory which contains the Vagrantfile
        string funnelContainerName - The name of the Docker container which holds the Funnel server

        Returns: None
        """

        try:
            subprocess.call(["docker", "container", "kill", keycloakContainerName, ga4ghContainerName, funnelContainerName])
            subprocess.call(["docker", "container", "rm", keycloakContainerName, ga4ghContainerName, funnelContainerName])
            subprocess.call(["vagrant", "destroy", "-f", "default"], cwd=self.vagrantDir)
        except OSError:
            return
        

    def printDeploy(self, args):
        """
        Prints the login information post-deployment

        Parameters:

        argsObject args - An object containing the command-line arguments as attributes

        Returns: None
        """
        print("\nDeployment Complete.\n")
        print("Keycloak is accessible at:")

        if not args.singularity:
            print("IMAGE:     " + args.keycloakImageName) 
            print("CONTAINER: " + args.keycloakContainerName)

        print("IP:PORT:   " + args.keycloakIP + ":" + args.keycloakPort)
        print("\nGA4GH Server is accessible at:")

        if not args.singularity:
            print("IMAGE:     " + args.ga4ghImageName)
            print("CONTAINER: " + args.ga4ghContainerName)

        print("IP:PORT:   " + args.ga4ghIP + ":" + args.ga4ghPort)

        if args.funnel:
            print("\nFunnel is accessible at:")
            print("IMAGE:     " + args.funnelImageName)
            print("CONTAINER: " + args.funnelContainerName)
            print("IP:PORT:   " + args.funnelIP + ":" + args.funnelPort)     

        print("\nUser Account:")
        print("USERNAME:  " + args.userUsername)
        print("PASSWORD:  " + args.userPassword)
        print("\nAdmin Account:")
        print("USERNAME:  " + args.adminUsername)
        print("PASSWORD:  " + args.adminPassword + "\n")


def main():
    deployer()

if __name__ == "__main__":
    main()
