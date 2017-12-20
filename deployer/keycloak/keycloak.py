import subprocess
import pkg_resources
import os
import json
import gzip

class keycloak:
    """
    Subdeployer for the Keycloak server

    Deploys keycloak either via Docker or Singularity
    based on the command-line arguments

                              +--> deployDocker
    args                      |
    --> route --> config --> XOR
                              |
                              +--> deploySingularity
    """
    def __init__(self):
        """
        Constructor for the keycloak subdeployer
        """
        # get the location of the keycloak directory
        pkgName = __name__
        keycloakPath = '/'.join(('.'))
        self.keycloakDir = pkg_resources.resource_filename(pkgName, keycloakPath)

        configPath = '/'.join(('.', 'keycloakConfig.json'))
        self.configJson = pkg_resources.resource_filename(pkgName, configPath)

        zipPath = '/'.join(('.', "key.img.gz"))
        self.zipName = pkg_resources.resource_filename(pkgName, zipPath)

        imgPath = '/'.join(('.', 'key.img'))
        self.imgName = pkg_resources.resource_filename(pkgName, imgPath)

    def route(self, args):
        """
        Configure and initiate Keycloak's deployment

        Entrypoint method for the Keycloak subdeployer

        Parameters:

        argpase.Namespace args - The object containing the command-line 
                                 arguments as attributes

        Returns: None
        """
        # configure the keycloak server
        if not args.noConfig:
            self.config(args)
        # choose between docker and singularity keycloak deployment
        if args.singularity:
            self.deploySingularity(args)
        else:
            self.deployDocker(args)

    def deployDocker(self, args):
        """
        Pulls keycloak from Docker Hub and configures it

        Parameters:

        argpase.Namespace args - The object containing the command-line 
                                 arguments as attributes

        Returns: None
        """
        # pull the keycloak docker image from imageRepo
        imageRepo = "dalos/docker-keycloak"
        pull = ["docker", "pull", imageRepo]
        subprocess.call(pull)

        # Create a docker container 
        # passing in environment variables
        # tokenTracer - deploy token tracer (boolean)
        # REALM_NAME - realm name to use
        # ADMIN_USERNAME - admin account username
        # ADMIN_PASSWORD - admin account password
        # USER_USERNAME - user account username
        # USER_PASSWORD - user account password 
        create = ["docker", "create", "-p", args.keycloakPort + ":8080", 
                  "--name", args.keycloakContainerName, 
                  "-e", "tokenTracer=''" + str(args.tokenTracer) + "'", 
                  "-e", "REALM_NAME='" + args.realmName + "'",
                  "-e", "ADMIN_USERNAME='" + args.adminUsername + "'",
                  "-e", "ADMIN_PASSWORD='" + args.adminPassword + "'",
                  "-e", "USER_USERNAME='" + args.userUsername + "'",
                  "-e", "USER_PASSWORD='" + args.userPassword + "'", 
                  imageRepo]
        subprocess.call(create)

        # copy file to the docker container keycloakConfig.json
        copyConfig = ["docker", "cp", self.configJson, 
                      "{0}:/srv/keycloakConfig.json".format(args.keycloakContainerName)]
        subprocess.call(copyConfig)

        # start the keycloak server
        start = ["docker", "start", args.keycloakContainerName]
        subprocess.Popen(start)


    def deploySingularity(self, args):
        """
        Deploy keycloak server via a singularity container

        Parameters:

        argparse.Namespace args - object with command-line arguments as attributes

        Returns: None
        """        
        # remove existing images
        imgList = [self.imgName, self.zipName]
        for img in imgList:
            # check if the compressed/uncompressed image already exists
            duplicateImg = os.path.exists(img)
            # remove the existing image
            # images that have already been executed cannot be re-executed
            if duplicateImg:
                os.remove(img)

        # download the compressed singularity image
        gitUrl = "https://github.com/DaleDupont/singularity-keycloak/releases/download/0.0.1/key.img.gz"
        subprocess.call(["wget", gitUrl, "-P", self.keycloakDir])

        # decompress the compressed singularity image
        subprocess.call(["gunzip", self.zipName])

        # set the environment variables to use
        # inside the container
        # PORT - Port number Keycloak listens to
        # IPADDR - IP address of keycloak server
        # REALM_NAME - Realm name
        # ADMIN_USERNAME - Admin account username
        # ADMIN_PASSWORD - Admin account password
        # USER_USERNAME - User account username 
        # USER_PASSWORD - User account password
        envList = [("SINGULARITYENV_PORT", args.keycloakPort), 
                   ("SINGULARITYENV_IPADDR", args.keycloakIP), 
                   ("SINGULARITYENV_CONFIGFILE", self.configJson), 
                   ("SINGULARITYENV_REALM_NAME", args.realmName), 
                   ("SINGULARITYENV_ADMIN_USERNAME", args.adminUsername), 
                   ("SINGULARITYENV_ADMIN_PASSWORD", args.adminPassword), 
                   ("SINGULARITYENV_USER_USERNAME", args.userUsername), 
                   ("SINGULARITYENV_USER_PASSWORD", args.userPassword)]

        for envVar in envList:
            os.environ[envVar[0]] = envVar[1]

        # execute the image
        subprocess.Popen(["singularity", "run", "--writable", self.imgName])


    def config(self, args):
        """
        Writes the keycloak.json configuration file

        The configuration file determines the realms, clients, 
        and users that exist on the server and their settings

        Parameters:

        argparse.Namespace args - An object containing the command-line arguments as attributes

        Returns: None
        """        
        # load the configuration file
        with open(self.configJson, 'r') as configFile:
            # load the configuration data from the file
            configData = json.load(configFile)

            # update IP and ports of authenticated servers
            ga4ghUrl = "http://" + args.ga4ghIP + ":" + args.ga4ghPort + "/"
            funnelUrl = "http://" + args.funnelIP + ":" + args.funnelPort + "/"

            # update the realm name
            configData[0]["realm"] = args.realmName
            configData[0]["id"] = args.realmName

            configData[0]["roles"]["realm"][0]["containerId"] = args.realmName
            configData[0]["roles"]["realm"][1]["containerId"] = args.realmName

            # update the realm name for account client
            configData[0]["clients"][0]["baseUrl"] = "/auth/realms/" + args.realmName + "/account"
            configData[0]["clients"][0]["redirectUris"] = [ "/auth/realms/" + args.realmName + "/account/*" ]

            # update the realm name for security-admin-console client
            configData[0]["clients"][6]["baseUrl"] = "/auth/admin/" + args.realmName + "/console/index.html"
            configData[0]["clients"][6]["redirectUris"]  = ["/auth/admin/" + args.realmName + "/console/*"]

            # configure funnel client
            configData[0]["clients"][3]["clientId"] = args.funnelID
            configData[0]["clients"][3]["secret"] = args.funnelSecret
            configData[0]["clients"][3]["baseUrl"] = funnelUrl
            configData[0]["clients"][3]["redirectUris"] = [ funnelUrl + "*" ]
            #configData[0]["clients"][3]["adminUrl"] = funnelUrl

            # configure ga4gh client
            configData[0]["clients"][4]["clientId"] = args.ga4ghID
            configData[0]["clients"][4]["secret"] = args.ga4ghSecret
            configData[0]["clients"][4]["baseUrl"] =  ga4ghUrl
            configData[0]["clients"][4]["redirectUris"] = [ ga4ghUrl + "*" ]
            #configData[0]["clients"][4]["adminUrl"] = ga4ghUrl

            # configure the user and admin
            configData[0]["users"][0]["username"] = args.userUsername
            configData[1]["users"][0]["username"] = args.adminUsername

        # write the configuration data to the file
        with open(self.configJson, "w") as configFile:
            json.dump(configData, configFile, indent=1)
