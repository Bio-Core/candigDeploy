#!/usr/bin/python

import sys
import subprocess

dataArg = sys.argv[1]

if dataArg == 'default':
    subprocess.call(['python', './scripts/prepare_compliance_data.py', '-o', '../ga4gh-compliance-data'])
elif dataArg == 'extra':
    subprocess.call(["ga4gh_repo", "add-dataset ga4gh-example-data/registry.db", "1kgenomes", "--description", "Variants  from the 1000 Genomes project and GENCODE genes annotations"])
    subprocess.call(["wget", "ftp://ftp.1000genomes.ebi.ac.uk//vol1/ftp/technical/reference/phase2_reference_assembly_sequence/hs37d5.fa.gz"])
    subprocess.call(["gunzip", "hs37d5.fa.gz"])
    subprocess.call(["git", "clone", "https://github.com/samtools/htslib", ".."])
    subprocess.call(["apt-get", "install" "-y", "autoconf", "bzip2-devel", "make"])
    #subprocess.call(["./autoheader", "../htslib"])
    subprocess.call(["./autoconf", "../htslib"])
    subprocess.call(["./configure", "../htslib"])
    subprocess.call(["make", "../htslib"])
    subprocess.call(["../htslib/bgzip", "hs37d5.fa"])
    subprocess.call(["ga4gh_repo", "add-referenceset", "registry.db", "/full/path/to/hs37d5.fa.gz", "-d", "NCBI37 assembly of the human genome", "--species", "\'{ \"term\" : \"Homo_sapiens\" }\'", "--name", "NCBI37", "--sourceUri", "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/phase2_reference_assembly_sequence/hs37d5.fa.gz"])
    subprocess.call(["wget", "https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/so-xp-dec.obo"]) 
    subprocess.call(["ga4gh_repo", "add-ontology", "ga4gh-example-data/registry.db", "so-xp-dec.obo", "-n", "so-xp"])
    subprocess.call(["wget", "-m", "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/", "-nd", "-P", "release", "-l", "1"])
    subprocess.call(["rm", "release/ALL.wgs.*"])
    subprocess.call(["ga4gh_repo", "add-variantset", "registry.db", "1kgenomes", "release/", "--name", "phase3-release", "--referenceSetName", "NCBI37"])
    subprocess.call(["wget", "http://s3.amazonaws.com/1000genomes/phase3/data/HG00096/alignment/HG00096.mapped.ILLUMINA.bwa.GBR.low_coverage.20120522.bam.bai"])
    subprocess.call(["ga4gh_repo", "add-readgroupset", "registry.db", "1kgenomes", "-I", "HG00096.mapped.ILLUMINA.bwa.GBR.low_coverage.20120522.bam.bai", "--referenceSetName", "NCBI37", "http://s3.amazonaws.com/1000genomes/phase3/data/HG00096/alignment/HG00096.mapped.ILLUMINA.bwa.GBR.low_coverage.20120522.bam"])

else:
    pass

exit
