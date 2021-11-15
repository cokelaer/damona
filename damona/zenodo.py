import requests
import os
import json


import colorlog
logger = colorlog.getLogger(__name__)


logger.setLevel("INFO")


class Zenodo:
    """

    ::

        z = Zenodo(mode="sandbox.zenodo")

    You can retrieve an existing deposit (read-only) given its ID:

        deposit = z.get_deposition(959590)

    Or start with a new one

        deposit = z.create_new_deposition()


    If you want to create a new file deposition and publish it, follow those 4 commands::

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

    4. publish  NOTE THAT PUBLISHED DEPOSITION CANNOT BE MODIFIED NOT DELETED::

        published = z.publish(deposit)

    # if we want an update, we must create a new version from a published deposit

        new_version = z.create_new_deposit_version(deposit)


    """

    def __init__(self, mode, token):

        assert mode in ['zenodo', 'sandbox.zenodo']
        self.mode = mode
        self.token = token
        self.headers = {"Content-Type": "application/json"}
        self.last_requests = []

    def _get_params(self):
        return {'access_token': self.token}
    params = property(_get_params)

    def _info(self): #pragma: no cover
        print(f"Status code: {self.last_requests[-1].status_code}")

    def create_new_deposition(self): # pragma: no cover
        # expected status is 201

        logger.info("Creating a new deposit")
        url = f'https://{self.mode}.org/api/deposit/depositions'
        r = requests.post(url, params=self.params, json={}, headers=self.headers)
        #if self.last_requests[-1].status_code not in [201]:
        #    print(f"unexpected status code. {r.json()}")
        self.last_requests.append(r)
        self._info()
        try:
            ID = self.last_requests.json()['id']
            logger.info(f"Created a new deposit with ID={ID}")
        except:
            pass
        return r

    def get_all_depositions(self): # pragma: no cover
        """Return all deposition for the currently authenticated user"""
        url = f'https://{self.mode}.org/api/deposit/depositions'
        r = requests.get(url, params=self.params, json={})
        self.last_requests.append(r)
        self._info()
        return r

    def get_deposition(self, ID): #pragma: no cover
        # expcted status code: 200

        url = f'https://{self.mode}.org/api/deposit/depositions/{ID}'
        r = requests.get(url, params=self.params, json={})
        self.last_requests.append(r)
        self._info()
        return r

    def delete_deposition(self, ID): # pragma: no cover
        """only unpublished deposit can be deleted. 

        Normal status code is 204. If already deleted, sent 401
        """
        url = f'https://{self.mode}.org/api/deposit/depositions/{ID}'
        r = requests.delete(url, params=self.params, json={})
        self.last_requests.append(r)
        self._info()
        return r

    def upload(self, filename, json_deposit): # pragma: no cover


        print(json_deposit)

        try:
            bucket_url = json_deposit['links']['bucket']
        except:
            bucket_url = json_deposit.json()['links']['bucket']

        jsons = {}

        logger.info("Uploading file")
        # the upload it self may take a while
        with open(filename, 'rb') as fp:
            basename = os.path.basename(filename)
            r = requests.put(f"{bucket_url}/{basename}", data=fp, params=self.params)
        self.last_requests.append(r)
        self._info()
        return r

    def get_metadata(self, software, version): 
        # check validity of the version
        assert len(version.split(".")) == 3
        items = version.split(".")
        if items[0][0]!= 'v':
            version = f"v{version}"

        data = {'metadata':
                {
                    'title' : f'Singularity image of {software} software',
                    'upload_type': 'physicalobject',
                    'description': f"""Singularity image(s) of {software} software to be used and installed with damona
(<a href="https://damona.readthedocs.org">See https://damona.readthedocs.org</a>) for reproducible bioinformatics
analysis.""",
                    'creators': [{'name':  'Cokelaer, Thomas', 'affiliation': 'Institut Pasteur'}],
                    'keywords': ['singularity', 'damona', 'bioinformatics',
                                'reproducibility', 'container'],
                    'version':f'{version}'
                }
            }

        return data

    def update_metadata(self, data, deposit): #pragma: no cover
        logger.info("Uploading metadata")
        ID = self.get_id(deposit)
        url = f'https://{self.mode}.org/api/deposit/depositions/{ID}'
        r = requests.put(url, params=self.params, data=json.dumps(data), headers=self.headers)
        self.last_requests.append(r)
        self._info()
        return r

    def publish(self, deposit): #pragma: no cover
        ID = self.get_id(deposit)
        logger.info(f"Publishing {ID}")
        url = f'https://{self.mode}.org/api/deposit/depositions/{ID}/actions/publish'
        r = requests.post(url, params=self.params)
        self.last_requests.append(r)
        self._info()
        return r

    def unlock(self, deposit): #pragma: no cover
        ID = self.get_id(deposit)
        logger.info(f"Unlocking {ID}. Expecting code 201. 403 means already unlocked.")
        url = f'https://{self.mode}.org/api/deposit/depositions/{ID}/actions/edit'
        r = requests.post(url, params=self.params)
        self.last_requests.append(r)
        self._info()
        return r

    def create_new_deposit_version(self, deposit): #pragma: no cover
        # expected status 201
        logger.info("Create a new version. Expecting status code 201")
        ID = self.get_id(deposit)
        url = f'https://{self.mode}.org/api/deposit/depositions/{ID}/actions/newversion'
        r  = requests.post(url, params=self.params)
        self.last_requests.append(r)
        self._info()
        return r

    def get_id(self, data):
        """
        data can be the output of a requests, in which case, we call to_json() and expect a 'id'
        key. Otherwise, it is alrady a json structure. If none works, most probably just an ID (integer).
        """
        try:
            return data.json()['id']
        except:
            try:
                return data['id']
            except:
                return data

    def create_new_deposit_with_file_and_publish(self, filename): #pragma: no cover
        """

        """
        from damona.registry import ImageName
        data = ImageName(filename)

        logger.info(f"Creating and Publising new deposit for {data.name}_{data.version}")
        deposit = self.create_new_deposition()

        up = self.upload(filename, deposit)
        metadata = self.get_metadata(data.name, data.version)
        self.update_metadata(metadata, deposit)


        self.publish(deposit)

        json = self.last_requests[-1].json()
        self._to_registry(json)


    def create_new_version_with_file_and_publish(self, filename, deposit):

        data = ImageName(filename)

        #basename = os.path.basename(filename)
        #software, version = basename.rsplit(".", 1)[0].rsplit("_", 1)
        logger.info(f"Creating and Publising new version for {data.name}_{data.version}")
        deposit = self.create_new_deposit_version(deposit)

        # switch the state from 'done' to 'inprogress'
        self.unlock(deposit)

        # get the ID of the new latest draft
        new_ID = deposit.json()['links']['latest_draft'].split("/")[-1]
        new_deposit = self.get_deposition(new_ID)

        up = self.upload(filename, new_deposit.json())

        metadata = self.get_metadata(data.name, data.version)
        self.update_metadata(metadata, new_deposit)

        json = self.last_requests[-1].json()
        self._to_registry(json)

        self.publish(deposit)


    def deposit2registry(self, ID):

        deposit = self.get_deposition(ID)
        self._to_registry(deposit)

    def _to_registry(self, json):
        try:
            json = json.json()
        except:
            pass
        files = json['files']
        zenodo_id = json['id']
        doi = json['conceptdoi']
        print(f"  doi: {doi}")
        print(f"  current_zenodo_id: {zenodo_id}")
        print("  releases:")
        for entry in files:
            download = entry['links']['download']
            md5sum = entry['checksum']
            basename = entry['filename']
            software, version = basename.rsplit(".", 1)[0].rsplit("_", 1)
            print(f"    {version}:")
            print(f"      download: {download}:")
            print(f"      md5sum: {md5sum}")


