Future features and fixes for the following releases:

- Get Singularity deployment of Keycloak working in a non-root environment with automatic configuration
- Remove hard-coded absolute paths
- Allow the script candigDeploy to be run in any direction
    - Make the paths absolute to the installation
    OR
    - Place the data in an absolute location on the system
- Add more documentation, including design docs
- Add more tests
- Refactor the deployer in functionally separate parts
   - Support modularity and extenisbility of the deployer better

Edits on the forked GA4GH server:
- Make the paths that must be changed configurable in a single file
- Refactor the authentication to be less code and simpler

