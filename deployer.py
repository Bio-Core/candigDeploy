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

# clean up any duplicate containers currently running or stopped
def containerTeardown(keycloakContainerName, ga4ghContainerName, vagrantDir, funnelContainerName):
    subprocess.call(['docker', 'container', 'kill', keycloakContainerName, ga4ghContainerName, funnelContainerName])
    subprocess.call(['docker', 'container', 'rm', keycloakContainerName, ga4ghContainerName, funnelContainerName])
    subprocess.call(['vagrant', 'destroy', '-f', 'default'], cwd=vagrantDir)
    #subprocess.call(['vagrant', 'destroy', '-f', '$(vagrant global-status | grep ga4ghVagrantSingularity | awk \'{print $1;}\')'], cwd=ga4ghSingularityDir)

# deploys the keycloak server
# builds the keyserver docker image and runs it
def keycloakDeploy(keycloakImageName, keycloakContainerName, keycloakDir, keycloakPort):
    buildKeycloakCode = subprocess.call(['docker', 'build', '-t', keycloakImageName, keycloakDir])
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
def ga4ghDeploy(ga4ghImageName, ga4ghContainerName, ga4ghDir, ga4ghPort, ga4ghSrc):
    # build the ga4gh server
    srcArg = 'sourceDir=' + ga4ghSrc
    # copy in the files
    #shutil.copyfile(ga4ghDir + '/frontend.py', ga4ghDockerDir + '/ga4gh/server/frontend.py')
    #shutil.copyfile(ga4ghDir + '/serverconfig.py', ga4ghDockerDir + '/ga4gh/server/serverconfig.py')
    #shutil.copyfile(ga4ghDir + '/dataPrep.py', ga4ghDockerDir + '/dataPrep.py')
    #shutil.copyfile(ga4ghDir + '/requirements.txt', ga4ghDockerDir + '/requirements.txt')

    # check for a duplicate source code directory for Docker to copy
    # overwrite it if it exists
    #duplicateDir = os.path.exists(ga4ghDockerDir + '/' + ga4ghSrc)
    #if duplicateDir:
    #    shutil.rmtree(ga4ghDockerDir + '/' + ga4ghSrc) 
    #shutil.copytree(ga4ghDir + '/' + ga4ghSrc, ga4ghDockerDir + '/' + ga4ghSrc)
  
    subprocess.call(['docker',  'build', '-t', ga4ghImageName, '--build-arg', srcArg, ga4ghDir])
    # run the ga4gh server
    subprocess.Popen(['docker', 'run', '-p', ga4ghPort + ':80', '--name', ga4ghContainerName, ga4ghImageName])


# deploy ga4gh via singularity through a vagrant container
# we should also have an option that deploys them directly via singularity
# this would require us to test it in a linux environment
def singularityDeploy(vagrantDir):
    # os.environ["SECRET"] = clientSecret
    # os.environ["KEYCLOAK_IP"] = keycloakIP 
    # os.environ["GA4GH_IP"] = ga4ghIP 
    # os.environ["GA4GH_CLIENT_ID"] = ga4ghClientID 
    # os.environ["GA4GH_REALM_NAME"] = realmName 
    subprocess.call(['vagrant', 'up'], cwd=vagrantDir)
    #subprocess.call(['vagrant', 'ssh', '--command', 'sudo singularity run keycloak.img'], cwd=vagrantDir)
    #subprocess.call(['vagrant', 'ssh', '--command', 'sudo singularity run ga4gh-server.img'], cwd=vagrantDir)

    
# deploy the funnel server
def funnelDeploy(funnelImageName, funnelContainerName, funnelPort, funnelDir):
    print('funnelDeploy')
    subprocess.call(['docker', 'build', '-t', funnelImageName, funnelDir])
    subprocess.Popen(['docker', 'run', '-p', funnelPort + ':3002', '--name', funnelContainerName, funnelImageName])


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
def keycloakConfigWrite(realmName, ga4ghClientID, clientSecret, ga4ghIP, ga4ghPort, adminUsername, userUsername, keycloakDir):
    keycloakConfigFile = keycloakDir + '/keycloakConfig.json'
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



# writes the keycloak.json file for the funnel client
def funnelKeycloakConfig(realmName, keycloakIP, keycloakPort, funnelPort, funnelIP, funnelSecret, funnelClientID, funnelDir):
    print('funnelConfig')

    fileName = funnelDir + '/funnel-node/node-client/keycloak.json'

    authUrl = "http://" + keycloakIP + ":" + keycloakPort + "/auth"
    redirectList = [ "http://" + funnelIP + ":" + funnelPort + "/oidc_callback" ]
    secretDict = { "secret" : funnelSecret } 

    keycloakData = { "realm" : realmName, "auth-server-url": authUrl, "resource" : funnelClientID, "redirect_uris" : redirectList, "credentials" : secretDict }

    jsonData = json.dumps(keycloakData)

    fileHandle = open(fileName, 'w')
    fileHandle.write(jsonData)
    fileHandle.close()    

