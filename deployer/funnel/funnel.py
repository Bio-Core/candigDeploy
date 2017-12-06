import subprocess
import pkg_resources
import json

class funnel:

    def __init__(self):
        """
        Constructor for the funnel deployer
        """
        self.pkgName = __name__
        self.funnelPath = '/'.join(('.'))

    def route(self, args):
        # deploy funnel if selected
        if args.funnel:
            self.config(args)
            self.deploy(args.funnelImageName, args.funnelContainerName, args.funnelPort)


    def deploy(self, funnelImageName, funnelContainerName, funnelPort):
        """
        Deploy the funnel server via docker

        Parameters:

        string funnelImageName
        string funnelContainerName
        string funnelPort
        string funnelDir

        Returns: None
        """
        funnelDir = pkg_resources.resource_filename(self.pkgName, self.funnelPath)
        build = ["docker", "build", "-t", funnelImageName, funnelDir]
        subprocess.call(build)

        # We must allow Funnel to call Docker from inside one of Docker's container
        # Hence we bind one of docker's sockets into its own container
        run = ["docker", "run", "-v", "/var/run/docker.sock:/var/run/docker.sock", "-p", funnelPort + ":3002", "--name", funnelContainerName, funnelImageName]
        subprocess.Popen(run)



    def config(self, args):
        """
        Writes the keycloak.json file for the funnel client

        Parameters:

        argsObject args - An object containing the command-line arguments as attributes
        string funnelDir - The absolute path of the deployed funnel files directory

        Returns: None
        """
        funnelDir = pkg_resources.resource_filename(self.pkgName, self.funnelPath)
        fileName = funnelDir + "/funnel-node/node-client/keycloak.json"

        authUrl = "http://" + args.keycloakIP + ":" + args.keycloakPort + "/auth"
        redirectList = [ "http://" + args.funnelIP + ":" + args.funnelPort + "/oidc_callback" ]
        secretDict = { "secret" : args.funnelSecret } 

        keycloakData = { "realm" : args.realmName, "auth-server-url": authUrl, "resource" : args.funnelID, "redirect_uris" : redirectList, "credentials" : secretDict }

        jsonData = json.dumps(keycloakData, indent=1)

        fileHandle = open(fileName, "w")
        fileHandle.write(jsonData)
        fileHandle.close()    
