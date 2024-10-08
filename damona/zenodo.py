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

from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

import colorlog
import requests

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

        damona zenodo-upload file.img --mode zenodo

    The zenodo_id is the record on the main page. e.g https://zenodo.org/records/8033026
    To cite all versions, use the main doi (here 10.5281/zenodo.8033025).

    Each release has its own DOI in case you want to cite a specific version.

    """

    def __init__(self, mode="sandbox.zenodo", token=None, author=None, affiliation=None, orcid=None):
        assert mode in ["zenodo", "sandbox.zenodo"]
        self.mode = mode
        self.headers = {"Content-Type": "application/json"}
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
        if orcid is None:
            try:
                self.orcid = cfg.config.get(f"{mode}", "orcid")
                logger.info(f"Found ORCID for {mode} in {cfg.config_file}")
            except (NoSectionError, NoOptionError):
                pass
        else:
            self.orcid = orcid

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

    def _get_params(self):
        return {"access_token": self.token}

    params = property(_get_params)

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
        r = requests.post(url, params=self.params, json={}, headers=self.headers)
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
        r = requests.get(url, params=self.params, json={})
        self._status(r, [200])
        return r

    def get_deposition(self, ID):  # pragma: no cover
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}"
        r = requests.get(url, params=self.params, json={})
        self._status(r, [200])
        return r

    def delete_deposition(self, ID):  # pragma: no cover
        """only unpublished deposit can be deleted.

        Normal status code is 204. If already deleted, sent 401
        """
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}"
        r = requests.delete(url, params=self.params, json={})
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
                r = requests.put(f"{bucket_url}/{basename}", data=wrapped_file, params=self.params)


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
        r = requests.put(url, params=self.params, data=json.dumps(data), headers=self.headers)
        self._status(r, [200])
        return r

    def publish(self, deposit):  # pragma: no cover
        ID = self.get_id(deposit)
        logger.info(f"Publishing {ID}")
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}/actions/publish"
        r = requests.post(url, params=self.params, headers=self.headers)
        self._status(r, [202, 504])
        return r

    def unlock(self, deposit):  # pragma: no cover
        ID = self.get_id(deposit)
        logger.info(f"Unlocking {ID}")
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}/actions/edit"
        r = requests.post(url, params=self.params)
        self._status(r, [201, 403])
        return r

    def create_new_deposit_version(self, deposit):  # pragma: no cover
        # expected status 201
        logger.info(f"Creating a new version for record {deposit}. Please wait")
        ID = self.get_id(deposit)
        url = f"https://{self.mode}.org/api/deposit/depositions/{ID}/actions/newversion"
        r = requests.post(url, params=self.params)
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

    def _upload(self, filename):
        data = ImageName(filename)
        software = Software(data.name)

        # sandbox has no registry in general, so no name, therefore we create
        # a new deposit.
        if software.name and self.mode != "sandbox.zenodo":
            logger.info("Software known, adding new version.")
            msg = self.create_new_version_with_file_and_publish(filename)
            print(msg)
            with open(self.registry_name, "a+") as fout:
                fout.write(msg)
        else:
            logger.info("Software not known, adding new deposit.")
            msg = self.create_new_deposit_with_file_and_publish(filename)
            print(msg)
            with open(self.registry_name, "w") as fout:
                fout.write(msg)

    def create_new_deposit_with_file_and_publish(self, filename):  # pragma: no cover
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
            msg = self._print_info_new_deposit(data, json)
            return msg

    def _print_info_new_deposit(self, data, json):
        # figure out the filename entryy we have just added
        entry = [x for x in json["files"] if x["filename"] == data.basename][0]

        zenodo_id = json["id"]
        doi = json["conceptdoi"]
        msg = f"{data.name}:\n"
        msg += f"  doi: {doi}\n"
        msg += f"  zenodo_id: {zenodo_id}\n"
        msg += "  releases:\n"

        this_doi = json["doi"]
        record_html = json["links"]["record_html"]

        md5sum = entry["checksum"]
        filesize = entry["filesize"]
        basename = entry["filename"]
        msg += f"    {data.version}:\n"
        msg += f"      download: {record_html}/files/{basename}\n"
        msg += f"      md5sum: {md5sum}\n"
        msg += f"      doi: {this_doi}\n"
        msg += f"      filesize: {filesize}\n"  # no EOF
        return msg

    def create_new_version_with_file_and_publish(self, filename, deposit=None):
        data = ImageName(filename)
        registry_data = Software(data.name)._data
        try:
            import pdb
            pdb.set_trace()
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
    """Returns number of downloads"""
    from damona.registry import Software

    s = Software(software)
    try:
        return get_stats_id(s.zenodo_id, software)
    except AttributeError:
        return 0


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
        R = int(r.headers['X-RateLimit-Remaining'])
        L = int(r.headers['X-RateLimit-Limit'])
        reset = int(r.headers['X-RateLimit-Reset'])
        T = int(time.time())
        if int(r.headers['X-RateLimit-Remaining']) < 1:

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
