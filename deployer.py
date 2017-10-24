#!/usr/bin/python

import subprocess
import argparse
import sys
import shutil
import os
import json

# this program deploys the keycloak and ga4gh server in docker containers
# the deployment procedure can be configured using command line arguments

# clean up any duplicate containers currently running or stopped
def containerTeardown(keycloakContainerName, ga4ghContainerName):
    subprocess.call(['docker', 'container', 'kill', keycloakContainerName, ga4ghContainerName])
    subprocess.call(['docker', 'container', 'rm', keycloakContainerName, ga4ghContainerName])

# deploys the keycloak server
# builds the keyserver docker image and runs it
def keycloakDeploy(keycloakImageName, keycloakContainerName, keycloakDirectory, keycloakPort):

    buildKeycloakCode = subprocess.call(['docker', 'build', '-t', keycloakImageName, keycloakDirectory])
    # check if docker is working
    # abort if docker fails or is inaccessible
    if buildKeycloakCode != 0:
        print("ERROR: Docker build has failed to build image.")
        exit(1)

    # we need to capture port errors!
    # without interrupting the server
    # run the keycloak server as a background process

    subprocess.Popen(['docker', 'run', '-p', keycloakPort + ':8080', '--name', keycloakContainerName, keycloakImageName])
    
# deploys the ga4gh server
# builds the ga4gh server docker image and runs it
def ga4ghDeploy(ga4ghImageName, ga4ghContainerName, ga4ghDirectory, ga4ghPort, ga4ghSrc):
    # build the ga4gh server
    srcArg = 'sourceDir=' + ga4ghSrc
    subprocess.call(['docker',  'build', '-t', ga4ghImageName, '--build-arg', srcArg, ga4ghDirectory])

    # run the ga4gh server
    subprocess.Popen(['docker', 'run', '-p', ga4ghPort + ':80', '--name', ga4ghContainerName, ga4ghImageName])

# deploy the funnel server
def funnelDeploy(funnelImageName, funnelContainerName, funnelPort):
    subprocess.call(['docker', 'build', '-t', funnelImageName])

    subprocess.Popen(['docker', 'run', '-p', funnelPort + ':3001', '--name', funnelContainerName, funnelImageName])


# prints the login information post-deployment
def printDeploy(keycloakImageName, keycloakContainerName, keycloakIP, keycloakPort, \
                ga4ghImageName, ga4ghContainerName, ga4ghIP, ga4ghPort, userUsername, \
                userPassword, adminUsername, adminPassword):
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

# writes the keycloak.json configuration file
# the configuration file determines the realms, clients, 
# and users that exist on the server and their settings
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

# writes the new client_secrets.json file 
# for registration of ga4gh client with keycloak CanDIG realm
def ga4ghKeycloakConfig(ga4ghSourceDirectory, keycloakIP, keycloakPort, ga4ghIP, ga4ghPort, ga4ghClientID, clientSecret, realmName):
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


# initializes the local ga4gh source code repository on the host machine
# this function is used if there is no pre-existing ga4gh source to use
# this code is later used to build the server on the docker container 
def initSrc(ga4ghDirectory, ga4ghClientID, clientSecret, ga4ghIP, ga4ghPort, keycloakIP, keycloakPort, override, realmName):
    ga4ghSourceDirectory = ga4ghDirectory + '/ga4gh-server'
    duplicateDirectory = os.path.exists(ga4ghSourceDirectory)  
    # halt if a duplicate directory exists and no override command has been given
    if (not duplicateDirectory) or override:
        # remove the existing source code if a duplicate directory exists
        # and the override command has been given
        if override and duplicateDirectory:
           shutil.rmtree(ga4ghSourceDirectory)
        subprocess.call(['git', 'clone', '--branch', 'authentication', 'https://github.com/CanDIG/ga4gh-server.git', ga4ghSourceDirectory])
        shutil.copyfile(ga4ghDirectory + '/frontend.py', ga4ghSourceDirectory + '/ga4gh/server/frontend.py')
        shutil.copyfile(ga4ghDirectory + '/serverconfig.py', ga4ghSourceDirectory + '/ga4gh/server/serverconfig.py')
        shutil.copyfile(ga4ghDirectory + '/dataPrep.py', ga4ghSourceDirectory + '/dataPrep.py')
        ga4ghKeycloakConfig(ga4ghSourceDirectory, keycloakIP, keycloakPort, ga4ghIP, ga4ghPort, ga4ghClientID, clientSecret, realmName)
    elif duplicateDirectory and (not override):
        print('Using existing source directory and configuration ' + ga4ghSourceDirectory)
        print('Command line configuration options for GA4GH will not be used')

# initialize the command line arguments

parser = argparse.ArgumentParser(description='Deployment script for CanDIG which deploys the GA4GH and Keycloak servers', add_help=True)

# defaults
clientSecret          = '250e42b8-3f41-4d0f-9b6b-e32e09fccaf7'

