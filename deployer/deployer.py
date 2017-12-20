"""
This program deploys the keycloak and ga4gh server in docker containers

The deployment procedure can be configured using command line arguments
"""

import subprocess
import sys
import pkg_resources

import cmdparse as cmdparse
import funnel.funnel as funnel
import keycloak.keycloak as keycloak
import ga4gh.ga4gh as ga4gh

class deployer:
    """
    The deployer class manages the control flow and 
    passing of arguments for the deployment 
    sequence of the CanDIG project.

    The deployer first fetches command-line arguments
    from the cmdparse singleton (1).

    Then, the deployer sequentially launches
    each of the subdeployers. Each subdeployer
    manages the deployment of a single application
    server and its different deployment schemes (2).
    The command-line arguments are passed to these
    subdeployers.

    There are three such subdeployers:
    1. keycloak
    2. ga4gh
    3. funnel

    These will support Docker (possibly and Singularity) deployments.

    +--------------+              +-----------+
    | deployer     | ----(1)--->  | cmdparse  |
    |              | <-- args --  |           |
    +--------------+              +-----------+
     |
    (2)
     |               +----------+ -> docker
     +-> deploys --> |keycloak  |
     |               +----------+ -> singularity
     |
     |               +----------+ -> docker
     +-> deploys --> |ga4gh     |
     |               +----------+ -> singularity
     |
     |               +----------+ -> docker
     +-> deploys --> |funnel    |
                     +----------+
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
        # initialize the objects composed with the deployer:
        # - keycloak 
        # - ga4gh
        # - cmdparse
        # - funnel 
        self.keycloak = keycloak.keycloak()
        self.ga4gh = ga4gh.ga4gh()
        self.cmdparse = cmdparse.cmdparse()
        self.funnel = funnel.funnel()

        # get the command line arguments
        args = self.cmdparse.commandParser(sys.argv[1:])

        # initiate the deployment procedure 
        self.routeDeploy(args)

        # print deployment information
        self.printDeploy(args)
        exit()


    def routeDeploy(self, args):
        """
        Allocates deployment to each of the subdeployers
        Passes command-line arguments of each of the subdeployers:
        1. keycloak
        2. ga4gh
        3. funnel

        The subdeployers choose between their own deployment
        schemes based on the command-line arguments

        Manages cleanup prior to deployment
        Existing containers with duplicate names and ports
        from previous deployments will otherwise conflict 
        with the current deployment

        Parameters:

        argparse.Namespace args - Object containing command-line
                                  arguments as attributes
        """
        # remove duplicate containers
        self.containerTeardown(args.keycloakContainerName, args.ga4ghContainerName, args.funnelContainerName)

        # Deploy keycloak, ga4gh, and funnel 
        # sequentially based on the command-line arguments
        self.keycloak.route(args) # deploy keycloak
        self.ga4gh.route(args) # deploy ga4gh
        self.funnel.route(args) # deploy funnel


    def containerTeardown(self, keycloakContainerName, ga4ghContainerName, funnelContainerName):
        """
        Remove up any duplicate containers currently running or stopped that may conflict with deployment

        Removes:
        1. Docker containers running Keycloak
        2. Docker containers running GA4GH 

        Parameters:

        string keycloakContainerName - The name of the Docker container which holds the Keycloak server
        string ga4ghContainerName - The name of the Docker container which holds the GA4GH server
        string funnelContainerName - The name of the Docker container which holds the Funnel server

        Returns: None
        """
        try:
            # kill running containers:
            subprocess.call(["docker", "container", "kill", 
                             keycloakContainerName, 
                             ga4ghContainerName, 
                             funnelContainerName])
            # remove stopped containers:
            subprocess.call(["docker", "container", "rm", 
                             keycloakContainerName, 
                             ga4ghContainerName, 
                             funnelContainerName])
        except OSError:
            return # abort the function if Docker not installed
        

    def printDeploy(self, args):
        """
        Prints the login information post-deployment

        Parameters:

        argparse.Namespace args - Object containing command-line arguments 
                                  as attributes

        Returns: None
        """
        print("\nDeployment Complete.\n")
        print("Keycloak is accessible at:")

        # print out Docker container information for keycloak
        if not args.singularity:
            print("CONTAINER: " + args.keycloakContainerName)

        print("IP:PORT:   " + args.keycloakIP + ":" + args.keycloakPort)
        print("\nGA4GH Server is accessible at:")

        # print out Docker container information for ga4gh
        if not args.singularity:
            print("CONTAINER: " + args.ga4ghContainerName)

        print("IP:PORT:   " + args.ga4ghIP + ":" + args.ga4ghPort)

        # print out Docker container information for funnel
        if args.funnel:
            print("\nFunnel is accessible at:")
            print("CONTAINER: " + args.funnelContainerName)
            print("IP:PORT:   " + args.funnelIP + ":" + args.funnelPort)     

        # provide login usernames and passwords
        print("\nUser Account:")
        print("USERNAME:  " + args.userUsername)
        print("PASSWORD:  " + args.userPassword)
        print("\nAdmin Account:")
        print("USERNAME:  " + args.adminUsername)
        print("PASSWORD:  " + args.adminPassword + "\n")


def main():
    """
    The entrypoint function for the Deployer program

    Constructs a deployer instance
    The deployer constructor will parse the invocation
    for command-line arguments and proceed to deploy
    """
    deployer()

if __name__ == "__main__":
    main()
