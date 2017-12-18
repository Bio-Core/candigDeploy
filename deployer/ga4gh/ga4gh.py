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
        self.pkgName = __name__

        # determine the ga4gh subdeployer directory
        ga4ghPath = '/'.join(('.'))
        self.ga4ghDir = pkg_resources.resource_filename(self.pkgName, ga4ghPath)

        # get the location of the local subdeployer client_secrets file
        secretLocalPath = '/'.join(('.', 'config', 'client_secrets.json'))
        self.secretLocalName = pkg_resources.resource_filename(self.pkgName, secretLocalPath)

        # get the ga4gh-server source code directory location
        ga4ghSource = '/'.join(('.', 'ga4gh-server'))
        self.sourceName = pkg_resources.resource_filename(self.pkgName, ga4ghSource)

        # get the location of oidc_config.yml
        configPath = '/'.join(('.', 'config', 'oidc_config.yml'))
        self.oidcConfigName = pkg_resources.resource_filename(self.pkgName, configPath)

        # identify the relative location of the client_secrets.json
        # in the source code
        secretPath = "/ga4gh/server/config/client_secrets.json"
        self.secretSourceName = self.sourceName + secretPath

    def route(self, args, dataArg):

        # initialize the ga4gh source code repository 
        self.initSrc(args)

        # deploy via singularity or docker
        # based on args
        if args.singularity:
            self.deploySingularity(args)
        elif not args.noGa4gh:
            self.deployDocker(args.ga4ghImageName, 
                              args.ga4ghContainerName,
                              args.ga4ghPort, dataArg)


    def deployDocker(self, ga4ghImageName, ga4ghContainerName, ga4ghPort, dataArg):
        """
        Deploys the ga4gh server

        Builds the ga4gh server docker image and runs it

        Parameters:

        string ga4ghImageName - Docker image name
        string ga4ghContainerName - Docker container name
        string ga4ghPort - Port number of the GA4GH server to listen on
        string dataArg - Data deployment scheme for the GA4GH server
                         One of: {"none", "default", "extra"}

        Returns: None
        """

        # prepare data argument for feeding into docker build
        dataArg = "dataArg=" + dataArg

        # execute docker to build the ga4gh image
        build = ["docker",  "build", "-t", ga4ghImageName, 
                 "--build-arg", dataArg, self.ga4ghDir]
        subprocess.call(build)

        # run the ga4gh server via a docker container
        run = ["docker", "run", "-p", ga4ghPort + ":8000", 
               "--name", ga4ghContainerName, ga4ghImageName]
        subprocess.Popen(run)


    def configSingularity(self):
        """
        Sets the location of the GA4GH configuration files
        for client_secrets.json and oidc_config.yml
        for singularity deployment
        """

        # get the location of client_secrets.json
        #clientSecretPath = '/'.join(('.', 'config', 'client_secrets.json'))
        #clientSecretFile = pkg_resources.resource_filename(self.pkgName, clientSecretPath)

        # rewrite oidc_config.yml to point to the location
        # of client_secrets.json
        fileHandle = open(self.oidcConfigName)
        yamlData = yaml.load(fileHandle)   
        yamlData['frontend']['OIDC_CLIENT_SECRETS'] = self.secretLocalName
        fileHandle.close()
        fileHandle = open(self.oidcConfigName, "w")
        yaml.dump(yamlData, fileHandle)
        fileHandle.close()

    def deploySingularity(self, args):
        """
        Deploy ga4gh server via a singularity container

        This deployment scheme does not require root access

        Parameters:

        args - command-line arguments object

        Returns: None
        """
        # get the path of the ga4gh singularity image
        imgPath = '/'.join(('.', 'ga4gh.simg'))
        imgName = pkg_resources.resource_filename(self.pkgName, imgPath)

        # determine if the ga4gh singularity image already exists
        duplicateImg = pkg_resources.resource_exists(self.pkgName, imgPath)

        # remove the image if the override argument is set
        if args.override:
            os.remove(imgName)

        # pull the singularity ga4gh image from singularity hub
        subprocess.call(["singularity", "pull", "--name", imgName, 
                         "shub://DaleDupont/singularity-ga4gh:latest"])

        # prepare configuration files for singularity deployment
        self.configSingularity()

        # set the environment variables to use
        # inside the singularity container
        envList = [("SINGULARITYENV_GA4GH_PORT", args.ga4ghPort), 
                   ("SINGULARITYENV_GA4GH_IP", args.ga4ghIP), 
                   ("SINGULARITYENV_GA4GH_CONFIG", self.oidcConfigName)]
        for envVar in envList:
            os.environ[envVar[0]] = envVar[1]

        # run the singularity container
        run = ["singularity", "run", imgName]
        subprocess.Popen(run)

    def config(self, args):
        """ 
        Writes the new client_secrets.json file 

        For registration of ga4gh client with keycloak CanDIG realm

        Parameters:

        argsObject args - An object containing the command-line arguments as attributes

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
        keycloakSecret = { "web": { "auth_uri" : authUri, 
                                    "issuer" : issuer, 
                                    "client_id" : args.ga4ghID, 
                                    "client_secret" : args.ga4ghSecret,
                                    "redirect_uris" : [ redirectUri ], 
                                    "token_uri" : tokenUri, 
                                    "token_introspection_uri" : tokenIntrospectUri, 
                                    "userinfo_endpoint" : userinfoUri } }

        jsonData = json.dumps(keycloakSecret, indent=1)

        # Rewrite the client_secrets.json file with the new configuration
        fileHandle = open(self.secretLocalName, "w")
        fileHandle.write(jsonData)
        fileHandle.close()

        # copy to the reference directory
        shutil.copy(self.secretLocalName, self.secretSourceName)

    def initSrc(self, args):
        """
        Initializes the local ga4gh source code repository on the host machine

        This function is used if there is no pre-existing ga4gh source to use
        This code is later used to build the server on the docker container 

        Parameters:

        argsObject args - An object containing the command-line arguments as attributes

        Returns: None
        """
        # determine if the source code directory already exists
        duplicateDir = pkg_resources.resource_exists(self.pkgName, self.sourceName)

        # halt if a duplicate directory exists 
        # and no override command has been given
        if (not duplicateDir) or args.override:
            # remove the existing source code 
            # if a duplicate directory exists
            # and the override command has been given
            if args.override and duplicateDir:
                 shutil.rmtree(self.sourceName)

            # clone in the source-code repository
            # cloneUrl determines which GitHub repository to use
            cloneUrl = "https://github.com/Bio-Core/ga4gh-server.git"
            # cloneBranch determines which branch to clone
            cloneBranch = "auth-deploy-stable"
            clone = ["git", "clone", "--branch", 
                     cloneBranch, cloneUrl, self.sourceName]
            subprocess.call(clone)

            # copy over the dataPrep file into the GA4GH source code 
            # prior to installation
            # the dataPrep file is the current means of offering 
            # different deployment options for test data
            #fileDict = { "/config/dataPrep.py" : "/dataPrep.py" } 

            # copy over the configuration files into the source code
            #for ifile in fileDict:
            #    shutil.copyfile(self.ga4ghDir + ifile, 
            #                    self.sourceName + fileDict[ifile])

            shutil.copyfile(self.ga4ghDir + "/config/dataPrep.py", 
                            self.sourceName + "/dataPrep.py")

            shutil.copyfile(self.oidcConfigName, self.sourceName + "/ga4gh/server/config/oidc_config.yml")



            # configure the GA4GH server
            self.config(args)

        elif (not args.noConfig):
            # reconfigure the client_secrets.json only
            os.remove(self.secretSourceName)

            # configure the GA4GH server
            self.config(args)
        else:
            print("Using existing source directory and configuration " + self.sourceName)
            print("Command line configuration options for GA4GH will not be used")
