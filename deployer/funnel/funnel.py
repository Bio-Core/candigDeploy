import subprocess
import pkg_resources
import json

class funnel:
    """
    The funnel subdeployer to manage funnel deployment via Docker
    """
    def __init__(self):
        """
        Constructor for the funnel subdeployer

        Determines paths to coordinate deployment
        """
        self.pkgName = __name__
        funnelPath = '/'.join(('.'))
        self.funnelDir = pkg_resources.resource_filename(self.pkgName, funnelPath)

    def route(self, args):
        """
        The entry-point method for the subdeployer

        Coordinates the deployment scheme based on the arguments
        Configures and deploys the software container holding funnel

        Parameters:

        argparse.Namespace args - command-line arguments object
        """
        # deploy funnel if selected
        if args.funnel:
            # configure the funnel setup based on args
            self.config(args)
            # run the Docker container
            self.deployDocker(args.funnelImageName, 
                              args.funnelContainerName, 
                              args.funnelPort)


    def deployDocker(self, funnelImageName, funnelContainerName, funnelPort):
        """
        Deploy the funnel server via docker

        Parameters:

        string funnelImageName
        string funnelContainerName
        string funnelPort

        Returns: None
        """
        build = ["docker", "build", "-t", funnelImageName, self.funnelDir]
        subprocess.call(build)

        # We must allow Funnel to call Docker 
        # from inside one of Docker's container
        # Hence we bind one of docker's sockets into its own container
        run = ["docker", "run", 
               "-v", "/var/run/docker.sock:/var/run/docker.sock", 
               "-p", funnelPort + ":3002", 
               "--name", funnelContainerName, funnelImageName]
        subprocess.Popen(run)


    def config(self, args):
        """
        Writes the keycloak.json file for the funnel client

        Parameters:

        argparse.Namespace args - An object containing the command-line 
                                  arguments as attributes

        Returns: None
        """
        fileName = self.funnelDir + "/funnel-node/node-client/keycloak.json"

        authUrl = "http://" + args.keycloakIP + ":" + args.keycloakPort + "/auth"
        redirectList = [ "http://" + args.funnelIP + ":" + args.funnelPort + "/oidc_callback" ]
        secretDict = { "secret" : args.funnelSecret } 

        keycloakData = { "realm" : args.realmName, 
                         "auth-server-url": authUrl, 
                         "resource" : args.funnelID, 
                         "redirect_uris" : redirectList, 
                         "credentials" : secretDict }

        jsonData = json.dumps(keycloakData, indent=1)

        fileHandle = open(fileName, "w")
        fileHandle.write(jsonData)
        fileHandle.close()
