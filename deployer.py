#!/usr/bin/python

import subprocess
import argparse
import sys
import shutil
import os
import json

# configure the IP from which to access keycloak and ga4gh from the host
keycloakIP = "192.168.99.100"
ga4ghIP = keycloakIP

# the ports on which to find the keycloak and ga4gh server from the host
keycloakPort = "8080"
ga4ghPort = "8000"

# ga4gh client id and realm name on which ga4gh will be registed
ga4ghClientID = "ga4ghServer"
realmName = "CanDIG"

# the image and container name for the keycloak server
keycloakImageName = "keycloak_candig_server"
keycloakContainerName = keycloakImageName

# the image and container name for the ga4gh server
ga4ghImageName = "ga4gh_candig_server"
ga4ghContainerName = ga4ghImageName

# the username and password of the administrator account 
# for the keycloak server on the master realm
adminUsername = "admin"
adminPassword = "admin"

# the username and password of the user account
# for the keycloak server on the ga4gh realm
userUsername = "user"
userPassword = "user"

#sourceDirectory = subprocess.getOutput(["pwd"])
initRepo = True
boot = False
configOnly = False 
force = False
# parse the optional command line arguments
# usage function explaining how to use the program
parser = argparse.ArgumentParser(description='Deployment script for Candig which deploys the ga4gh and keycloak servers')

parser.add_argument('-i', '--ip', help='Set the ip address of both servers')
parser.add_argument('-k', '--keycloakIP', help='Set the ip address of the keycloak server')
parser.add_argument('-g', '--ga4ghIP', help='Set the ip address of the ga4gh server')
parser.add_argument('-p', '--keycloakPort', help='Set the port number of the keycloak server')
parser.add_argument('-o', '--ga4ghPort', help='Set the port number of the ga4gh server')
parser.add_argument('-r', '--realmName', help='Set the keycloak realm name')
parser.add_argument('-d', '--ga4ghClientID', help='Set the ga4gh server client id')
parser.add_argument('--keycloakContainerName', help='Set the keycloak container name')
parser.add_argument('--ga4ghContainerName', help='Set the ga4gh server container name')
parser.add_argument('--keycloakImageName', help='Set the keycloak image tag')
parser.add_argument('--ga4ghImageName', help='Set the ga4gh image tag')
parser.add_argument('-a', '--adminUsername', help='Set the administrator account username')
parser.add_argument('--adminPassword', help='Set the administrator account password')
parser.add_argument('-n', '--userUsername', help='Set the user account username')
parser.add_argument('--userPassword', help='Set the user account password')
parser.add_argument('-s', '--src', help='Use an existing source directory')
parser.add_argument('-c', '--configOnly', help='Reconfigure the existing containers without destroying them', action='store_true')
parser.add_argument('-b', '--boot', help='Start the existing containers in their current unmodified state', action='store_true')
parser.add_argument('-f', '--force', help="Force the removal of an existing source code directory")
# make a config option which can set each of these permanently individually 
# maybe revert to defaults option?

if boot:
    # start the containers
    subprocess.Popen(['docker', 'run', '-p', keycloakPort + ':8080', '--name', keycloakContainerName, keycloakImageName])
    subprocess.call(['docker', 'run', '-p', ga4ghPort + ':80', '--name', ga4ghContainerName, ga4ghImageName])
    exit()
elif configOnly:  
    # copy the configuration file into the keycloak container
    # copy the local source code into the ga4gh container
    configFileSrc = keycloakDirectory + '/keycloakConfig.json'
    ga4ghSrc = ga4ghDirectory + '/ga4gh-server'
    keycloakDest = keycloakContainerName + ':/home/keycloak'
    ga4ghDest = ga4ghContainerName + ':/home/ga4gh-server'
    subprocess.call(['docker', 'cp', configFileSrc, keycloakDest])
    subprocess.call(['docker', 'cp', ga4ghSrc, ga4ghDest])

    # restart the servers on the containers
    subprocess.call(['docker', 'exec', keycloakContainerName, '/home/keycloak/bin/standalone.sh'])
    subprocess.call(['docker', 'exec', ga4ghContainerName, 'apache-restart'])
    exit()

# clean up any duplicate containers currently running or stopped
subprocess.call(['docker', 'container', 'kill', keycloakContainerName, ga4ghContainerName])
subprocess.call(['docker', 'container', 'rm', keycloakContainerName, ga4ghContainerName])

# build the keycloak server
keycloakDirectory = "./keycloakDocker"
ga4ghDirectory = "./ga4ghDocker"
clientSecret = '250e42b8-3f41-4d0f-9b6b-e32e09fccaf7'

subprocess.call(['docker', 'build', '-t', keycloakImageName, keycloakDirectory])

# run the keycloak server as a background process
subprocess.Popen(['docker', 'run', '-p', keycloakPort + ':8080', '--name', keycloakContainerName, keycloakImageName])

# initialize the repository containing the ga4gh source code locally if specified

ga4ghSourceDirectory = ga4ghDirectory + '/ga4gh-server'

if initRepo:    
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

# build the ga4gh server
subprocess.call(['docker',  'build', '-t', ga4ghImageName, '--build-arg', 'sourceDir=ga4gh-server', ga4ghDirectory])

# run the ga4gh server
subprocess.call(['docker', 'run', '-p', ga4ghPort + ':80', '--name', ga4ghContainerName, ga4ghImageName])

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

exit()
