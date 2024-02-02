import os
import sys

from setuptools import find_packages, setup

_MAJOR = 0
_MINOR = 16
_MICRO = 0
version = "%d.%d.%d" % (_MAJOR, _MINOR, _MICRO)
release = "%d.%d" % (_MAJOR, _MINOR)


metainfo = {
    "authors": {"main": ("Thomas Cokelaer", "thomas.cokelaer@pasteur.fr")},
    "maintainer": {"main": ("Thomas Cokelaer", "thomas.cokelaer@pasteur.fr")},
    "version": version,
    "license": "new BSD",
    "download_url": "https://github.com/sequana/sequana/archive/{0}.tar.gz".format(version),
    "url": "http://github.com/sequana/sequana",
    "description": "A set of standalone application and pipelines dedicated to NGS (new generation sequencing) analysis",
    "platforms": ["Linux", "Unix", "MacOsX", "Windows"],
    "keywords": ["NGS", "snakemake"],
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
}


packages = find_packages()
packages = [this for this in packages if this.startswith("test.") is False]
packages = [this for this in packages if this not in ["test"]]

# load a common list of requirements
requirements = open("requirements.txt").read().split()


setup(
    name="sequana",
    version=version,
    maintainer=metainfo["authors"]["main"][0],
    maintainer_email=metainfo["authors"]["main"][1],
    author=metainfo["authors"]["main"][0],
    author_email=metainfo["authors"]["main"][1],
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    keywords=metainfo["keywords"],
    description=metainfo["description"],
    license=metainfo["license"],
    platforms=metainfo["platforms"],
    url=metainfo["url"],
    download_url=metainfo["download_url"],
    classifiers=metainfo["classifiers"],
    # package installation
    packages=packages,
    # pillow, sphinx-gallery and numpydoc are  for the doc only
    # mock is for the test only qtconsole is required by Sequanix
    install_requires=requirements,
    # specific packages for testing
    # This is recursive include of data files
    exclude_package_data={"": ["__pycache__"]},
    package_data={
        "": [
            "README.rst",
            "requirements*txt",
        ],
        "sequana.multiqc": ["*yaml"],
    },
    # these files do not need to be added in MANIFEST.in since there are python
    # packages that will be copied from sequana/ into sequana/
    # Note, however, that e.g. ./pipelines must be added
    zip_safe=False,
    # ext_modules = ext_modules,
    entry_points={
        "multiqc.modules.v1": [
            "sequana_pacbio_qc=sequana.multiqc.pacbio_qc:MultiqcModule",
            "sequana_quality_control=sequana.multiqc.quality_control:MultiqcModule",
            "sequana_coverage=sequana.multiqc.coverage:MultiqcModule",
            "sequana_isoseq=sequana.multiqc.isoseq:MultiqcModule",
            "sequana_isoseq_qc=sequana.multiqc.isoseq_qc:MultiqcModule",
            "sequana_bamtools_stats=sequana.multiqc.bamtools_stats:MultiqcModule",
            "sequana_laa=sequana.multiqc.laa:MultiqcModule",
            "sequana_kraken=sequana.multiqc.kraken:MultiqcModule",
            "sequana_pacbio_amplicon=sequana.multiqc.pacbio_amplicon:MultiqcModule",
        ],
        "multiqc.hooks.v1": [
            "before_config = sequana.multiqc.config:load_config",
        ],
    },
)
