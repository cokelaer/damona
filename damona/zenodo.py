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
"""Tools to upload/retrieve zenodo deposits"""
import inspect
import json
import os
import sys
from configparser import NoOptionError, NoSectionError

import click
import colorlog
import requests
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from damona import Config
from damona.registry import ImageName, Software

logger = colorlog.getLogger(__name__)


logger.setLevel("INFO")


class Zenodo:  # pragma: no cover
    """

    ::

        z = Zenodo(mode="sandbox.zenodo")

    You can retrieve an existing deposit (read-only) given its ID::

        deposit = z.get_deposition(959590)

    Or start with a new one::

        deposit = z.create_new_deposition()


    If you want to create a new file deposition and publish it, follow those 4 commands:

    1. create a new deposit::

        deposit = z.create_new_deposition()
        ID = deposit['id']
        # e.g. 959590

    2. upload data::

        up = z.upload('file', deposit)
        # this gives us the md5sum for later

    3. metadata. Here, we update the deposit with some metadata::

        data = z.get_metadata("fastqc", "v0.11.8")
        update = z.update_metadata(deposit, data)

    4. publish  NOTE THAT PUBLISHED DEPOSITION CANNOT BE MODIFIED NOR DELETED::

        published = z.publish(deposit)

    # if we want an update, we must create a new version from a published deposit::

        new_version = z.create_new_deposit_version(deposit)


    A damona registry looks like::

        ivar:
          doi: 10.5281/zenodo.8033025
          zenodo_id: 8033026
          releases:
            1.3.1:
              download: https://zenodo.org/record/8033026/files/ivar_1.3.1.img
              md5sum: 213e286c708e12d6423b0bd8fa723327
              doi: 10.5281/zenodo.8033026
              filesize: 139108352

    This is created when using::

        damona publish file.img --mode zenodo

    The zenodo_id is the record on the main page. e.g https://zenodo.org/records/8033026
    To cite all versions, use the main doi (here 10.5281/zenodo.8033025).

    Each release has its own DOI in case you want to cite a specific version.

    """

    def __init__(self, mode="sandbox.zenodo", token=None, author=None, affiliation=None, orcid=None):
        assert mode in ["zenodo", "sandbox.zenodo"]
        self.mode = mode
        self.last_requests = []

        cfg = Config()

        if token is None:
            try:
                self.token = cfg.config.get(f"{mode}", "token")
                logger.info(f"Found token for {mode} in {cfg.config_file}")
            except (NoSectionError, NoOptionError):
                logger.error("A token must be provided on command line or in your damona.cfg file")
                sys.exit(1)
        else:
            self.token = token

        # Do we have an orcid (optional)
        self.orcid = None
        if orcid is None:
            try:
                self.orcid = cfg.config.get(f"{mode}", "orcid")
                logger.info(f"Found ORCID for {mode} in {cfg.config_file}")
            except (NoSectionError, NoOptionError):
                pass
        else:
            self.orcid = orcid

        if self.orcid:
            self.orcid = (
                self.orcid.replace("https://orcid.org/", "").replace("http://orcid.org/", "").strip("/").strip()
            )
            import re

            if not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", self.orcid):
                logger.error(f"ORCID '{self.orcid}' does not match the expected format XXXX-XXXX-XXXX-XXXX")
                sys.exit(1)

        # Do we have a name ?
        if author is None:
            try:
                self.author = cfg.config.get(f"{mode}", "name").replace("'", "").replace('"', "")
                logger.info(f"Found Name {self.author} for {mode} in {cfg.config_file}")
            except (NoSectionError, NoOptionError):
                pass
        else:
            self.author = author

        # Do we have an affiliation ?
        if affiliation is None:
            try:
                self.affiliation = cfg.config.get(f"{mode}", "affiliation").replace("'", "").replace('"', "")
                logger.info(f"Found Affiliation {self.affiliation} for {mode} in {cfg.config_file}")
            except (NoSectionError, NoOptionError):
                pass
        else:
            self.affiliation = affiliation

        if self.affiliation is None or self.author is None:
            logger.error("you must provide an author and affiliation")
            sys.exit(1)

    def _get_headers(self):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}

    headers = property(_get_headers)

    def _status(self, r, correct_codes):
        try:
            caller = inspect.stack()[1].function
        except:
            caller = ""

        self.last_requests.append(r)

        if r.status_code not in correct_codes:
            logger.warning(f"Status code: {r.status_code}; {r.reason}")
            try:
                output = f"{r.json()}"
                logger.warning(output)
            except:
                logger.warning("Could not figure out the erorr from json()")
            finally:

                logger.error(f"unexpected return code {r.status_code}")
                logger.error(f"Caller: {caller}")
                logger.error("Know issues:\n - Have you set a token in zenodo and provide the token in damona.cfg ? ")
                sys.exit(1)

    def create_new_deposition(self):  # pragma: no cover
        # expected status is 201

        logger.info("Creating a new deposit")
        url = f"https://{self.mode}.org/api/deposit/depositions"
        r = requests.post(url, json={}, headers=self.headers)
        self._status(r, [201])

        try:
            ID = self.last_requests[-1].json()["id"]
            logger.info(f"Created a new deposit with ID={ID}")
        except:
            raise
        return r

    def get_all_depositions(self):  # pragma: no cover
        """Return all depositions for the currently authenticated user"""
        url = f"https://{self.mode}.org/api/deposit/depositions"
        r = requests.get(url, json={}, headers=self.headers)
        self._status(r, [200])
        return r

    def get_deposition(self, ID):  # pragma: no cover
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}"
        r = requests.get(url, json={}, headers=self.headers)
        self._status(r, [200])
        return r

    def delete_deposition(self, ID):  # pragma: no cover
        """only unpublished deposit can be deleted.

        Normal status code is 204. If already deleted, sent 401
        """
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}"
        r = requests.delete(url, json={}, headers=self.headers)
        self._status(r, [201])
        return r

    def upload(self, filename, json_deposit):  # pragma: no cover
        logger.info("Uploading file")

        try:
            bucket_url = json_deposit["links"]["bucket"]
        except:
            bucket_url = json_deposit.json()["links"]["bucket"]

        jsons = {}

        # Determine the total size of the file
        total_size = os.path.getsize(filename)

        # the upload it self may take a while
        with open(filename, "rb") as fp:
            basename = os.path.basename(filename)

            with tqdm(total=total_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
                wrapped_file = CallbackIOWrapper(t.update, fp, "read")
                r = requests.put(
                    f"{bucket_url}/{basename}", data=wrapped_file, headers={"Authorization": f"Bearer {self.token}"}
                )

            self._status(r, [200, 201])
            return r

    def get_metadata(self, software, version):
        # check validity of the version
        assert len(version.split(".")) == 3
        items = version.split(".")
        if items[0][0] != "v":
            version = f"v{version}"

        data = {
            "metadata": {
                "title": f"Damona singularity image of {software} software",
                "upload_type": "physicalobject",
                "description": f"""Singularity image(s) of {software} software to be used and installed with damona
(<a href="https://damona.readthedocs.org">See https://damona.readthedocs.org</a>) for reproducible bioinformatics
analysis.""",
                "keywords": ["apptainer", "singularity", "damona", "bioinformatics", "reproducibility", "container"],
                "version": f"{version}",
                "communities": [{"identifier": "damona"}],
            }
        }

        if self.orcid:
            data["metadata"]["creators"] = [{"orcid": self.orcid, "name": self.author, "affiliation": self.affiliation}]
        else:
            data["metadata"]["creators"] = [{"name": self.author, "affiliation": self.affiliation}]

        return data

    def update_metadata(self, data, deposit):  # pragma: no cover
        logger.info("Uploading metadata")
        ID = self.get_id(deposit)
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}"
        r = requests.put(url, data=json.dumps(data), headers=self.headers)
        self._status(r, [200])
        return r

    def publish(self, deposit):  # pragma: no cover
        ID = self.get_id(deposit)
        logger.info(f"Publishing {ID}")
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}/actions/publish"
        r = requests.post(url, headers=self.headers)
        self._status(r, [202, 504])
        return r

    def unlock(self, deposit):  # pragma: no cover
        ID = self.get_id(deposit)
        logger.info(f"Unlocking {ID}")
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}/actions/edit"
        r = requests.post(url, headers=self.headers)
        self._status(r, [201, 403])
        return r

    def create_new_deposit_version(self, deposit):  # pragma: no cover
        # expected status 201
        logger.info(f"Creating a new version for record {deposit}. Please wait")
        ID = self.get_id(deposit)
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}/actions/newversion"
        r = requests.post(url, headers=self.headers)
        if r.status_code == 403:
            logger.error(
                f"403 on newversion for record {ID}. Common cause: an unpublished draft already exists. "
                f"Go to https://{self.mode}.org/me/uploads and discard any pending draft for this record, then retry."
            )
            sys.exit(1)
        self._status(r, [201])
        return r

    def get_id(self, data):
        """
        data can be the output of a requests, in which case, we call to_json() and expect a 'id'
        key. Otherwise, it is alrady a json structure. If none works, most probably just an ID (integer).
        """
        try:
            return data.json()["id"]
        except:
            try:
                return data["id"]
            except:
                return data

    def _get_registry(self):
        if self.mode == "zenodo":
            return "registry.yaml"
        elif self.mode == "sandbox.zenodo":
            return "registry_sandbox.yaml"

    registry_name = property(_get_registry)

    def _comment_out_release(self, registry_file, version):
        """Comment out an existing release block for *version* in *registry_file*.

        Returns the ``extra_binaries`` value found in the block (or ``None``).
        The file is rewritten in place with the matching lines prefixed by ``# ``.
        """
        if not os.path.exists(registry_file):
            return None

        with open(registry_file, "r") as f:
            lines = f.readlines()

        # Locate the uncommented version line at 4-space indent: "    X.Y.Z:"
        start_idx = None
        for i, line in enumerate(lines):
            if line.startswith(f"    {version}:") and not line.lstrip().startswith("#"):
                start_idx = i
                break

        if start_idx is None:
            return None

        # Collect sub-entries: lines with indent > 4 that immediately follow
        extra_binaries = None
        end_idx = start_idx + 1
        while end_idx < len(lines):
            line = lines[end_idx]
            if not line.strip():
                break
            indent = len(line) - len(line.lstrip())
            if indent <= 4:
                break
            if "extra_binaries:" in line:
                extra_binaries = line.split("extra_binaries:", 1)[1].strip()
            end_idx += 1

        # Prefix each non-blank line in the block with "# "
        for i in range(start_idx, end_idx):
            if lines[i].strip():
                lines[i] = "# " + lines[i]

        with open(registry_file, "w") as f:
            f.writelines(lines)

        logger.warning(f"Existing {version} entry commented out in {registry_file}")
        return extra_binaries

    def _is_known_locally(self, registry_file, software_name):
        """Return True if *software_name* already has an entry in *registry_file*."""
        if not os.path.exists(registry_file):
            return False
        with open(registry_file, "r") as f:
            for line in f:
                if line.startswith(f"{software_name}:") and not line.lstrip().startswith("#"):
                    return True
        return False

    def _upload(self, filename, binaries=None, extra_binaries=None):
        data = ImageName(filename)
        software = Software(data.name)

        # known_in_registry: software exists in the installed damona registry (production only)
        known_in_registry = bool(software.name) and self.mode != "sandbox.zenodo"
        # known_locally: software already has an entry in the local output file (both modes)
        known_locally = self._is_known_locally(self.registry_name, data.name)
        # known: drives YAML structure (release-only block vs full entry) and append vs overwrite
        known = known_in_registry or known_locally

        # Always create a new independent deposit. Zenodo records are owned by
        # whoever created them, so attempting newversion on someone else's record
        # always fails with 403. Each version gets its own record instead.
        if known:
            logger.info("Software known, creating new independent deposit for this version.")

            # If this version already exists locally, comment it out and reuse extra_binaries
            old_extra = self._comment_out_release(self.registry_name, data.version)
            if old_extra is not None:
                click.echo(
                    f"Version {data.version} was already present in {self.registry_name} — old entry commented out."
                )

            # Warn if the global binaries field is empty (only meaningful for installed registry)
            if known_in_registry:
                current_binaries = software._data.get(data.name, {}).get("binaries", "")
                if not current_binaries:
                    click.echo(
                        f"WARNING: 'binaries' field is currently empty for '{data.name}' in the registry. "
                        "Remember to add it manually."
                    )

            if extra_binaries is None:
                default = old_extra or ""
                prompt = "Extra binaries for this release (space or comma separated, empty to skip)"
                if default:
                    prompt += f" [previous value: {default}]"
                raw = click.prompt(prompt, default=default)
                extra_binaries = raw.strip() or None
        else:
            logger.info("Software not known, creating new deposit.")

            if binaries is None:
                raw = click.prompt(
                    f"Binary names for '{data.name}' (space or comma separated)",
                    default=data.name,
                )
                binaries = raw.strip() or data.name

        msg = self.create_new_deposit_with_file_and_publish(
            filename, known=known, binaries=binaries, extra_binaries=extra_binaries
        )
        with open(self.registry_name, "a+" if known else "w") as fout:
            fout.write(msg)

        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        body = (
            f"[bold green]Image published successfully.[/bold green]\n\n"
            f"1. Review and edit [bold]{self.registry_name}[/bold] if needed.\n"
            f"2. Commit the registry and the image recipe:\n\n"
            f"   [bold]git add {self.registry_name}[/bold]\n"
            f"   [bold]git commit -m 'add {data.name} {data.version}'[/bold]\n\n"
            f"3. Open a pull request to merge your changes."
        )
        console.print(Panel(body, title="[bold cyan]damona publish — done[/bold cyan]", expand=False))

    def create_new_deposit_with_file_and_publish(
        self, filename, known=False, binaries=None, extra_binaries=None
    ):  # pragma: no cover
        """ """
        data = ImageName(filename)

        logger.info(f"Creating and Publising new deposit for {data.name}_{data.version}")
        deposit = self.create_new_deposition()

        up = self.upload(filename, deposit)
        metadata = self.get_metadata(data.name, data.version)
        self.update_metadata(metadata, deposit)

        # in order to obtain the DOI, we must publish first
        self.publish(deposit)

        if self.last_requests[-1].ok:
            json = self.last_requests[-1].json()
            msg = self._print_info_new_deposit(
                data, json, known=known, binaries=binaries, extra_binaries=extra_binaries
            )
            return msg

    def _print_info_new_deposit(self, data, json, known=False, binaries=None, extra_binaries=None):
        # figure out the filename entry we have just added
        entry = [x for x in json["files"] if x["filename"] == data.basename][0]

        zenodo_id = json["id"]
        doi = json["conceptdoi"]
        this_doi = json["doi"]
        record_html = json["links"]["record_html"]
        md5sum = entry["checksum"]
        filesize = entry["filesize"]
        basename = entry["filename"]

        if known:
            # Software already has a registry entry. Output only the new release
            # block and remind the developer to update the top-level zenodo_id.
            msg = f"    {data.version}:\n"
            msg += f"      download: {record_html}/files/{basename}\n"
            msg += f"      md5sum: {md5sum}\n"
            msg += f"      doi: {this_doi}\n"
            msg += f"      filesize: {filesize}\n"
            if extra_binaries:
                msg += f"      extra_binaries: {extra_binaries}\n"
        else:
            msg = f"{data.name}:\n"
            if binaries:
                msg += f"  binaries: {binaries}\n"
            msg += "  releases:\n"
            msg += f"    {data.version}:\n"
            msg += f"      download: {record_html}/files/{basename}\n"
            msg += f"      md5sum: {md5sum}\n"
            msg += f"      doi: {this_doi}\n"
            msg += f"      filesize: {filesize}\n"
        return msg

    def create_new_version_with_file_and_publish(self, filename, deposit=None):
        data = ImageName(filename)
        registry_data = Software(data.name)._data
        try:
            zenodo_id = registry_data[data.name]["zenodo_id"]
        except KeyError:
            logger.critical(
                f"Could not find {data.name} in the registry. Filename must have the same name as those to be found in the recipes."
            )
            sys.exit(1)

        logger.info(f"Creating and Publising new version for {data.name}_{data.version}")

        deposit = self.create_new_deposit_version(zenodo_id)

        # switch the state from 'done' to 'inprogress'
        self.unlock(deposit)

        # get the ID of the new latest draft and its deposition
        new_ID = deposit.json()["links"]["latest_draft"].split("/")[-1]
        new_deposit = self.get_deposition(new_ID)

        up = self.upload(filename, new_deposit.json())

        metadata = self.get_metadata(data.name, data.version)
        self.update_metadata(metadata, new_deposit)

        self.publish(new_ID)

        if self.last_requests[-1].ok:
            json = self.last_requests[-1].json()
            msg = self._print_info_new_version(data, json)
            return msg

    def _print_info_new_version(self, data, json):
        # figure out the filename entryy we have just added
        entry = [x for x in json["files"] if x["filename"] == data.basename][0]

        # update the new zenodo ID

        this_doi = json["doi"]
        md5sum = entry["checksum"]
        basename = entry["filename"]
        record_html = json["links"]["record_html"]
        filesize = entry["filesize"]

        msg = f"    {data.version}:\n"
        msg += f"      download: {record_html}/files/{basename}\n"
        msg += f"      md5sum: {md5sum}\n"
        msg += f"      doi: {this_doi}\n"
        msg += f"      filesize: {filesize}"  # no EOF
        return msg


