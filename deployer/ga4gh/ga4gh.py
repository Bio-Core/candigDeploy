import subprocess
import shutil
import os
import pkg_resources
import json
import yaml


class ga4gh:
    """
    The Global Alliance for Genomics and Health Server subdeployer

    Deploys GA4GH Server on either a Docker
    or singularity container based on the arguments provided
    """

    def __init__(self):
        """
        Constructor for the GA4GH subdeployer

        Sets the paths to coordinate deployment
        """
        # establish relative directory names
        # for inclusion of files
        pkgName = __name__

        # determine the ga4gh subdeployer directory
        ga4ghPath = '/'.join(('.'))
        self.ga4ghDir = pkg_resources.resource_filename(pkgName, ga4ghPath)

        # get the location of the local subdeployer client_secrets file
        secretPath = '/'.join(('.', 'config', 'client_secrets.json'))
        self.secretName = pkg_resources.resource_filename(pkgName, secretPath)

        # get the ga4gh-server source code directory location
        ga4ghSource = '/'.join(('.', 'ga4gh-server'))
        self.sourceName = pkg_resources.resource_filename(pkgName, ga4ghSource)

        # get the location of oidc_config.yml
        configPath = '/'.join(('.', 'config', 'oidc_config.yml'))
        self.oidcConfigName = pkg_resources.resource_filename(pkgName, configPath)

        # get the path of the ga4gh singularity image
        imgPath = '/'.join(('.', 'ga4gh.simg'))
        self.imgName = pkg_resources.resource_filename(pkgName, imgPath)


    def route(self, args):
        """
        Deploy via singularity or docker based on command-line arguments

        Parameters:

        argparse.Namespace args - Object with command-line arguments as attributes

        Returns: None
        """
        # configure configuration files first
        self.config(args)

        # deploy by singularity or docker
        if args.singularity:
            self.deploySingularity(args)
        else:
            self.deployDocker(args.ga4ghContainerName, args.ga4ghPort)

    def deployDocker(self, ga4ghContainerName, ga4ghPort):
        """
        Pulls a pre-built ga4gh server image and runs as a Docker container

        Copies configuration files onto the container and
        configures ports before executing

        Parameters:

        str ga4ghContainerName - the Docker container name holding the ga4gh server
        str ga4ghPort - The port number of the ga4gh server

        Returns: None
        """
        # pull the ga4gh server image from the dalos repository
        imageRepo = "dalos/docker-ga4gh"
        pull = ["docker", "pull", imageRepo]
        subprocess.call(pull)

        # create the container
        create = ["docker", "create", "-p", ga4ghPort + ":8000", 
               "--name", ga4ghContainerName, imageRepo]
        subprocess.call(create)

        # the location of the directory to which the pip installation is located
        configDir = "/usr/local/lib/python2.7/dist-packages/ga4gh/server/config"

        # write the location of the client secrets to oidc_config.yml
        self.configOidc(configDir + "/client_secrets.json")

        # copy the client secrets and oidc config into the container
        copyConfig = ["docker", "cp", self.oidcConfigName, 
                      "{0}:{1}/oidc_config.yml".format(ga4ghContainerName, configDir)]
        subprocess.call(copyConfig)

        copySecrets = ["docker", "cp", self.secretName, 
                       "{0}:{1}/client_secrets.json".format(ga4ghContainerName, configDir)]
        subprocess.call(copySecrets)

        # start the container as a separate background process
        start = ["docker", "start", ga4ghContainerName]
        subprocess.Popen(start)

    def configOidc(self, path):
        """
        Sets the location of the GA4GH configuration files
        for client_secrets.json and oidc_config.yml
        for singularity deployment

        Parameters: None

        Returns: None
        """
        # open the oidc_config.yml file
        fileHandle = open(self.oidcConfigName)
        # read the YAML data
        yamlData = yaml.load(fileHandle)   
        # rewrite oidc_config.yml to point 
        # to the location of client_secrets.json
        yamlData['frontend']['OIDC_CLIENT_SECRETS'] = path
        fileHandle.close()

        # write the data to the oidc_config.yml file
        fileHandle = open(self.oidcConfigName, "w")
        yaml.dump(yamlData, fileHandle)
        fileHandle.close()

    def deploySingularity(self, args):
        """
        Deploy ga4gh server via a singularity container

        This deployment scheme does not require root access

        Parameters:

        argparse.Namespace args - command-line arguments object

        Returns: None
        """

        # determine if the ga4gh singularity image already exists
        duplicateImg = os.path.exists(self.imgName)
        # remove the image if the override argument is set
        if args.override and duplicateImg:
            os.remove(self.imgName)

        # pull the singularity ga4gh image from singularity hub
        subprocess.call(["singularity", "pull", "--name", self.imgName, 
                         "shub://DaleDupont/singularity-ga4gh:latest"])

        # prepare configuration files for singularity deployment
        self.configOidc(self.secretName)

        # set the environment variables to use
        # inside the singularity container
        # GA4GH_PORT - Port number of the ga4gh server
        # GA4GH_IP - IP address of the ga4gh server
        # GA4GH_CONFIG - Absolute location of the oidc_config.yml file
        envList = [("SINGULARITYENV_GA4GH_PORT", args.ga4ghPort), 
                   ("SINGULARITYENV_GA4GH_IP", args.ga4ghIP), 
                   ("SINGULARITYENV_GA4GH_CONFIG", self.oidcConfigName)]
        for envVar in envList:
            os.environ[envVar[0]] = envVar[1]

        # run the singularity container
        run = ["singularity", "run", self.imgName]
        subprocess.Popen(run)

    def config(self, args):
        """ 
        Writes the new client_secrets.json file 

        For registration of ga4gh client with keycloak CanDIG realm

        Parameters:

        argparse.Namespace args - An object containing the command-line arguments as attributes

        Returns: None
        """
        # set the data to write to client_secrets.json
        keycloakRootUrl    = "http://" + args.keycloakIP + ":" + args.keycloakPort + "/auth"
        issuer             = keycloakRootUrl + "/realms/" + args.realmName
        openidUri          =  issuer + "/protocol/openid-connect"
        authUri            = openidUri + "/auth"
        tokenUri           =  openidUri + "/token"
        tokenIntrospectUri = tokenUri + "/introspect"
        userinfoUri        = openidUri + "/userinfo"
        redirectUri        = "http://" + args.ga4ghIP + ":" + args.ga4ghPort + "/oidc_callback"

        # generate and write the json data
        keycloakSecret = { 
            "web": { 
                "auth_uri" : authUri, 
                 "issuer" : issuer, 
                 "client_id" : args.ga4ghID, 
                 "client_secret" : args.ga4ghSecret,
                 "redirect_uris" : [ redirectUri ], 
                 "token_uri" : tokenUri, 
                 "token_introspection_uri" : tokenIntrospectUri, 
                 "userinfo_endpoint" : userinfoUri } }

        jsonData = json.dumps(keycloakSecret, indent=1)

        # Rewrite the client_secrets.json file with the new configuration
        fileHandle = open(self.secretName, "w")
        fileHandle.write(jsonData)
        fileHandle.close()
