
import subprocess
import pkg_resources
import os
import json
import gzip

class keycloak:

    def __init__(self):

        self.pkgName = __name__
        self.keycloakPath = '/'.join(('.'))

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
        keyProc = ["docker", "build", "-t", args.keycloakImageName, \
                   "--build-arg", tokenArg, "--build-arg", realmArg, \
                   "--build-arg", adminNameArg, "--build-arg", adminPwdArg, \
                   "--build-arg", userNameArg, "--build-arg", \
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




    def singularityKeycloakDeploy(self, args):
        """
        Deploy keycloak server via a singularity container

        Parameters:

        args

        Returns: None
        """        

        imgPath = '/'.join(('.', 'key.img'))
        imgName = pkg_resources.resource_filename(self.pkgName, imgPath)

        duplicateImg = pkg_resources.resource_exists(self.pkgName, imgPath)

        if duplicateImg:
           os.remove(imgName)

        zipPath = '/'.join(('.', 'key.img.gz'))
        zipName = pkg_resources.resource_filename(self.pkgName, zipPath)

        duplicateZipImg = pkg_resources.resource_exists(self.pkgName, zipPath)

        if duplicateZipImg:
           os.remove(zipName)

        keycloakDir = pkg_resources.resource_filename(self.pkgName, self.keycloakPath)

        gitUrl = "https://github.com/DaleDupont/singularity-keycloak/releases/download/0.0.1/key.img.gz"
        subprocess.call(["wget", gitUrl, "-P", keycloakDir])

        subprocess.call(["gunzip", zipName])

        keycloakConfigPath = '/'.join(('.', 'keycloakConfig.json'))
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
        keycloakConfigPath = '/'.join(('.', 'keycloakConfig.json'))
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

