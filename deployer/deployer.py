#!/usr/bin/python

import subprocess
import argparse
import sys
import shutil
import os
import json
import time
import pkg_resources

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
        self.ga4ghSecret = "250e42b8-3f41-4d0f-9b6b-e32e09fccaf7"
        self.funnelSecret = "07998d29-17aa-4821-9b9e-9f5c398146c6"

        dataArg = "default"

        self.pkgName = __name__

        self.keycloakPath = '/'.join(('.', 'keycloak'))
        self.ga4ghPath = '/'.join(('.', 'ga4gh'))
        self.vagrantPath = '/'.join(('.', 'vagrant'))
        self.funnelPath = '/'.join(('.', 'funnel'))

        # get the comamnd line arguments
        args = self.commandParser(sys.argv[1:])

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
        if args.deploy:
            self.deploymentRouter(args, dataArg)
            self.printDeploy(args)

        exit()

    def commandParser(self, commandArgs):
        """
        Parsers for and returns the values of command line arguments

        Creates the command line argument parser which parsers for arguments passed through
        the command line interface

        Parameters:

        commandArgs

        Returns: 

        argsObject - An object whose attribute names correspond to the argument fields
                     and whose values are the values supplied to the arguments (or default otherwise)
        """

        # initialize the command line arguments
        descLine = "Deployment script for CanDIG which deploys the GA4GH and Keycloak servers"
        parser = argparse.ArgumentParser(description=descLine, add_help=True)


        # having no data, additional data, or the default data are to be mutually exclusive
        dataGroup    = parser.add_mutually_exclusive_group()
        rewriteGroup = parser.add_mutually_exclusive_group() 
        deployGroup = parser.add_mutually_exclusive_group()

        localhost = "127.0.0.1"
        keycloakName = "keycloak_candig_server"
        ga4ghName =  "ga4gh_candig_server"
        funnelName = "funnel_candig_server"

        commandList = [ ["-i",   "--ip",                      
                         None,           "ip",                    
                         "store", "Set the ip address of both servers"],
                        ["-kip", "--keycloak-ip",             
                         localhost,      "keycloakIP",            
                         "store", "Set the ip address of the keycloak server"],
                        ["-gip", "--ga4gh-ip",                
                         localhost,      "ga4ghIP",               
                         "store", "Set the ip address of the ga4gh server"],
                        ["-kp",  "--keycloak-port",           
                         "8080",         "keycloakPort",          
                         "store", "Set the port number of the keycloak server"], 
                        ["-gp",  "--ga4gh-port",              
                         "8000",         "ga4ghPort",             
                         "store", "Set the port number of the ga4gh server"],
                        ["-r",   "--realm-name",              
                         "CanDIG",       "realmName",             
                         "store", "Set the keycloak realm name"],
                        ["-gid", "--ga4gh-id",                
                         "ga4gh",        "ga4ghID",               
                         "store", "Set the ga4gh server client id"],
                        ["-kcn", "--keycloak-container-name", 
                         keycloakName,   "keycloakContainerName", 
                         "store", "Set the keycloak container name"],
                        ["-gcn", "--ga4gh-container-name",    
                         ga4ghName,      "ga4ghContainerName",    
                         "store", "Set the ga4gh server container name"],
                        ["-kin", "--keycloak-image-name",     
                         keycloakName,   "keycloakImageName",     
                         "store", "Set the keycloak image tag"],
                        ["-gin", "--ga4gh-image-name",        
                         ga4ghName,      "ga4ghImageName",        
                         "store", "Set the ga4gh image tag"],
                        ["-au",  "--admin-username",          
                         "admin",        "adminUsername",         
                         "store", "Set the administrator account username"],
                        ["-uu",  "--user-username",           
                         "user",         "userUsername",          
                         "store", "Set the user account username"],
                        ["-gsrc", "--ga4gh-src",              
                         "ga4gh-server", "ga4ghSrc",              
                         "store", "Use an existing source directory"],
                        ["-gs",  "--ga4gh-secret",            
                         self.ga4ghSecret,    "ga4ghSecret",           
                         "store", "Client secret for the ga4gh server"],
                        ["-fin", "--funnel-image-name",       
                         funnelName,     "funnelImageName",       
                         "store", "Set the funnel image tag"],
                        ["-fcn", "--funnel-container-name",   
                         funnelName,     "funnelContainerName",   
                         "store", "Set the funnel container name"],
                        ["-fp",  "--funnel-port",             
                         "3002",         "funnelPort",            
                         "store", "Set the funnel port number"],
                        ["-fip", "--funnel-ip",               
                         localhost,      "funnelIP",              
                         "store", "Set the funnel ip address"],
                        ["-fid", "--funnel-id",               
                         "funnel",       "funnelID",              
                         "store", "Set the funnel client id"],
                        ["-fs",  "--funnel-secret",           
                         self.funnelSecret,   "funnelSecret",          
                         "store", "Set the funnel client secret"],
                        ["-f",   "--funnel",                  
                         False,          "funnel",                
                         "store_true", "Deploy the funnel server"],
                        ["-t",   "--token-tracer",            
                         False,           "tokenTracer",          
                         "store_true", "Deploy and run the token tracer program"],
                        ["-ng",  "--no-ga4gh",                
                         False,           "noGa4gh",              
                         "store_true", "Do not deploy the GA4GH server"],
                        ["-vip", "--vagrant-ip",              
                         localhost,       "vagrantIP",            
                         "store",      "The IP on which the Vagrant container is accessible"],
                        ["-upwd", "--user-password",          
                         "user",          "userPassword",         
                         "store",      "Set the user account password"],
                        ["-apwd", "--admin-password",         
                         "admin",         "adminPassword",        
                         "store",      "Set the administrator password"]]

        for subList in commandList:
            parser.add_argument(subList[0], subList[1], default=subList[2], dest=subList[3], action=subList[4], help=subList[5])

        rewriteGroup.add_argument("-o",  "--override",    default=False,                   action="store_true", help="Force the removal of an existing source code directory")
        rewriteGroup.add_argument("-nc", "--no-config",    default=False, dest="noConfig", action="store_true", help="Surpress reconfiguration of the client_secrets for the GA4GH server")

        dataGroup.add_argument("-ed",    "--extra-data",  default=False, dest="extraData", action="store_true", help="Add additional test data to the ga4gh server")
        dataGroup.add_argument("-nd",    "--no-data",     default=False, dest="noData",    action="store_true", help="Deploy the ga4gh server with no data")

        deployGroup.add_argument("-s",   "--singularity", default=False,                  action="store_true", help="Deploy using singularity containers")
        deployGroup.add_argument("-v",   "--vagrant",     default=False, dest="vagrant",  action="store_true", help="Deploy the deployer onto a Vagrant container that will then use Singularity containers (for testing)")

        parser.add_argument("deploy",   help="Deploy the Keycloak and GA4GH server")        

        # parse for command line arguments
        args = parser.parse_args(commandArgs)

        return args




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

        The GA4GH deployment is overidden by the Vagrant deployment if enabled

        3. Funnel
           a. Docker

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
            self.singularityKeycloakDeploy(args.override)

        # initialize the repository containing the ga4gh source code locally if unspecified
        if args.ga4ghSrc == "ga4gh-server":   
            self.initSrc(args)

        # choose between vagrant deployment or singularity or docker deployment of ga4gh server 
        if args.vagrant:        
            self.vagrantDeploy(args)
        elif args.singularity:
            self.singularityGa4ghDeploy(args.override)
        elif (not args.noGa4gh):
            self.ga4ghDeploy(args.ga4ghImageName, args.ga4ghContainerName, args.ga4ghPort,\
                        args.ga4ghSrc, dataArg)

        # deploy funnel if selected
        if args.funnel:
            self.funnelConfig(args)
            self.funnelDeploy(args.funnelImageName, args.funnelContainerName, args.funnelPort)



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


    def vagrantDeploy(self, args):
        """
        Deploy ga4gh via singularity through a vagrant container

        We should also have an option that deploys them directly via singularity
        This would require us to test it in a linux environment

        Parameters:

        string vagrantDir
        argsObject args

        Returns: None
        """

        os.environ["VAGRANT_IP"] = args.vagrantIP
        os.environ["KEYCLOAK_PORT"] = args.keycloakPort
        os.environ["GA4GH_PORT"] = args.ga4ghPort

        vagrantDir = pkg_resources.resource_filename(self.pkgName, self.vagrantPath)
        subprocess.call(["vagrant", "up"], cwd=vagrantDir) 



    def singularityKeycloakDeploy(self, override):
        """
        Deploy keycloak server via a singularity container

        Parameters:

        string imgDir

        Returns: None
        """        
        if override:
           os.remove("keycloak.simg")
        #keycloakImg = imgDir + "/keycloak.img"
        #subprocess.call(["sudo", "singularity", "build", "--writable", keycloakImg, "keycloak/keycloakSingularity"])
        subprocess.call(["singularity", "pull", "--name", "keycloak.img", "shub://DaleDupont/singularity-keycloak:latest"])
        subprocess.Popen(["singularity", "run", "keycloak.simg"])



    def singularityGa4ghDeploy(self, override):
        """
        Deploy ga4gh server via a singularity container

        This deployment scheme does not require root access

        Parameters:

        string imgDir - The path containing the 

        Returns: None
        """
        if override:
            os.remove("ga4gh.simg")
        #ga4ghImg = imgDir + "/ga4gh-server.img"
        #subprocess.call(["sudo", "singularity", "build", "--writable", ga4ghImg, "ga4gh/Singularity"])
        subprocess.call(["singularity", "pull", "--name", "ga4gh.img", "shub://DaleDupont/singularity-ga4gh:latest"])
        subprocess.Popen(["singularity", "run", "ga4gh.simg"])


    def funnelDeploy(self, funnelImageName, funnelContainerName, funnelPort):
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



    def funnelConfig(self, args):
        """
        Writes the keycloak.json file for the funnel client

        Parameters:

        argsObject args - An object containing the command-line arguments as attributes
        string funnelDir - The absolute path of the deployer's funnel files directory

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


    def ga4ghConfig(self, ga4ghSourceDir, args):
        """ 
        Writes the new client_secrets.json file 

        For registration of ga4gh client with keycloak CanDIG realm

        Parameters:

        string ga4ghSourceDir - The path of the directory containing the GA4GH source code
        argsObject args - An object containing the command-line arguments as attributes

        Returns: None
        """

        fileName           = ga4ghSourceDir + "/client_secrets.json"
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
        fileHandle = open(fileName, "w")
        fileHandle.write(jsonData)
        fileHandle.close()


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

            subprocess.call(["git", "clone", "--branch", "authentication", "https://github.com/CanDIG/ga4gh-server.git", srcPath])

            fileDict = { "/config/requirements.txt" : "/requirements.txt",             "/config/frontend.py" : "/ga4gh/server/frontend.py", \
                         "/config/serverconfig.py"  : "/ga4gh/server/serverconfig.py", "/config/dataPrep.py" : "/dataPrep.py", \
                         "/config/application.wsgi" : "/deploy/application.wsgi",      "/config/config.py"   : "/deploy/config.py", \
                         "/config/001-ga4gh.conf"   : "/deploy/001-ga4gh.conf",        "/config/ports.conf"  : "/deploy/ports.conf"} 
            for ifile in fileDict:
                ga4ghDir = pkg_resources.resource_filename(self.pkgName, self.ga4ghPath)
                shutil.copyfile(ga4ghDir + ifile, srcPath + fileDict[ifile])

            self.ga4ghConfig(sourcePath, args)

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
