#!/usr/bin/python

import subprocess
import argparse
import sys
import shutil
import os
import json


def containerTeardown(keycloakContainerName, ga4ghContainerName):
    # clean up any duplicate containers currently running or stopped
    subprocess.call(['docker', 'container', 'kill', keycloakContainerName, ga4ghContainerName])
    subprocess.call(['docker', 'container', 'rm', keycloakContainerName, ga4ghContainerName])


def keycloakDeploy(keycloakImageName, keycloakDirectory):
    buildKeycloakCode = subprocess.call(['docker', 'build', '-t', keycloakImageName, keycloakDirectory])

    # check if docker is working
    # abort if docker fails or is inaccessible
    if buildKeycloakCode != 0:
        exit(1)


    # we need to capture port errors!
    # without interrupting the server
    # run the keycloak server as a background process
    #runKeycloakCode = 
    subprocess.Popen(['docker', 'run', '-p', keycloakPort + ':8080', '--name', keycloakContainerName, keycloakImageName])
    #if runKeycloakCode != 0:
    #    exit(1)


def ga4ghDeploy(ga4ghImageName, ga4ghContainerName, ga4ghDirectory, ga4ghPort, ga4ghSrc):
    # build the ga4gh server
    srcArg = 'sourceDir=' + ga4ghSrc
    subprocess.call(['docker',  'build', '-t', ga4ghImageName, '--build-arg', srcArg, ga4ghDirectory])

    # run the ga4gh server
    subprocess.Popen(['docker', 'run', '-p', ga4ghPort + ':80', '--name', ga4ghContainerName, ga4ghImageName])


def printDeploy(keycloakImageName, keycloakContainerName, keycloakIP, keycloakPort, ga4ghImageName, ga4ghContainerName, ga4ghIP, ga4ghPort, userUsername, userPassword, adminUsername, adminPassword):
    # print the login information
    print("\nDeployment Complete.\n")
    print("Keycloak is accessible at:")
    print("IMAGE:     " + keycloakImageName) 
    print("CONTAINER: " + keycloakContainerName)
    print("IP:PORT:   " + keycloakIP + ':' + keycloakPort)
    print("\nGA4GH Server is accessible at:")
    print("IMAGE:     " + ga4ghImageName)
    print("CONTAINER: " + ga4ghContainerName)
    print("IP:PORT:   " + ga4ghIP + ':' + ga4ghPort)
    print("\nUser Account:")
    print("USERNAME:  " + userUsername)
    print("PASSWORD:  " + userPassword)
    print("\nAdmin Account:")
    print("USERNAME:  " + adminUsername)
    print("PASSWORD:  " + adminPassword + "\n")


def keycloakConfigWrite(realmName, ga4ghClientID, clientSecret, ga4ghIP, ga4ghPort, adminUsername, userUsername):
    keycloakConfigFile = './keycloakDocker/keycloakConfig.json'
    with open(keycloakConfigFile, 'r+') as configFile:
        configData = json.load(configFile)

        ga4ghUrl = 'http://' + ga4ghIP + ':' + ga4ghPort + '/*'

        configData[0]['realm'] = realmName
        #print(configData[0]['clients'][5]['redirectUris'])
        configData[0]['clients'][3]['clientId'] = ga4ghClientID
        configData[0]['clients'][3]["adminUrl"] = ga4ghUrl
        configData[0]['clients'][3]["baseUrl"] =  ga4ghUrl
        configData[0]['clients'][3]['secret'] = clientSecret
        configData[0]['clients'][3]["redirectUris"] = [ ga4ghUrl ]
        configData[0]['users'][0]['username'] = userUsername
        configData[1]['users'][0]['username'] = adminUsername
        configData[0]['clients'][0]["baseUrl"] = '/auth/realms/' + realmName + '/account'
        configData[0]['clients'][0]['redirectUris'] = [ '/auth/realms/' + realmName + '/account/*' ]
        configData[0]['clients'][5]['baseUrl'] = '/auth/admin/' + realmName + '/console/index.html'
        configData[0]['clients'][5]['redirectUris']  = ['/auth/admin/' + realmName + '/console/*']


        #configData['users'][n]['password']= "user"                                                                                                  
        #configFile.seek(0) # reset position to start

    os.remove(keycloakConfigFile)
    with open(keycloakConfigFile, 'w') as configFile:
        json.dump(configData, configFile, indent=1)