parser.add_argument(        '--ip',                                                                            help='Set the ip address of both servers')
parser.add_argument('-kip', '--keycloak-ip',             default="192.168.99.100",         dest="keycloakIP",                   help='Set the ip address of the keycloak server')
parser.add_argument('-gip', '--ga4gh-ip',                default="192.168.99.100",         dest="ga4ghIP",               help='Set the ip address of the ga4gh server')
parser.add_argument('-kp',  '--keycloak-port',           default="8080",                   dest="keycloakPort",                    help='Set the port number of the keycloak server')
parser.add_argument('-gp',  '--ga4gh-port',              default="8000",                   dest="ga4ghPort",                       help='Set the port number of the ga4gh server')
parser.add_argument('-r',   '--realm-name',              default="CanDIG",                 dest="realmName",                      help='Set the keycloak realm name')
parser.add_argument('-gid', '--ga4gh-client-id',         default="ga4ghServer",            dest="ga4ghClientID",          help='Set the ga4gh server client id')
parser.add_argument('-kcn', '--keycloak-container-name', default="keycloak_candig_server", dest="keycloakContainerName", help='Set the keycloak container name')
parser.add_argument('-gcn', '--ga4gh-container-name',    default="ga4gh_candig_server",    dest="ga4ghContainerName", help='Set the ga4gh server container name')
parser.add_argument('-kim', '--keycloak-image-name',     default="keycloak_candig_server", dest="keycloakImageName", help='Set the keycloak image tag')
parser.add_argument('-gim', '--ga4ghImageName',          default="ga4gh_candig_server",    dest="ga4ghImageName",   help='Set the ga4gh image tag')
parser.add_argument('-au',  '--admin-username',          default="admin",                  dest="adminUsername",                 help='Set the administrator account username')
parser.add_argument('-uu',  '--user-username',           default="user",                   dest="userUsername",                   help='Set the user account username')
parser.add_argument('-gs'   '--ga4gh-src',               default="ga4gh-server",           dest="ga4ghSrc",                help='Use an existing source directory')
parser.add_argument('-o',   '--override',                default=False,                     action='store_true', help="Force the removal of an existing source code directory")
parser.add_argument('-tt',  '--token-tracer',            default=False, dest='tokenTracer', action='store_true', help='Deploy and run the token tracer program')
parser.add_argument('-ed',  '--extra-data',              default=False, dest='extraData',   action='store_true', help='Add additional test data to the ga4gh server')
parser.add_argument('-nd',  '--no-data',                 default=False, dest='noData',      action='store_true', help='Deploy the ga4gh server with no data')
parser.add_argument('-f',   '--funnel',                  default=False,                     action='store_true', help='Deploy the funnel server')
parser.add_argument(        'deploy',                                                                          help='Deploy the Keycloak and GA4GH server')
parser.add_argument('-s',   '--singularity',             default=False,                     action='store_true', help='Deploy using singularity containers')
parser.add_argument('-cs',  '--client-secret',           default=clientSecret, dest='clientSecret',              help="Client secret for the ga4gh server")
#parser.add_argument('-oc',  '--config-override', default=False, dest='configOverride', action='store_true', help="Overwrite the client secrets file for an existing repository")
#parser.add_argument('--adminPassword', help='Set the administrator account password')
#parser.add_argument('--userPassword', help='Set the user account password')
#parser.add_argument('-c', '--configOnly', help='Reconfigure the existing containers without destroying them', action='store_true')
#parser.add_argument('-b', '--boot', help='Start the existing containers in their current unmodified state', action='store_true')

adminPassword         = "admin"                  # keycloak master realm admin account password
userPassword          = "user"                   # password for the account on which to log into ga4gh server via keycloak
initRepo              = True                     # flag as to whether to clone in a clean repository from the authentication branch of candig ga4gh server
#boot = False
#configOnly = False 
dataArg = 'default'
keycloakDirectory = "./keycloakDocker"
ga4ghDirectory = "./ga4ghDocker"

# parse for command line arguments
args = parser.parse_args()

# override the other ip address if ip specified
if args.ip:
    args.keycloakIP = args.ip
    args.ga4ghIP = args.ip

# initiate the deployment procedure if deploy has been specified
if args.deploy:
    containerTeardown(args.keycloakContainerName, args.ga4ghContainerName)

    keycloakConfigWrite(args.realmName, args.ga4ghClientID, args.clientSecret, args.ga4ghIP,\
                        args.ga4ghPort, args.adminUsername, args.userUsername)

    keycloakDeploy(args.keycloakImageName, args.keycloakContainerName, keycloakDirectory, args.keycloakPort)

    # clone the tokenTracer into the keycloak container if enabled
    if args.tokenTracer:
        subprocess.call(["docker", "exec", args.keycloakContainerName, "git clone https://github.com/Bio-Core/tokenTracer.git"])

    # initialize the repository containing the ga4gh source code locally if unspecified
    if args.ga4ghSrc == 'ga4gh-server':   
        initSrc(ga4ghDirectory, args.ga4ghClientID, args.clientSecret, args.ga4ghIP,\
                args.ga4ghPort, args.keycloakIP, args.keycloakPort, args.override, args.realmName) 

    ga4ghDeploy(args.ga4ghImageName, args.ga4ghContainerName, ga4ghDirectory, args.ga4ghPort,\
                args.ga4ghSrc)

    printDeploy(args.keycloakImageName, args.keycloakContainerName, args.keycloakIP, args.keycloakPort,\
                args.ga4ghImageName, args.ga4ghContainerName, args.ga4ghIP, args.ga4ghPort,\
                args.userUsername, userPassword, args.adminUsername, adminPassword)

    if args.funnel:
        funnelDeploy()


    # execute the tokenTracer if enabled
    if args.tokenTracer: 
        subprocess.call(["docker", "exec", args.keycloakContainerName, "pyparse.py"])
 
exit()