def get_stats_software(software):
    """Returns total number of downloads across all releases."""
    from damona.registry import Software

    s = Software(software)
    counts = []
    for release in getattr(s, "releases", {}).values():
        if release.doi and "zenodo" in release.doi:
            record_id = release.doi.split("zenodo.")[-1]
            n = get_stats_id(record_id, software)
            if isinstance(n, int) and n >= 0:
                counts.append(n)
    # Old-style versioned records all return the same all_versions total,
    # so deduplicating avoids multiplying the concept count by N releases.
    # New-style independent deposits each have a unique count, so the set
    # preserves them all and the sum is correct.
    return sum(set(counts))


def get_stats_id(ID, name=None):
    """Returns number of downloads


    For instance, for this link: https://zenodo.org/record/7319782
    you should provide the ID 7319782


    """
    import json

    from bs4 import BeautifulSoup

    if ID == "bioconainers":
        return 0
    elif ID is None:
        print(f"# ID {ID} is unknown for {name}. developers should update registry")
        return 0
    else:

        r = requests.get(f"https://zenodo.org/record/{ID}")
        bs = BeautifulSoup(r.content, features="html.parser")

        # according to damona, there is a limit of 60 requests per minute but also
        # 2000 requests per hour. Since there are more than 60 software, we expect
        # this call to reach the limit. Therefore, we introspect the X-RateLimit
        # and Number of requests remaining and add a sleep.
        import time

        R = int(r.headers["X-RateLimit-Remaining"])
        L = int(r.headers["X-RateLimit-Limit"])
        reset = int(r.headers["X-RateLimit-Reset"])
        T = int(time.time())
        if int(r.headers["X-RateLimit-Remaining"]) < 1:

            delay = reset - int(time.time())
            logger.warning(f"Warning limit attained. please wait {delay}")
            time.sleep(delay)

        try:
            data = bs.find(id="recordVersions")
            data = json.loads(data.attrs["data-record"])["stats"]["all_versions"]["downloads"]
            return data
        except Exception as err:
            print(err)
            print(ID)
            print("====")
            return -1