# writes the new client_secrets.json file 
# for registration of ga4gh client with keycloak CanDIG realm
def ga4ghKeycloakConfig(ga4ghSourceDir, keycloakIP, keycloakPort, ga4ghIP, ga4ghPort, ga4ghClientID, clientSecret, realmName):

    fileName = ga4ghSourceDir + '/client_secrets.json'

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
def initSrc(ga4ghDir, ga4ghClientID, clientSecret, ga4ghIP, ga4ghPort, keycloakIP, keycloakPort, override, realmName):

    ga4ghSourceDir = ga4ghDir + '/ga4gh-server'
    duplicateDir = os.path.exists(ga4ghSourceDir)  

    # halt if a duplicate directory exists and no override command has been given
    if (not duplicateDir) or override:
        # remove the existing source code if a duplicate directory exists
        # and the override command has been given
        if override and duplicateDir:
           shutil.rmtree(ga4ghSourceDir)

        subprocess.call(['git', 'clone', '--branch', 'authentication', 'https://github.com/CanDIG/ga4gh-server.git', ga4ghSourceDir])

        shutil.copyfile(ga4ghDir + '/requirements.txt', ga4ghSourceDir + '/requirements.txt')
        shutil.copyfile(ga4ghDir + '/frontend.py', ga4ghSourceDir + '/ga4gh/server/frontend.py')
        shutil.copyfile(ga4ghDir + '/serverconfig.py', ga4ghSourceDir + '/ga4gh/server/serverconfig.py')
        shutil.copyfile(ga4ghDir + '/dataPrep.py', ga4ghSourceDir + '/dataPrep.py')

        ga4ghKeycloakConfig(ga4ghSourceDir, keycloakIP, keycloakPort, ga4ghIP, ga4ghPort, ga4ghClientID, clientSecret, realmName)

    elif duplicateDir and (not override):
        print('Using existing source directory and configuration ' + ga4ghSourceDir)
        print('Command line configuration options for GA4GH will not be used')

# initialize the command line arguments

parser = argparse.ArgumentParser(description='Deployment script for CanDIG which deploys the GA4GH and Keycloak servers', add_help=True)

# defaults
clientSecret = '250e42b8-3f41-4d0f-9b6b-e32e09fccaf7'
funnelSecret = "44f9ebc0-0a21-4044-b93c-f654dcd3f1b9"

parser.add_argument('-i',   '--ip',                                                                                      help='Set the ip address of both servers')
parser.add_argument('-kip', '--keycloak-ip',             default="127.0.0.1",              dest="keycloakIP",            help='Set the ip address of the keycloak server')
parser.add_argument('-gip', '--ga4gh-ip',                default="127.0.0.1",              dest="ga4ghIP",               help='Set the ip address of the ga4gh server')
parser.add_argument('-kp',  '--keycloak-port',           default="8080",                   dest="keycloakPort",          help='Set the port number of the keycloak server')
parser.add_argument('-gp',  '--ga4gh-port',              default="8000",                   dest="ga4ghPort",             help='Set the port number of the ga4gh server')
parser.add_argument('-r',   '--realm-name',              default="CanDIG",                 dest="realmName",             help='Set the keycloak realm name')
parser.add_argument('-gid', '--ga4gh-client-id',         default="ga4ghServer",            dest="ga4ghClientID",         help='Set the ga4gh server client id')
parser.add_argument('-kcn', '--keycloak-container-name', default="keycloak_candig_server", dest="keycloakContainerName", help='Set the keycloak container name')
parser.add_argument('-gcn', '--ga4gh-container-name',    default="ga4gh_candig_server",    dest="ga4ghContainerName",    help='Set the ga4gh server container name')
parser.add_argument('-kin', '--keycloak-image-name',     default="keycloak_candig_server", dest="keycloakImageName",     help='Set the keycloak image tag')
parser.add_argument('-gin', '--ga4gh-image-name',        default="ga4gh_candig_server",    dest="ga4ghImageName",        help='Set the ga4gh image tag')
parser.add_argument('-au',  '--admin-username',          default="admin",                  dest="adminUsername",         help='Set the administrator account username')
parser.add_argument('-uu',  '--user-username',           default="user",                   dest="userUsername",          help='Set the user account username')
parser.add_argument('-gs',  '--ga4gh-src',               default="ga4gh-server",           dest="ga4ghSrc",              help='Use an existing source directory')
parser.add_argument('-o',   '--override',                default=False,                     action='store_true',         help="Force the removal of an existing source code directory")
parser.add_argument('-t',   '--token-tracer',            default=False, dest='tokenTracer', action='store_true',         help='Deploy and run the token tracer program')
parser.add_argument('-ed',  '--extra-data',              default=False, dest='extraData',   action='store_true',         help='Add additional test data to the ga4gh server')
parser.add_argument('-nd',  '--no-data',                 default=False, dest='noData',      action='store_true',         help='Deploy the ga4gh server with no data')
parser.add_argument('-f',   '--funnel',                  default=False,                     action='store_true',         help='Deploy the funnel server')
parser.add_argument(        'deploy',                                                                                    help='Deploy the Keycloak and GA4GH server')
parser.add_argument('-s',   '--singularity',             default=False,                     action='store_true',         help='Deploy using singularity containers')
parser.add_argument('-cs',  '--client-secret',           default=clientSecret,             dest='clientSecret',          help="Client secret for the ga4gh server")
parser.add_argument('-fin', '--funnel-image-name',       default="funnel_candig_server",   dest="funnelImageName",       help='Set the funnel image tag')
parser.add_argument('-fcn', '--funnel-container-name',   default="funnel_candig_server",   dest="funnelContainerName",   help='Set the funnel container name')
parser.add_argument('-fp',  '--funnel-port',             default="3002",                   dest="funnelPort",            help='Set the funnel port number')
parser.add_argument('-fip', '--funnel-ip',               default="127.0.0.1",              dest="funnelIP",              help='Set the funnel ip address')
parser.add_argument('-fs',  '--funnel-secret',           default=funnelSecret,             dest="funnelSecret",              help='Set the funnel client secret')
parser.add_argument('-fid', '--funnel-client-id',        default="funnel",                 dest="funnelClientID",        help='Set the funnel client id')
parser.add_argument('-ng', '--no-ga4gh',        default=False,                 dest="noGa4gh", action='store_true',      help="Do not deploy the GA4GH server")

