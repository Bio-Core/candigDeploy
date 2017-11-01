#!/usr/bin/python

import subprocess
import argparse
import sys
import shutil
import os
import json
import time

# this program deploys the keycloak and ga4gh server in docker containers
# the deployment procedure can be configured using command line arguments


class deployer:

    # constructor
    def __init__(self):
        self.commandParser()

    def commandParser(self):
        # initialize the command line arguments

        parser = argparse.ArgumentParser(description="Deployment script for CanDIG which deploys the GA4GH and Keycloak servers", add_help=True)

        # defaults
        ga4ghSecret = "250e42b8-3f41-4d0f-9b6b-e32e09fccaf7"
        funnelSecret = "07998d29-17aa-4821-9b9e-9f5c398146c6"

        # having no data, additional data, or the default data are to be mutually exclusive
        dataGroup    = parser.add_mutually_exclusive_group()
        rewriteGroup = parser.add_mutually_exclusive_group() 
        deployGroup = parser.add_mutually_exclusive_group()

        commandList = [ ["-i",   "--ip",                      None,                     "ip",                    "store", "Set the ip address of both servers"],
                        ["-kip", "--keycloak-ip",             "127.0.0.1",              "keycloakIP",            "store", "Set the ip address of the keycloak server"],
                        ["-gip", "--ga4gh-ip",                "127.0.0.1",              "ga4ghIP",               "store", "Set the ip address of the ga4gh server"],
                        ["-kp",  "--keycloak-port",           "8080",                   "keycloakPort",          "store", "Set the port number of the keycloak server"], 
                        ["-gp",  "--ga4gh-port",              "8000",                   "ga4ghPort",             "store", "Set the port number of the ga4gh server"],
                        ["-r",   "--realm-name",              "CanDIG",                 "realmName",             "store", "Set the keycloak realm name"],
                        ["-gid", "--ga4gh-id",                "ga4gh",                  "ga4ghID",               "store", "Set the ga4gh server client id"],
                        ["-kcn", "--keycloak-container-name", "keycloak_candig_server", "keycloakContainerName", "store", "Set the keycloak container name"],
                        ["-gcn", "--ga4gh-container-name",    "ga4gh_candig_server",    "ga4ghContainerName",    "store", "Set the ga4gh server container name"],
                        ["-kin", "--keycloak-image-name",     "keycloak_candig_server", "keycloakImageName",     "store", "Set the keycloak image tag"],
                        ["-gin", "--ga4gh-image-name",        "ga4gh_candig_server",    "ga4ghImageName",        "store", "Set the ga4gh image tag"],
                        ["-au",  "--admin-username",          "admin",                  "adminUsername",         "store", "Set the administrator account username"],
                        ["-uu",  "--user-username",           "user",                   "userUsername",          "store", "Set the user account username"],
                        ["-gsrc", "--ga4gh-src",              "ga4gh-server",           "ga4ghSrc",              "store", "Use an existing source directory"],
                        ["-gs",  "--ga4gh-secret",            ga4ghSecret,              "ga4ghSecret",           "store", "Client secret for the ga4gh server"],
                        ["-fin", "--funnel-image-name",       "funnel_candig_server",   "funnelImageName",       "store", "Set the funnel image tag"],
                        ["-fcn", "--funnel-container-name",   "funnel_candig_server",   "funnelContainerName",   "store", "Set the funnel container name"],
                        ["-fp",  "--funnel-port",             "3002",                   "funnelPort",            "store", "Set the funnel port number"],
                        ["-fip", "--funnel-ip",               "127.0.0.1",              "funnelIP",              "store", "Set the funnel ip address"],
                        ["-fid", "--funnel-id",               "funnel",                 "funnelID",              "store", "Set the funnel client id"],
                        ["-fs",  "--funnel-secret",           funnelSecret,             "funnelSecret",          "store", "Set the funnel client secret"],
                        ["-f",   "--funnel",                  False,                    "funnel",                "store_true", "Deploy the funnel server"],
                        ["-t",   "--token-tracer",            False,                    "tokenTracer",           "store_true", "Deploy and run the token tracer program"],
                        ["-ng",  "--no-ga4gh",                False,                    "noGa4gh",               "store_true", "Do not deploy the GA4GH server"],
                        ["-vip", "--vagrant-ip",              "192.168.12.123",         "vagrantIP",             "store",      "The IP on which the Vagrant container is accessible"]]

        for subList in commandList:
            parser.add_argument(subList[0], subList[1], default=subList[2], dest=subList[3], action=subList[4], help=subList[5])


        #parser.add_argument("-i",   "--ip",                                                                                      help="Set the ip address of both servers")
        #parser.add_argument("-kip", "--keycloak-ip",             default="127.0.0.1",              dest="keycloakIP",            help="Set the ip address of the keycloak server")
        #parser.add_argument("-gip", "--ga4gh-ip",                default="127.0.0.1",              dest="ga4ghIP",               help="Set the ip address of the ga4gh server")
        #parser.add_argument("-kp",  "--keycloak-port",           default="8080",                   dest="keycloakPort",          help="Set the port number of the keycloak server")
        #parser.add_argument("-gp",  "--ga4gh-port",              default="8000",                   dest="ga4ghPort",             help="Set the port number of the ga4gh server")
        #parser.add_argument("-r",   "--realm-name",              default="CanDIG",                 dest="realmName",             help="Set the keycloak realm name")
        #parser.add_argument("-gid", "--ga4gh-id",                default="ga4gh",                  dest="ga4ghID",               help="Set the ga4gh server client id")
        #parser.add_argument("-kcn", "--keycloak-container-name", default="keycloak_candig_server", dest="keycloakContainerName", help="Set the keycloak container name")
        #parser.add_argument("-gcn", "--ga4gh-container-name",    default="ga4gh_candig_server",    dest="ga4ghContainerName",    help="Set the ga4gh server container name")
        #parser.add_argument("-kin", "--keycloak-image-name",     default="keycloak_candig_server", dest="keycloakImageName",     help="Set the keycloak image tag")
        #parser.add_argument("-gin", "--ga4gh-image-name",        default="ga4gh_candig_server",    dest="ga4ghImageName",        help="Set the ga4gh image tag")
        #parser.add_argument("-au",  "--admin-username",          default="admin",                  dest="adminUsername",         help="Set the administrator account username")
        #parser.add_argument("-uu",  "--user-username",           default="user",                   dest="userUsername",          help="Set the user account username")
        #parser.add_argument("-gsrc", "--ga4gh-src",              default="ga4gh-server",           dest="ga4ghSrc",              help="Use an existing source directory")
        rewriteGroup.add_argument("-o",   "--override",                default=False,                     action="store_true",         help="Force the removal of an existing source code directory")
        #parser.add_argument("-t",   "--token-tracer",            default=False, dest="tokenTracer", action="store_true",         help="Deploy and run the token tracer program")
        dataGroup.add_argument("-ed",  "--extra-data",           default=False, dest="extraData",   action="store_true",         help="Add additional test data to the ga4gh server")
        dataGroup.add_argument("-nd",  "--no-data",              default=False, dest="noData",      action="store_true",         help="Deploy the ga4gh server with no data")
        #parser.add_argument("-f",   "--funnel",                  default=False,                     action="store_true",         help="Deploy the funnel server")
        parser.add_argument(        "deploy",                                                                                    help="Deploy the Keycloak and GA4GH server")
        deployGroup.add_argument("-s",   "--singularity",             default=False,                     action="store_true",         help="Deploy using singularity containers")
        #parser.add_argument("-gs",  "--ga4gh-secret",            default=ga4ghSecret,              dest="ga4ghSecret",          help="Client secret for the ga4gh server")
        #parser.add_argument("-fin", "--funnel-image-name",       default="funnel_candig_server",   dest="funnelImageName",       help="Set the funnel image tag")
        #parser.add_argument("-fcn", "--funnel-container-name",   default="funnel_candig_server",   dest="funnelContainerName",   help="Set the funnel container name")
        #parser.add_argument("-fp",  "--funnel-port",             default="3002",                   dest="funnelPort",            help="Set the funnel port number")
        #parser.add_argument("-fip", "--funnel-ip",               default="127.0.0.1",              dest="funnelIP",              help="Set the funnel ip address")
        #parser.add_argument("-fid", "--funnel-id",               default="funnel",                 dest="funnelID",              help="Set the funnel client id")
        #parser.add_argument("-fs",  "--funnel-secret",           default=funnelSecret,             dest="funnelSecret",              help="Set the funnel client secret")
        #parser.add_argument("-ng", "--no-ga4gh",                 default=False,                    dest="noGa4gh", action="store_true",      help="Do not deploy the GA4GH server")
        deployGroup.add_argument("-v", "--vagrant",                   default=False,                    dest="vagrant", action="store_true",      help="Deploy the deployer onto a Vagrant container that will then use Singularity containers (for testing)")
        #parser.add_argument("-vip", "--vagrant-ip",              default="192.168.12.123",         dest="vagrantIP", help="The IP on which the Vagrant container is accessible")
        rewriteGroup.add_argument("-rc", "--reconfig", default=False, dest="reconfig", action="store_true", help="Reconfigure the client_secrets for the GA4GH server only")
        #parser.add_argument(      "token-tracer", default=False, dest=tokenTracerInvoke, action="store_true", help="Invoke the token tracer")
        #parser.add_argument("-nk",  "--no-keycloak", default=False, dest=noKeycloak, action="store_true", help="Do not deploy Keycloak")
        #parser.add_argument("-ck", "--config-keycloak", default=False, dest=configKeycloak, action="store_true", help="Reconfigure keycloak only - do not reinstall")
        #parser.add_argument("-oc",  "--config-override", default=False, dest="configOverride", action="store_true", help="Overwrite the client secrets file for an existing repository")
        #parser.add_argument("--adminPassword", help="Set the administrator account password")
        #parser.add_argument("--userPassword", help="Set the user account password")
        #parser.add_argument("-c", "--configOnly", help="Reconfigure the existing containers without destroying them", action="store_true")
        #parser.add_argument("-b", "--boot", help="Start the existing containers in their current unmodified state", action="store_true")

        adminPassword = "admin" # keycloak master realm admin account password
        userPassword  = "user"  # password for the account on which to log into ga4gh server via keycloak
        initRepo      = True    # flag as to whether to clone in a clean repository from the authentication branch of candig ga4gh server

        dataArg = "default"
        keycloakDir = "./keycloak"
        ga4ghDir = "./ga4gh"
        vagrantDir = "./vagrant"
        funnelDir="./funnel"
        vagrantImgDir = "/home/vagrant"

        # parse for command line arguments
        args = parser.parse_args()

        # override the other ip address if ip specified
        if args.ip:
            args.keycloakIP = args.ga4ghIP = args.funnelIP = args.ip
            #args.ga4ghIP = args.ip
            #args.funnelIP = args.ip

        #if args.vagrant:
        #    args.keycloakIP = "192.168.12.123"
        #    args.ga4ghIP = "192.168.12.123"

        if args.noData:
            dataArg = "none"
        elif args.extraData:
            dataArg = "extra"

        # initiate the deployment procedure if deploy has been specified
        if args.deploy:
            self.deploymentRouter(args, vagrantDir, keycloakDir, vagrantImgDir, ga4ghDir, dataArg, funnelDir)
            self.printDeploy(args, userPassword, adminPassword)

        exit()


    def deploymentRouter(self, args, vagrantDir, keycloakDir, vagrantImgDir, ga4ghDir, dataArg, funnelDir):
        # remove duplicate containers
        self.containerTeardown(args.keycloakContainerName, args.ga4ghContainerName, vagrantDir, args.funnelContainerName)
        # configure the keycloak server
        self.keycloakConfig(args, keycloakDir)

        # choose between docker and singularity keycloak deployment
        if ((not args.vagrant) and (not args.singularity)):
            self.keycloakDeploy(args.keycloakImageName, args.keycloakContainerName, keycloakDir, args.keycloakPort, args.tokenTracer)
        elif args.singularity:
            self.singularityKeycloakDeploy(vagrantImgDir)

        # initialize the repository containing the ga4gh source code locally if unspecified
        if args.ga4ghSrc == "ga4gh-server":   
            self.initSrc(ga4ghDir, args)

        # choose between vagrant deployment or singularity or docker deployment of ga4gh server 
        if args.vagrant:        
            self.vagrantDeploy(vagrantDir, args.vagrantIP)
        elif args.singularity:
            self.singularityGa4ghDeploy(vagrantImgDir)
        elif (not args.noGa4gh):
            self.ga4ghDeploy(args.ga4ghImageName, args.ga4ghContainerName, ga4ghDir, args.ga4ghPort,\
                        args.ga4ghSrc, dataArg)

        # deploy funnel if selected
        if args.funnel:
            self.funnelConfig(args, funnelDir)
            self.funnelDeploy(args.funnelImageName, args.funnelContainerName, args.funnelPort, funnelDir)




    # remove up any duplicate containers currently running or stopped that may conflict with deployment
    def containerTeardown(self, keycloakContainerName, ga4ghContainerName, vagrantDir, funnelContainerName):
        try:
            subprocess.call(["docker", "container", "kill", keycloakContainerName, ga4ghContainerName, funnelContainerName])
            subprocess.call(["docker", "container", "rm", keycloakContainerName, ga4ghContainerName, funnelContainerName])
            subprocess.call(["vagrant", "destroy", "-f", "default"], cwd=vagrantDir)
        except OSError:
            pass


    # deploys the keycloak server
    # builds the keyserver docker image and runs it
    def keycloakDeploy(self, keycloakImageName, keycloakContainerName, keycloakDir, keycloakPort, tokenTracer):
        tokenArg = "tokenTracer=" + str(tokenTracer)
        buildKeycloakCode = subprocess.call(["docker", "build", "-t", keycloakImageName, "--build-arg", tokenArg, keycloakDir])
        # check if docker is working
        # abort if docker fails or is inaccessible
        if buildKeycloakCode != 0:
            print("ERROR: Docker build has failed to build image.")
            exit(1)
        # we need to capture port errors!
        # without interrupting the server
        # run the keycloak server as a background process
        if tokenTracer:
            subprocess.Popen(["docker", "run", "--cap-add", "net_raw", "--cap-add", "net_admin", "-p", keycloakPort + ":8080", "--name", keycloakContainerName, keycloakImageName])
        else:
            subprocess.Popen(["docker", "run", "-p", keycloakPort + ":8080", "--name", keycloakContainerName, keycloakImageName])


    # deploys the ga4gh server
    # builds the ga4gh server docker image and runs it
    def ga4ghDeploy(self, ga4ghImageName, ga4ghContainerName, ga4ghDir, ga4ghPort, ga4ghSrc, dataArg):
        # build the ga4gh server
        srcArg = "sourceDir=" + ga4ghSrc
        dataArg = "dataArg=" + dataArg
        subprocess.call(["docker",  "build", "-t", ga4ghImageName, "--build-arg", srcArg, "--build-arg", dataArg, ga4ghDir])
        # run the ga4gh server
        subprocess.Popen(["docker", "run", "-p", ga4ghPort + ":80", "--name", ga4ghContainerName, ga4ghImageName])


    # deploy ga4gh via singularity through a vagrant container
    # we should also have an option that deploys them directly via singularity
    # this would require us to test it in a linux environment
    def vagrantDeploy(self, vagrantDir, vagrantIP):
        os.environ["VAGRANT_IP"] = vagrantIP
        subprocess.call(["vagrant", "up"], cwd=vagrantDir) 

    def singularityKeycloakDeploy(self, imgDir):
        keycloakImg = imgDir + "/keycloak.img"
        subprocess.call(["sudo", "singularity", "build", "--writable", keycloakImg, "keycloak/keycloakSingularity"])
        subprocess.Popen(["sudo", "singularity", "run", keycloakImg])

    def singularityGa4ghDeploy(self, imgDir):
        ga4ghImg = imgDir + "/ga4gh-server.img"
        subprocess.call(["sudo", "singularity", "build", "--writable", ga4ghImg, "ga4gh/Singularity"])
        subprocess.Popen(["sudo", "singularity", "run", ga4ghImg])

    # deploy the funnel server
    def funnelDeploy(self, funnelImageName, funnelContainerName, funnelPort, funnelDir):
        subprocess.call(["docker", "build", "-t", funnelImageName, funnelDir])
        subprocess.Popen(["docker", "run", "-v", "/var/run/docker.sock:/var/run/docker.sock", "-p", funnelPort + ":3002", "--name", funnelContainerName, funnelImageName])


    # prints the login information post-deployment
    def printDeploy(self, args, userPassword, adminPassword):
        print("\nDeployment Complete.\n")
        print("Keycloak is accessible at:")
        print("IMAGE:     " + args.keycloakImageName) 
        print("CONTAINER: " + args.keycloakContainerName)
        print("IP:PORT:   " + args.keycloakIP + ":" + args.keycloakPort)
        print("\nGA4GH Server is accessible at:")
        print("IMAGE:     " + args.ga4ghImageName)
        print("CONTAINER: " + args.ga4ghContainerName)
        print("IP:PORT:   " + args.ga4ghIP + ":" + args.ga4ghPort)
        print("\nUser Account:")
        print("USERNAME:  " + args.userUsername)
        print("PASSWORD:  " + userPassword)
        print("\nAdmin Account:")
        print("USERNAME:  " + args.adminUsername)
        print("PASSWORD:  " + adminPassword + "\n")
        if args.funnel:
            print("\nFunnel is accessible at:")
            print("IMAGE:     " + args.funnelImageName)
            print("CONTAINER: " + args.funnelContainerName)
            print("IP:PORT:   " + args.funnelIP + ":" + args.funnelPort)     

    # writes the keycloak.json configuration file
    # the configuration file determines the realms, clients, 
    # and users that exist on the server and their settings
    def keycloakConfig(self, args, keycloakDir):
        keycloakConfigFile = keycloakDir + "/keycloakConfig.json"
        with open(keycloakConfigFile, "r") as configFile:
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

        with open(keycloakConfigFile, "w") as configFile:
            json.dump(configData, configFile, indent=1)

    # writes the keycloak.json file for the funnel client
    def funnelConfig(self, args, funnelDir):
        fileName = funnelDir + "/funnel-node/node-client/keycloak.json"

        authUrl = "http://" + args.keycloakIP + ":" + args.keycloakPort + "/auth"
        redirectList = [ "http://" + args.funnelIP + ":" + args.funnelPort + "/oidc_callback" ]
        secretDict = { "secret" : args.funnelSecret } 

        keycloakData = { "realm" : args.realmName, "auth-server-url": authUrl, "resource" : args.funnelID, "redirect_uris" : redirectList, "credentials" : secretDict }

        jsonData = json.dumps(keycloakData)

        fileHandle = open(fileName, "w")
        fileHandle.write(jsonData)
        fileHandle.close()    

    # writes the new client_secrets.json file 
    # for registration of ga4gh client with keycloak CanDIG realm
    def ga4ghConfig(self, ga4ghSourceDir, args):
        fileName           = ga4ghSourceDir + "/client_secrets.json"
        keycloakRootUrl    = "http://" + args.keycloakIP + ":" + args.keycloakPort + "/auth"
        issuer             = keycloakRootUrl + "/realms/" + args.realmName
        openidUri          =  issuer + "/protocol/openid-connect"
        authUri            = openidUri + "/auth"
        tokenUri           =  openidUri + "/token"
        tokenIntrospectUri = tokenUri + "/introspect"
        userinfoUri        = openidUri + "/userinfo"
        redirectUri        = "http://" + args.ga4ghIP + ":" + args.ga4ghPort + "/oidc_callback"
        #uriList = [ redirectUri ]
        # generate the json data
        keycloakSecret = { "web": { "auth_uri" : authUri, "issuer" : issuer, "client_id" : args.ga4ghID, "client_secret" : args.ga4ghSecret, "redirect_uris" : [ redirectUri ], "token_uri" : tokenUri, "token_introspection_uri" : tokenIntrospectUri, "userinfo_endpoint" : userinfoUri } }

        jsonData = json.dumps(keycloakSecret)

        # Rewrite the client_secrets.json file with the new configuration
        fileHandle = open(fileName, "w")
        fileHandle.write(jsonData)
        fileHandle.close()


    # initializes the local ga4gh source code repository on the host machine
    # this function is used if there is no pre-existing ga4gh source to use
    # this code is later used to build the server on the docker container 
    def initSrc(self, ga4ghDir, args):
        ga4ghSourceDir = ga4ghDir + "/ga4gh-server"
        duplicateDir = os.path.exists(ga4ghSourceDir)  

        # halt if a duplicate directory exists and no override command has been given
        if (not duplicateDir) or args.override:
            # remove the existing source code if a duplicate directory exists
            # and the override command has been given
            if args.override and duplicateDir:
               shutil.rmtree(ga4ghSourceDir)

            subprocess.call(["git", "clone", "--branch", "authentication", "https://github.com/CanDIG/ga4gh-server.git", ga4ghSourceDir])

            fileDict = { "/requirements.txt" : "/requirements.txt", "/frontend.py" : "/ga4gh/server/frontend.py", "/serverconfig.py" : "/ga4gh/server/serverconfig.py", "/dataPrep.py" : "/dataPrep.py" } 
            for file in fileDict:
                shutil.copyfile(ga4ghDir + file, ga4ghSourceDir + fileDict[file])

            #shutil.copyfile(ga4ghDir + "/requirements.txt", ga4ghSourceDir + "/requirements.txt")
            #shutil.copyfile(ga4ghDir + "/frontend.py", ga4ghSourceDir + "/ga4gh/server/frontend.py")
            #shutil.copyfile(ga4ghDir + "/serverconfig.py", ga4ghSourceDir + "/ga4gh/server/serverconfig.py")
            #shutil.copyfile(ga4ghDir + "/dataPrep.py", ga4ghSourceDir + "/dataPrep.py")

            self.ga4ghConfig(ga4ghSourceDir, args)

        # reconfigure the client_secrets.json only
        elif args.reconfig:
             clientSecretFile = ga4ghSourceDir + '/client_secrets.json'
             os.remove(clientSecretFile)
             self.ga4ghConfig(ga4ghSourceDir, args)
        else:
            print("Using existing source directory and configuration " + ga4ghSourceDir)
            print("Command line configuration options for GA4GH will not be used")


deployer()