def initRepoFunc(ga4ghDirectory, ga4ghClientID, clientSecret, ga4ghIP, ga4ghPort, keycloakIP, keycloakPort):
    ga4ghSourceDirectory = ga4ghDirectory + '/ga4gh-server'
    duplicateDirectory = os.path.exists(ga4ghSourceDirectory)
    if not duplicateDirectory or force:
        if force and duplicateDirectory:
           shutil.rmtree(ga4ghSourceDirectory)
        subprocess.call(['git', 'clone', '--branch', 'authentication', 'https://github.com/CanDIG/ga4gh-server.git', ga4ghSourceDirectory])
        shutil.copyfile(ga4ghDirectory + '/frontend.py', ga4ghSourceDirectory + '/ga4gh/server/frontend.py')
        shutil.copyfile(ga4ghDirectory + '/serverconfig.py', ga4ghSourceDirectory + '/ga4gh/server/serverconfig.py')

        fileName = ga4ghSourceDirectory + '/client_secrets.json'

        keycloakRootUrl="http://" + keycloakIP + ":" + keycloakPort + "/auth"
        issuer = keycloakRootUrl + "/realms/" + realmName
        openidUri =  issuer + "/protocol/openid-connect"
        authUri = openidUri + "/auth"
        tokenUri =  openidUri + "/token"
        tokenIntrospectUri = tokenUri + "/introspect"
        userinfoUri = openidUri + "/userinfo"
        redirectUri="http://" + ga4ghIP + ":" + ga4ghPort + "/oidc_callback"
        uriList = [ redirectUri ]
        # generate the json data                                                                                                                                                        
        webDict = { "auth_uri" : authUri, "issuer" : issuer, "client_id" : ga4ghClientID, \
        "client_secret" : clientSecret, "redirect_uris" : uriList, \
        "token_uri" : tokenUri, "token_introspection_uri" : tokenIntrospectUri, \
        "userinfo_endpoint" : userinfoUri }

        keycloakSecret = { 'web' : webDict }

        jsonData = json.dumps(keycloakSecret)

        # Rewrite the client_secrets.json file with the new configuration                                                                                                                        
        fileHandle = open(fileName, 'w')
        fileHandle.write(jsonData)
        fileHandle.close()

parser = argparse.ArgumentParser(description='Deployment script for Candig which deploys the ga4gh and keycloak servers', add_help=True)

parser.add_argument('-i', '--ip', help='Set the ip address of both servers')
parser.add_argument('-kip', '--keycloakIP', help='Set the ip address of the keycloak server')
parser.add_argument('-gip', '--ga4ghIP', help='Set the ip address of the ga4gh server')
parser.add_argument('-kp', '--keycloakPort', help='Set the port number of the keycloak server')
parser.add_argument('-gp', '--ga4ghPort', help='Set the port number of the ga4gh server')
parser.add_argument('-r', '--realmName', help='Set the keycloak realm name')
parser.add_argument('-d', '--ga4ghClientID', help='Set the ga4gh server client id')
parser.add_argument('--keycloakContainerName', help='Set the keycloak container name')
parser.add_argument('--ga4ghContainerName', help='Set the ga4gh server container name')
parser.add_argument('--keycloakImageName', help='Set the keycloak image tag')
parser.add_argument('--ga4ghImageName', help='Set the ga4gh image tag')
parser.add_argument('-a', '--adminUsername', help='Set the administrator account username')
parser.add_argument('-n', '--userUsername', help='Set the user account username')
parser.add_argument('-s', '--src', help='Use an existing source directory')
parser.add_argument('-o', '--override', help="Force the removal of an existing source code directory", action='store_true')
parser.add_argument('deploy', help='Deploymen the Keycloak and GA4GH server')

