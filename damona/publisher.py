#
#  This file is part of Damona software
#
#  Copyright (c) 2020 - Damona Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/cokelaer/damona
#  documentation: http://damona.readthedocs.io
#
##############################################################################
"""Publisher: automates the full build → check → upload workflow for developers."""
import os
import subprocess
import sys

import colorlog

from damona.builders import BuilderFromSingularityRecipe
from damona.zenodo import Zenodo

logger = colorlog.getLogger(__name__)

__all__ = ["Publisher"]


class Publisher:
    """Automate the full developer workflow: build, check, and upload a container.

    A developer typically performs three steps when releasing a new container:

    1. Build a Singularity image from a recipe file.
    2. Validate the image (check that required commands are present).
    3. Upload the image to Zenodo.

    :class:`Publisher` wraps these steps so they can be executed individually
    or all at once with :meth:`publish`.

    ::

        from damona.publisher import Publisher

        pub = Publisher("Singularity.fastqc_0.12.1", mode="sandbox.zenodo")
        pub.build()
        pub.check()
        pub.upload()

    Or in one call::

        pub.publish()

    """

    def __init__(self, recipe, mode="sandbox.zenodo", token=None, destination=None, force=False):
        """.. rubric:: **Constructor**

        :param str recipe: Path to the Singularity recipe file.  The basename
            must start with ``Singularity.`` and follow the
            ``Singularity.NAME_x.y.z`` naming convention.
        :param str mode: Zenodo target.  Either ``"zenodo"`` (production) or
            ``"sandbox.zenodo"`` (testing, default).
        :param token: Zenodo API token.  When ``None`` the token is read from
            the ``damona.cfg`` configuration file.
        :type token: str or None
        :param destination: Output ``.img`` file path.  When ``None`` the
            destination is derived from the recipe name by stripping the
            ``Singularity.`` prefix and appending ``.img``.
        :type destination: str or None
        :param bool force: Overwrite an existing image without prompting
            (default ``False``).
        """
        self.recipe = recipe
        self.mode = mode
        self.token = token
        self.force = force

        if not os.path.basename(recipe).startswith("Singularity."):
            logger.error("Recipe must start with 'Singularity.' (e.g. Singularity.fastqc_0.12.1)")
            sys.exit(1)

        if destination is None:
            self.destination = os.path.basename(recipe).replace("Singularity.", "") + ".img"
        else:
            self.destination = destination

    def build(self):
        """Build the Singularity container from the recipe.

        Delegates to :class:`~damona.builders.BuilderFromSingularityRecipe`.

        :raises SystemExit: When the recipe name is invalid or the build fails.
        """
        logger.info(f"Building container from {self.recipe}")
        builder = BuilderFromSingularityRecipe()
        builder.build(self.recipe, destination=self.destination, force=self.force)

    def check(self):
        """Validate the built container.

        Runs two quick sanity checks inside the image:

        * **bash** – mandatory; exits with an error when absent.
        * **python** – optional; logs a warning when absent.

        :returns: ``True`` when all required checks pass.
        :rtype: bool
        :raises SystemExit: When ``bash`` is not found in the container.
        """
        logger.info(f"Checking container {self.destination}")

        status = subprocess.run(
            ["singularity", "exec", self.destination, "python", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if status.returncode:
            logger.warning("Could not find **python** command in the container")
        else:
            logger.info("python is available in the container")

        status = subprocess.run(
            ["singularity", "exec", self.destination, "bash", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if status.returncode:
            logger.error("Could not find **bash** command in the container")
            sys.exit(1)
        else:
            logger.info("bash is available in the container")

        return True

    def upload(self):
        """Upload the container image to Zenodo.

        Uses the :class:`~damona.zenodo.Zenodo` class.  The Zenodo author,
        affiliation, and ORCID are read from ``damona.cfg`` when not
        supplied at construction time.

        :raises SystemExit: When the Zenodo token or author metadata is
            missing, or when the upload fails.
        """
        logger.info(f"Uploading {self.destination} to {self.mode}")
        z = Zenodo(self.mode, self.token)
        z._upload(self.destination)

    def publish(self):
        """Run the full workflow: build, check, and upload.

        Convenience method that calls :meth:`build`, :meth:`check`, and
        :meth:`upload` in sequence.

        :raises SystemExit: On any build, validation, or upload failure.
        """
        logger.info(f"Starting publication workflow for {self.recipe}")
        self.build()
        self.check()
        self.upload()
        logger.info("Publication workflow completed successfully")
