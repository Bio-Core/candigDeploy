import argparse

class cmdparse:
    """
    Class reponsible for initializing and 
    parsing command-line arguments.

    All command-line arguments are created 
    and registered inside this class.

    Cmdparse is called by the deployer
    to parse and return the arguments
    input by the user when the program
    was called.
    """

    def __init__(self):
        self.ga4ghSecret = "250e42b8-3f41-4d0f-9b6b-e32e09fccaf7"
        self.funnelSecret = "07998d29-17aa-4821-9b9e-9f5c398146c6"

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
        rewriteGroup = parser.add_mutually_exclusive_group() 

        localhost = "127.0.0.1"
        keycloakName = "keycloak_candig"
        ga4ghName =  "ga4gh_candig"
        funnelName = "funnel_candig"

        commandList = [ 
            ("-s",              "--singularity", 
              False,              "singularity",
              "store_true",       "Deploy using singularity containers"),
            ("-i",              "--ip",                      
              None,               "ip",                    
              "store",            "Set the ip address of both servers"),
            ("-kip",            "--keycloak-ip",             
              localhost,          "keycloakIP",            
              "store",            "Set the ip address of the keycloak server"),
            ("-gip",            "--ga4gh-ip",                
              localhost,          "ga4ghIP",               
              "store",            "Set the ip address of the ga4gh server"),
            ("-kp",             "--keycloak-port",           
              "8080",             "keycloakPort",          
              "store",            "Set the port number of the keycloak server"), 
            ("-gp",             "--ga4gh-port",              
              "8000",             "ga4ghPort",             
              "store",            "Set the port number of the ga4gh server"),
            ("-r",              "--realm-name",              
              "CanDIG",           "realmName",             
              "store",            "Set the keycloak realm name"),
            ("-gid",            "--ga4gh-id",                
              "ga4gh",            "ga4ghID",               
              "store",            "Set the ga4gh server client id"),
            ("-kcn",            "--keycloak-container-name", 
              keycloakName,       "keycloakContainerName", 
              "store",            "Set the keycloak container name"),
            ("-gcn",            "--ga4gh-container-name",    
              ga4ghName,          "ga4ghContainerName",    
              "store",            "Set the ga4gh server container name"),
            ("-kin",            "--keycloak-image-name",     
              keycloakName,       "keycloakImageName",     
              "store",            "Set the keycloak image tag"),
            ("-gin",            "--ga4gh-image-name",        
              ga4ghName,          "ga4ghImageName",        
             "store",             "Set the ga4gh image tag"),
            ("-au",             "--admin-username",          
              "admin",            "adminUsername",         
              "store",            "Set the administrator account username"),
            ("-uu",             "--user-username",           
              "user",             "userUsername",          
              "store",            "Set the user account username"),
            ("-gs",             "--ga4gh-secret",            
              self.ga4ghSecret,   "ga4ghSecret",           
              "store",            "Client secret for the ga4gh server"),
            ("-fin",            "--funnel-image-name",       
              funnelName,         "funnelImageName",       
              "store",            "Set the funnel image tag"),
            ("-fcn",            "--funnel-container-name",   
              funnelName,         "funnelContainerName",   
              "store",            "Set the funnel container name"),
            ("-fp",             "--funnel-port",             
              "3002",             "funnelPort",            
              "store",            "Set the funnel port number"),
            ("-fip",            "--funnel-ip",               
              localhost,          "funnelIP",              
              "store",            "Set the funnel ip address"),
            ("-fid",            "--funnel-id",               
              "funnel",           "funnelID",              
              "store",            "Set the funnel client id"),
            ("-fs",             "--funnel-secret",           
              self.funnelSecret,  "funnelSecret",          
              "store",            "Set the funnel client secret"),
            ("-f",              "--funnel",                  
              False,              "funnel",                
              "store_true",       "Deploy the funnel server"),
            ("-t",              "--token-tracer",            
              False,              "tokenTracer",          
              "store_true",       "Deploy and run the token tracer program"),
            ("-ng",             "--no-ga4gh",                
              False,              "noGa4gh",              
              "store_true",       "Do not deploy the GA4GH server"),
            ("-upwd",           "--user-password",          
              "user",             "userPassword",         
              "store",            "Set the user account password"),
            ("-apwd",           "--admin-password",         
              "admin",            "adminPassword",        
              "store",            "Set the administrator password")]

        for subList in commandList:
            parser.add_argument(subList[0], subList[1], default=subList[2], dest=subList[3], action=subList[4], help=subList[5])

        rewriteGroup.add_argument("-o",  "--override",    default=False,                   action="store_true", help="Force the removal of an existing source code directory")
        rewriteGroup.add_argument("-nc", "--no-config",    default=False, dest="noConfig", action="store_true", help="Surpress reconfiguration of the client_secrets for the GA4GH server")

        # parse for command line arguments
        args = parser.parse_args(commandArgs)

        return args
