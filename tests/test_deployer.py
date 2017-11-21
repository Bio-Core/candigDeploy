import unittest

from deployer.deployer import deployer

class argParserTest(unittest.TestCase):

    def setUp(self):
        self.deployer = deployer()
        self.args = deployer.commandArgs(["deploy"])

    def testDeploy(self):         
        assertTrue(self.args.deploy)

    def testVagrant(self):
        assertFalse(self.args.vagrant)

    def testIP(self):
        assertFalse(self.args.ip)

    def testNoData(self):
        assertFalse(self.args.noData)

    def testExtraData(self):
        assertFalse(self.args.extraData)

    def testKeycloakIP(self):
        keycloakIP = "127.0.0.1"
        assertEqual(self.args.keycloakIP, keycloakIP)

    def testGa4ghIP(self):
        ga4ghIP = "127.0.0.1"
        assertEqual(self.args.ga4ghIP, ga4ghIP)

    def testGa4ghPort(self):
        ga4ghPort = "8000"
        assertEqual(self.args.ga4ghPort, ga4ghPort)

    def testKeycloakPort(self):
        keycloakPort = "8080"
        assertEqual(self.args.keycloakPort, keycloakPort)

    def testRealmName(self):
        realmName = "CanDIG"
        assertEqual(self.args.realmName, realmName)

    def testGa4ghID(self):
        ga4ghID = "ga4gh"
        assertEqual(self.args.ga4ghID, ga4ghID)

    def testKeycloakContainerName(self):
        keycloakContainerName = "keycloak_candig_server"
        assertEqual(self.args.keycloakContainerName, keycloakContainerName)

    def testGa4ghContainerName(self):
        ga4ghContainerName = "ga4gh_candig_server"
        assertEqual(self.args.ga4ghContainerName, ga4ghContainerName)

    def testKeycloakImageName(self):
        keycloakImageName = "keycloak_candig_server"
        assertEqual(self.args.keycloakImageName, keycloakImageName)

    def testGa4ghImageName(self):
        ga4ghImageName = "ga4gh_candig_server"
        assertEqual(self.args.ga4ghImageName, ga4ghImageName)




