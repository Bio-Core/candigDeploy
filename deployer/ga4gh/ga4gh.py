import subprocess
import shutil
import os
import pkg_resources
import json
import yaml


class ga4gh:

    def __init__(self):
        self.pkgName = __name__
        self.ga4ghPath = '/'.join(('.'))


    def route(self, args, dataArg):

        # initialize the repository containing the ga4gh source code locally if unspecified
        self.initSrc(args)

        # choose between vagrant deployment or singularity or docker deployment of ga4gh server 
        if args.singularity:
            self.deploySingularity(args)
        elif not args.noGa4gh:
            self.deployDocker(args.ga4ghImageName, args.ga4ghContainerName,\
                             args.ga4ghPort, args.ga4ghSrc, dataArg)


    def deployDocker(self, ga4ghImageName, ga4ghContainerName, ga4ghPort, ga4ghSrc, dataArg):
        """
        Deploys the ga4gh server

        Builds the ga4gh server docker image and runs it

        Parameters:

        string ga4ghImageName - 
        string ga4ghContainerName -
        string ga4ghDir - 
        string ga4ghPort - 
        string ga4ghSrc - 
        string dataArg -

        Returns: None
        """

        # build the ga4gh server
        srcArg = "sourceDir=" + ga4ghSrc
        dataArg = "dataArg=" + dataArg

        ga4ghDir = pkg_resources.resource_filename(self.pkgName, self.ga4ghPath)
        build = ["docker",  "build", "-t", ga4ghImageName, "--build-arg", srcArg, "--build-arg", dataArg, ga4ghDir]
        subprocess.call(build)
        # run the ga4gh server
        run = ["docker", "run", "-p", ga4ghPort + ":8000", "--name", ga4ghContainerName, ga4ghImageName]
        subprocess.Popen(run)


    def configSingularity(self):
        """
        Sets the location of the client_secrets JSON file
        in the configuration
        """
        configPath = '/'.join(('.', 'config', 'oidc_config.yml'))
        configFile = pkg_resources.resource_filename(self.pkgName, configPath)

        clientSecretPath = '/'.join(('.', 'config', 'client_secrets.json'))
        clientSecretFile = pkg_resources.resource_filename(self.pkgName, clientSecretPath)

        fileHandle = open(configFile)
        yamlData = yaml.load(fileHandle)   
        yamlData['OIDC_CLIENT_SECRETS'] = clientSecretFile
        fileHandle.close()
        fileHandle = open(configFile, "w")
        yaml.dump(yamlData, fileHandle)
        fileHandle.close()


    def deploySingularity(self, args):
        """
        Deploy ga4gh server via a singularity container

        This deployment scheme does not require root access

        Parameters:

        string imgDir - The path containing the 

        Returns: None
        """
        imgPath = '/'.join(('.', 'ga4gh.simg'))
        imgName = pkg_resources.resource_filename(self.pkgName, imgPath)
        duplicateImg = pkg_resources.resource_exists(self.pkgName, imgPath)

        if args.override:
            os.remove(imgName)

        subprocess.call(["singularity", "pull", "--name", imgName, "shub://DaleDupont/singularity-ga4gh:latest"])

        self.configSingularity()

        configPath = '/'.join(('.', 'config', 'oidc_config.yml'))
        configFile = pkg_resources.resource_filename(self.pkgName, configPath)

        # set the environment variables to use
        # inside the singularity container
        envList = [("SINGULARITYENV_GA4GH_PORT", args.ga4ghPort), 
                   ("SINGULARITYENV_GA4GH_IP", args.ga4ghIP), 
                   ("SINGULARITYENV_GA4GH_CONFIG", configFile)]

        for envVar in envList:
            os.environ[envVar[0]] = envVar[1]

        subprocess.Popen(["singularity", "run", imgName])


    def config(self, ga4ghSourceDir, args):
        """ 
        Writes the new client_secrets.json file 

        For registration of ga4gh client with keycloak CanDIG realm

        Parameters:

        string ga4ghSourceDir - The path of the directory containing the GA4GH source code
        argsObject args - An object containing the command-line arguments as attributes

        Returns: None
        """
        clientSecretPath = '/'.join(('.', 'config', 'client_secrets.json'))
        clientSecretFile = pkg_resources.resource_filename(self.pkgName, clientSecretPath)

        keycloakRootUrl    = "http://" + args.keycloakIP + ":" + args.keycloakPort + "/auth"
        issuer             = keycloakRootUrl + "/realms/" + args.realmName
        openidUri          =  issuer + "/protocol/openid-connect"
        authUri            = openidUri + "/auth"
        tokenUri           =  openidUri + "/token"
        tokenIntrospectUri = tokenUri + "/introspect"
        userinfoUri        = openidUri + "/userinfo"
        redirectUri        = "http://" + args.ga4ghIP + ":" + args.ga4ghPort + "/oidc_callback"

        # generate the json data
        keycloakSecret = { "web": { "auth_uri" : authUri, "issuer" : issuer, "client_id" : args.ga4ghID, "client_secret" : args.ga4ghSecret, \
        "redirect_uris" : [ redirectUri ], "token_uri" : tokenUri, "token_introspection_uri" : tokenIntrospectUri, "userinfo_endpoint" : userinfoUri } }

        jsonData = json.dumps(keycloakSecret, indent=1)

        # Rewrite the client_secrets.json file with the new configuration
        fileHandle = open(clientSecretFile, "w")
        fileHandle.write(jsonData)
        fileHandle.close()

        # copy to the reference directory
        copyFile = ga4ghSourceDir + "/ga4gh/server/frontend/config/client_secrets.json"
        shutil.copy(clientSecretFile, copyFile)


    def initSrc(self, args):
        """
        Initializes the local ga4gh source code repository on the host machine

        This function is used if there is no pre-existing ga4gh source to use
        This code is later used to build the server on the docker container 

        Parameters:

        string ga4ghDir - The absolute path of the deployer's GA4GH deployment folder
        argsObject args - An object containing the command-line arguments as attributes

        Returns: None
        """
        ga4ghSrc = '/'.join(('.', 'ga4gh-server'))
        srcPath = pkg_resources.resource_filename(self.pkgName, ga4ghSrc)
        duplicateDir = pkg_resources.resource_exists(self.pkgName, ga4ghSrc)
        # os.path.exists(ga4ghSourceDir)  

        # halt if a duplicate directory exists and no override command has been given
        if (not duplicateDir) or args.override:
            # remove the existing source code if a duplicate directory exists
            # and the override command has been given
            if args.override and duplicateDir:
               shutil.rmtree(srcPath)

            subprocess.call(["git", "clone", "--branch", "auth-deploy-fixes", "https://github.com/Bio-Core/ga4gh-server.git", srcPath])

            # copy over the dataPrep file into the GA4GH source code prior to installation
            # the dataPrep file is the current means of offering different deployment
            # options for test data
            fileDict = { "/config/dataPrep.py" : "/dataPrep.py" } 

            for ifile in fileDict:
                ga4ghDir = pkg_resources.resource_filename(self.pkgName, self.ga4ghPath)
                shutil.copyfile(ga4ghDir + ifile, srcPath + fileDict[ifile])

            self.config(srcPath, args)
        elif (not args.noConfig):
            # reconfigure the client_secrets.json only
            clientSecretFile = srcPath + '/ga4gh/server/frontend/config/client_secrets.json'
            os.remove(clientSecretFile)
            self.config(srcPath, args)
        else:
            print("Using existing source directory and configuration " + srcPath)
            print("Command line configuration options for GA4GH will not be used")