#parser.add_argument('--adminPassword', help='Set the administrator account password')
#parser.add_argument('--userPassword', help='Set the user account password')
#parser.add_argument('-c', '--configOnly', help='Reconfigure the existing containers without destroying them', action='store_true')
#parser.add_argument('-b', '--boot', help='Start the existing containers in their current unmodified state', action='store_true')

args = parser.parse_args()

# default values:
keycloakIP            = "192.168.99.100"         # keycloak server IP address
ga4ghIP               = keycloakIP               # GA4GH server IP address
keycloakPort          = "8080"                   # keycloak server port number
ga4ghPort             = "8000"                   # ga4gh server port number
ga4ghClientID         = "ga4ghServer"            # ga4gh server client id name registered with keycloak 
realmName             = "CanDIG"                 # keycloak server realm on which ga4gh server is registered as a client
keycloakImageName     = "keycloak_candig_server" # keycloak server docker image tag
keycloakContainerName = keycloakImageName        # keycloak server docker container name
ga4ghImageName        = "ga4gh_candig_server"    # ga4gh server docker image tag
ga4ghContainerName    = ga4ghImageName           # ga4gh server docker container name
adminUsername         = "admin"                  # keycloak master realm admin account username
adminPassword         = "admin"                  # keycloak master realm admin account password
userUsername          = "user"                   # username for the account on which to log into ga4gh server via keycloak
userPassword          = "user"                   # password for the account on which to log into ga4gh server via keycloak
initRepo              = True                     # flag as to whether to clone in a clean repository from the authentication branch of candig ga4gh server
force                 = False                    # force the removal of an existing ga4gh-server code repository 
ga4ghSrc              = 'ga4gh-server'           # the default source code directory in which to pull code for the GA4GH server into a container; relative to ./ga4ghDocker
clientSecret          = '250e42b8-3f41-4d0f-9b6b-e32e09fccaf7' # the client secret to assign keycloak and ga4gh 
#boot = False
#configOnly = False 

keycloakDirectory = "./keycloakDocker"
ga4ghDirectory = "./ga4ghDocker"

if args.override:
   force = args.override

if args.ip:
    keycloakIP = args.ip
    ga4ghIP = args.ip
if args.keycloakIP:
    keycloakIP = args.keycloakIP
if args.ga4ghIP:
    ga4ghIP = args.ga4ghIP
if args.realmName:
    realmName = args.realmName
if args.ga4ghPort:
    ga4ghPort = args.ga4ghPort
if args.keycloakPort:
    keycloakPort = args.keycloakPort
if args.ga4ghClientID:
    ga4ghClientID = args.ga4ghClientID

if args.src:
   initRepo = False
   ga4ghSrc = args.src

if args.ga4ghImageName:
    ga4ghImageName = args.ga4ghImageName
if args.keycloakImageName:
    keycloakImageName = args.keycloakImageName
if args.keycloakContainerName:
    keycloakContainerName = args.keycloakContainerName
if args.ga4ghContainerName:
    ga4ghContainerName = args.ga4ghContainerName


if args.userUsername:
    userUsername = args.userUsername
if args.adminUsername:
    adminUsername = args.adminUsername

if args.deploy:
    containerTeardown(keycloakContainerName, ga4ghContainerName)

    keycloakConfigWrite(realmName, ga4ghClientID, clientSecret, ga4ghIP, ga4ghPort, adminUsername, userUsername)

    keycloakDeploy(keycloakImageName, keycloakDirectory)

 

    # initialize the repository containing the ga4gh source code locally if specified
    if initRepo:   
        initRepoFunc(ga4ghDirectory, ga4ghClientID, clientSecret, ga4ghIP, ga4ghPort, keycloakIP, keycloakPort) 

    ga4ghDeploy(ga4ghImageName, ga4ghContainerName, ga4ghDirectory, ga4ghPort, ga4ghSrc)

    printDeploy(keycloakImageName, keycloakContainerName, keycloakIP, keycloakPort, ga4ghImageName, ga4ghContainerName, ga4ghIP, ga4ghPort, userUsername, userPassword, adminUsername, adminPassword)

exit()
