#!/usr/bin/python

import subprocess
import sys
import shutil
import os
import pkg_resources
import json
import yaml

import cmdparse as cmdparse
import funnel.funnel as funnel
import vagrant.vagrant as vagrant

# this program deploys the keycloak and ga4gh server in docker containers
# the deployment procedure can be configured using command line arguments

class deployer:

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

        # defaults

        dataArg = "default"

        self.pkgName = __name__

        self.keycloakPath = '/'.join(('.', 'keycloak'))
        self.ga4ghPath = '/'.join(('.', 'ga4gh'))
        self.vagrantPath = '/'.join(('.', 'vagrant'))

        # get the comamnd line arguments
        self.cmdparse = cmdparse.cmdparse()

        args = self.cmdparse.commandParser(sys.argv[1:])

        if args.vagrant:
            args.keycloakIP = args.ga4ghIP = args.vagrantIP

        # override the other ip address if ip specified
        if args.ip:
            args.keycloakIP = args.ga4ghIP = args.funnelIP = args.ip

        # set the dataArg based on whether more or no data
        # for the ga4gh server was requested
        if args.noData:
            dataArg = "none"
        elif args.extraData:
            dataArg = "extra"

        # initiate the deployment procedure if deploy has been specified

        self.deploymentRouter(args, dataArg)
        self.printDeploy(args)

        exit()


    def deploymentRouter(self, args, dataArg):
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
        # configure the keycloak server
        self.keycloakConfig(args)

        # choose between docker and singularity keycloak deployment
        if ((not args.vagrant) and (not args.singularity)):
            self.keycloakDeploy(args)
        elif args.singularity:
            self.singularityKeycloakDeploy(args)

        # initialize the repository containing the ga4gh source code locally if unspecified
        if args.ga4ghSrc == "ga4gh-server":   
            self.initSrc(args)

        # choose between vagrant deployment or singularity or docker deployment of ga4gh server 
        if args.vagrant:
            self.vagrant = vagrant.vagrant()        
            self.vagrant.vagrantDeploy(args)
        elif args.singularity:
            self.singularityGa4ghDeploy(args)
        elif (not args.noGa4gh):
            self.ga4ghDeploy(args.ga4ghImageName, args.ga4ghContainerName, args.ga4ghPort,\
                        args.ga4ghSrc, dataArg)

        # deploy funnel if selected
        if args.funnel:
            self.funnel = funnel.funnel()
            self.funnel.funnelConfig(args)
            self.funnel.funnelDeploy(args.funnelImageName, args.funnelContainerName, args.funnelPort)



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
        vagrantDir = pkg_resources.resource_filename(self.pkgName, self.vagrantPath)

        try:
            subprocess.call(["docker", "container", "kill", keycloakContainerName, ga4ghContainerName, funnelContainerName])
            subprocess.call(["docker", "container", "rm", keycloakContainerName, ga4ghContainerName, funnelContainerName])
            subprocess.call(["vagrant", "destroy", "-f", "default"], cwd=vagrantDir)
        except OSError:
            return


    def keycloakDeploy(self, args):
        """
        Deploys the keycloak server

        Builds the keyserver docker image and runs it

        Parameters:

        string keycloakDir - The path of the directory which contains the Keycloak server images
        argsObject args - The object containing the command line arguments as attributes

        Returns: None
        """

        tokenArg = "tokenTracer=" + str(args.tokenTracer)
        realmArg = "realmName=" + args.realmName
        adminNameArg = "adminUsername=" + args.adminUsername
        adminPwdArg = "adminPassword=" + args.adminPassword
        userNameArg = "userUsername=" + args.userUsername
        userPwdArg = "userPassword=" + args.userPassword
  
        keycloakDir = pkg_resources.resource_filename(self.pkgName, self.keycloakPath)
        keyProc = ["docker", "build", "-t", args.keycloakImageName, "--build-arg", tokenArg, "--build-arg", realmArg, \
                   "--build-arg", adminNameArg, "--build-arg", adminPwdArg, "--build-arg", userNameArg, "--build-arg", \
                   userPwdArg, keycloakDir]
        buildKeycloakCode = subprocess.call(keyProc)
        # check if docker is working
        # abort if docker fails or is inaccessible
        if buildKeycloakCode != 0:
            print("ERROR: Docker build has failed to build image.")
            exit(1)

        # we need to capture port errors!
        # without interrupting the server
        # run the keycloak server as a background process
        if args.tokenTracer:
            # net_raw and net_admin are necesary to have the network privileges to packet capture
            subprocess.Popen(["docker", "run", "--cap-add", "net_raw", "--cap-add", "net_admin", "-p", \
                              args.keycloakPort + ":8080", "--name", args.keycloakContainerName, args.keycloakImageName])
        else:
            subprocess.Popen(["docker", "run", "-p", args.keycloakPort + ":8080", "--name", args.keycloakContainerName, args.keycloakImageName])


        

    def ga4ghDeploy(self, ga4ghImageName, ga4ghContainerName, ga4ghPort, ga4ghSrc, dataArg):
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




    def singularityKeycloakDeploy(self, args):
        """
        Deploy keycloak server via a singularity container

        Parameters:

        args

        Returns: None
        """        

        imgPath = '/'.join(('.', 'keycloak', 'key.img'))
        imgName = pkg_resources.resource_filename(self.pkgName, imgPath)

        duplicateImg = pkg_resources.resource_exists(self.pkgName, imgPath)

        if duplicateImg:
           os.remove(imgName)

        #keycloakImg = imgDir + "/keycloak.img"
        #subprocess.call(["singularity", "pull", "--name", "keycloak.img", "shub://DaleDupont/singularity-keycloak:latest"])

        keycloakDir = pkg_resources.resource_filename(self.pkgName, self.keycloakPath)

        subprocess.call(["wget", "https://github.com/DaleDupont/singularity-keycloak/releases/download/0.0.1/key.img.gz", "-P", keycloakDir])

        zipPath = '/'.join(('.', 'keycloak', 'key.img.gz'))
        zipName = pkg_resources.resource_filename(self.pkgName, zipPath)

        subprocess.call(["gunzip", zipName])

        keycloakConfigPath = '/'.join(('.', 'keycloak', 'keycloakConfig.json'))
        configPath = pkg_resources.resource_filename(self.pkgName, keycloakConfigPath)

        # set the environment variables to use
        # inside the container

        envList = [("SINGULARITYENV_PORT", args.keycloakPort), 
                   ("SINGULARITYENV_IPADDR", args.keycloakIP), 
                   ("SINGULARITYENV_CONFIGFILE", configPath), 
                   ("SINGULARITYENV_REALM_NAME", args.realmName), 
                   ("SINGULARITYENV_ADMIN_USERNAME", args.adminUsername), 
                   ("SINGULARITYENV_ADMIN_PASSWORD", args.adminPassword), 
                   ("SINGULARITYENV_USER_USERNAME", args.userUsername), 
                   ("SINGULARITYENV_USER_PASSWORD", args.userPassword)]

        for envVar in envList:
            os.environ[envVar[0]] = envVar[1]

        subprocess.Popen(["singularity", "run", "--writable", imgName])



    def ga4ghBaseConfig(self):
        """
        Sets the location of the client_secrets JSON file
        in the configuration
        """
        configPath = '/'.join(('.', 'ga4gh', 'config', 'oidc_auth_config.yml'))
        configFile = pkg_resources.resource_filename(self.pkgName, configPath)
        

        clientSecretPath = '/'.join(('.', 'ga4gh', 'config', 'client_secrets.json'))
        clientSecretFile = pkg_resources.resource_filename(self.pkgName, clientSecretPath)

        print(configFile)
        fileHandle = open(configFile)
        yamlData = yaml.load(fileHandle)   
        print(yamlData)
        print(yamlData['OIDC_CLIENT_SECRETS'])
        yamlData['OIDC_CLIENT_SECRETS'] = clientSecretFile
        fileHandle.close()
        fileHandle = open(configFile, "w")
        yaml.dump(yamlData, fileHandle)
        fileHandle.close()

    def singularityGa4ghDeploy(self, args):
        """
        Deploy ga4gh server via a singularity container

        This deployment scheme does not require root access

        Parameters:

        string imgDir - The path containing the 

        Returns: None
        """

        imgPath = '/'.join(('.', 'ga4gh', 'ga4gh.simg'))
        imgName = pkg_resources.resource_filename(self.pkgName, imgPath)
        duplicateImg = pkg_resources.resource_exists(self.pkgName, imgPath)

        if args.override:
            os.remove(imgName)

        subprocess.call(["singularity", "pull", "--name", imgName, "shub://DaleDupont/singularity-ga4gh:latest"])

        self.ga4ghBaseConfig()

        configPath = '/'.join(('.', 'ga4gh', 'config', 'oidc_auth_config.yml'))
        configFile = pkg_resources.resource_filename(self.pkgName, configPath)

        # set the environment variables to use
        # inside the singularity container

        envList = [("SINGULARITYENV_GA4GH_PORT", args.ga4ghPort), 
                   ("SINGULARITYENV_GA4GH_IP", args.ga4ghIP), 
                   ("SINGULARITYENV_GA4GH_CONFIG", configFile)]

        for envVar in envList:
            os.environ[envVar[0]] = envVar[1]

        subprocess.Popen(["singularity", "run", imgName])




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
        print("\nUser Account:")
        print("USERNAME:  " + args.userUsername)
        print("PASSWORD:  " + args.userPassword)
        print("\nAdmin Account:")
        print("USERNAME:  " + args.adminUsername)
        print("PASSWORD:  " + args.adminPassword + "\n")
        if args.funnel:
            print("\nFunnel is accessible at:")
            print("IMAGE:     " + args.funnelImageName)
            print("CONTAINER: " + args.funnelContainerName)
            print("IP:PORT:   " + args.funnelIP + ":" + args.funnelPort)     


    def keycloakConfig(self, args):
        """
        Writes the keycloak.json configuration file

        The configuration file determines the realms, clients, 
        and users that exist on the server and their settings

        Parameters:

        argsObject args - An object containing the command-line arguments as attributes
        string keycloakDir - The absolute path of the deployer's keycloak files directory

        Returns: None
        """        
        keycloakConfigPath = '/'.join(('.', 'keycloak', 'keycloakConfig.json'))
        #keycloakConfigFile = keycloakDir + "/keycloakConfig.json"
        configPath = pkg_resources.resource_filename(self.pkgName, keycloakConfigPath)

        #configFile = pkg_resources.resource_stream(self.pkgName, keycloakConfigPath)
        with open(configPath, 'r') as configFile:
            configData = json.load(configFile)

            ga4ghUrl = "http://" + args.ga4ghIP + ":" + args.ga4ghPort + "/*"
            funnelUrl = "http://" + args.funnelIP + ":" + args.funnelPort + "/*"

            configData[0]["realm"] = args.realmName

            configData[0]["clients"][3]["clientId"] = args.funnelID
            configData[0]["clients"][3]["secret"] = args.funnelSecret
            configData[0]["clients"][3]["baseUrl"] = funnelUrl
            configData[0]["clients"][3]["redirectUris"] = [ funnelUrl ]
            configData[0]["clients"][3]["adminUrl"] = funnelUrl

            configData[0]["clients"][4]["clientId"] = args.ga4ghID
            configData[0]["clients"][4]["adminUrl"] = ga4ghUrl
            configData[0]["clients"][4]["baseUrl"] =  ga4ghUrl
            configData[0]["clients"][4]["secret"] = args.ga4ghSecret
            configData[0]["clients"][4]["redirectUris"] = [ ga4ghUrl ]

            configData[0]["users"][0]["username"] = args.userUsername
            configData[1]["users"][0]["username"] = args.adminUsername

            configData[0]["clients"][0]["baseUrl"] = "/auth/realms/" + args.realmName + "/account"
            configData[0]["clients"][0]["redirectUris"] = [ "/auth/realms/" + args.realmName + "/account/*" ]

            configData[0]["clients"][6]["baseUrl"] = "/auth/admin/" + args.realmName + "/console/index.html"
            configData[0]["clients"][6]["redirectUris"]  = ["/auth/admin/" + args.realmName + "/console/*"]

        with open(configPath, "w") as configFile:
            json.dump(configData, configFile, indent=1)




    def ga4ghConfig(self, ga4ghSourceDir, args):
        """ 
        Writes the new client_secrets.json file 

        For registration of ga4gh client with keycloak CanDIG realm

        Parameters:

        string ga4ghSourceDir - The path of the directory containing the GA4GH source code
        argsObject args - An object containing the command-line arguments as attributes

        Returns: None
        """

        #configPath = '/'.join(('.', 'ga4gh', 'config' + 'oidc_auth_config.yml'))
        #configFile = pkg_resources.resource_filename(self.pkgName, clientSecretPath)

        clientSecretPath = '/'.join(('.', 'ga4gh', 'config', 'client_secrets.json'))
        clientSecretFile = pkg_resources.resource_filename(self.pkgName, clientSecretPath)

        #fileName           = ga4ghSourceDir + "/client_secrets.json"
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
        copyFile = ga4ghSourceDir + "/client_secrets.json"
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
        ga4ghSrc = '/'.join(('.', 'ga4gh', 'ga4gh-server'))
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

            self.ga4ghConfig(srcPath, args)

        # reconfigure the client_secrets.json only
        elif (not args.noConfig):
            clientSecretFile = srcPath + '/client_secrets.json'
            os.remove(clientSecretFile)
            self.ga4ghConfig(srcPath, args)
        else:
            print("Using existing source directory and configuration " + srcPath)
            print("Command line configuration options for GA4GH will not be used")


def main():
    deployer()

if __name__ == "__main__":
    main()
