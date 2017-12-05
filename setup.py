
from setuptools import setup, find_packages

setup(name="candigDeploy",
      version="0.0.1",
      description="Deployment program for the CanDIG project",
      long_description="Deploys Keycloak and authenticated GA4GH and Funnel application servers.\
                        Supports deployment through Docker, Singularity, or Vagrant containers",
      url="https://github.com/Bio-Core/candigDeploy",
      author="Dale Dupont",
      author_email="dale.dupont@uhnresearch.ca",
      license="Apache 2.0",
      classifiers=["Development Status :: 3 - Alpha",
                  "Intended Audience :: Developers",
                  "Intended Audience :: System Administrators",
                  "LICENSE :: OSI Approved :: Apache Software License",
                  "Programming Language :: Python :: 2",
                  "Programming Language :: Python 2.7",
                  "Natural Language :: English",
                  "Topic :: Scientific/Engineering :: Bio-Informatics",
                  "Topic :: System :: Installation/Setup",
                  "Topic :: Utilities"],
      keywords="utility command-line candig deploy deployment deployer ga4gh keycloak funnel authentication server setup",
      packages=find_packages(exclude=['docs', 'tests']),
      install_requires=["PyYAML"],
      python_requires=">=2.7",
      include_package_data=True,
      entry_points = {
          "console_scripts": ["candigDeploy = deployer.deployer:main"]
      })
