#!/bin/bash
wget https://downloads.jboss.org/keycloak/3.4.0.Final/keycloak-3.4.0.Final.zip
unzip keycloak-3.4.0.Final.zip
./keycloak-3.4.0.Final/bin/standalone.sh -Dkeycloak.migration.action=import -Dkeycloak.migration.provider=singleFile -Dkeycloak.migration.file=../keycloakConfig.json -Dkeycloak.migration.strategy=OVERWRITE_EXISTING