#parser.add_argument('-nk',  '--no-keycloak', default=False, dest=noKeycloak, action='store_true', help="Do not deploy Keycloak")
#parser.add_argument('-ck', '--config-keycloak', default=False, dest=configKeycloak, action='store_true', help='Reconfigure keycloak only - do not reinstall')
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
keycloakDir = "./keycloak"
ga4ghDir = "./ga4gh"
vagrantDir = './vagrant'
funnelDir="./funnel"

# parse for command line arguments
args = parser.parse_args()

# override the other ip address if ip specified
if args.ip:
    args.keycloakIP = args.ip
    args.ga4ghIP = args.ip

if args.singularity:
    args.keycloakIP = "192.168.12.123"
    args.ga4ghIP = "192.168.12.123"

# initiate the deployment procedure if deploy has been specified
if args.deploy:
    containerTeardown(args.keycloakContainerName, args.ga4ghContainerName, vagrantDir, args.funnelContainerName)
 
    keycloakConfigWrite(args.realmName, args.ga4ghClientID, args.clientSecret, args.ga4ghIP,\
                        args.ga4ghPort, args.adminUsername, args.userUsername, keycloakDir)

    if (not args.singularity):
        keycloakDeploy(args.keycloakImageName, args.keycloakContainerName, keycloakDir, args.keycloakPort)

    # initialize the repository containing the ga4gh source code locally if unspecified
    if args.ga4ghSrc == 'ga4gh-server':   
        initSrc(ga4ghDir, args.ga4ghClientID, args.clientSecret, args.ga4ghIP,\
                args.ga4ghPort, args.keycloakIP, args.keycloakPort, args.override, args.realmName) 

    if args.singularity:        
        singularityDeploy(vagrantDir)
    elif (not args.noGa4gh):
        ga4ghDeploy(args.ga4ghImageName, args.ga4ghContainerName, ga4ghDir, args.ga4ghPort,\
                    args.ga4ghSrc)

    printDeploy(args.keycloakImageName, args.keycloakContainerName, args.keycloakIP, args.keycloakPort,\
                args.ga4ghImageName, args.ga4ghContainerName, args.ga4ghIP, args.ga4ghPort,\
                args.userUsername, userPassword, args.adminUsername, adminPassword)

    if args.funnel:
        funnelKeycloakConfig(args.realmName, args.keycloakIP, args.keycloakPort, args.funnelPort, args.funnelIP, args.funnelSecret, args.funnelClientID, funnelDir)
        funnelDeploy(args.funnelImageName, args.funnelContainerName, args.funnelPort, funnelDir)


    # execute the tokenTracer if enabled
    if args.tokenTracer: 
        time.sleep(5)
        print('tokenTracer')
        subprocess.call(["docker", "exec", args.keycloakContainerName, "apt-get install -y python python-pip git"])
        subprocess.call(["docker", "exec", args.keycloakContainerName, "git clone https://github.com/Bio-Core/tokenTracer.git"])
        subprocess.call(["docker", "exec", args.keycloakContainerName, "pip install pyshark"])
        subprocess.call(["docker", "exec", args.keycloakContainerName, "python", "/home/tokenTracer/pyparseLive.py"])
 
exit()
