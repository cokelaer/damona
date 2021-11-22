import damona
from damona import zenodo

from . import test_dir


deposit = {
    "conceptdoi": "10.5072/zenodo.960007",
    "conceptrecid": "960007",
    "created": "2021-11-13T20:15:42.926938+00:00",
    "doi": "10.5072/zenodo.960008",
    "doi_url": "https://doi.org/10.5072/zenodo.960008",
    "files": [
        {
            "checksum": "4949d8da803d970e74de7ce898ed3c6b",
            "filename": "art_2.5.8.img",
            "filesize": 339525632,
            "id": "de1a2781-7d3f-4322-97d4-52fcd9df29c0",
            "links": {
                "download": "https://sandbox.zenodo.org/api/files/7b677fd2-2722-4f17-a270-3cef204f9858/art_2.5.8.img",
                "self": "https://sandbox.zenodo.org/api/deposit/depositions/960008/files/de1a2781-7d3f-4322-97d4-52fcd9df29c0",
            },
        }
    ],
    "id": 960008,
    "links": {
        "badge": "https://sandbox.zenodo.org/badge/doi/10.5072/zenodo.960008.svg",
        "bucket": "https://sandbox.zenodo.org/api/files/7b677fd2-2722-4f17-a270-3cef204f9858",
        "conceptbadge": "https://sandbox.zenodo.org/badge/doi/10.5072/zenodo.960007.svg",
        "conceptdoi": "https://doi.org/10.5072/zenodo.960007",
        "doi": "https://doi.org/10.5072/zenodo.960008",
        "latest": "https://sandbox.zenodo.org/api/records/960008",
        "latest_html": "https://sandbox.zenodo.org/record/960008",
        "record": "https://sandbox.zenodo.org/api/records/960008",
        "record_html": "https://sandbox.zenodo.org/record/960008",
    },
    "metadata": {
        "access_right": "open",
        "communities": [{"identifier": "zenodo"}],
        "creators": [{"affiliation": "Institut Pasteur", "name": "Cokelaer, Thomas"}],
        "description": 'Singularity image(s) of art software to be used and installed with damona\n(<a href="https://damona.readthedocs.org">See https://damona.readthedocs.org</a>) for reproducible bioinformatics\nanalysis.',
        "doi": "10.5072/zenodo.960008",
        "keywords": ["singularity", "damona", "bioinformatics", "reproducibility", "container"],
        "license": "CC-BY-4.0",
        "prereserve_doi": {"doi": "10.5072/zenodo.960008", "recid": 960008},
        "publication_date": "2021-11-13",
        "title": "Singularity image of art software",
        "upload_type": "physicalobject",
        "version": "v2.5.8",
    },
    "modified": "2021-11-13T20:22:57.340141+00:00",
    "owner": 18543,
    "record_id": 960008,
    "state": "done",
    "submitted": True,
    "title": "Singularity image of art software",
}




def test(mocker):

    mocker.patch("damona.zenodo.Zenodo.create_new_deposition", return_values={})

    try:
        z = zenodo.Zenodo("sandbox.zenodo")
    except:
        SystemExit

    z = zenodo.Zenodo("sandbox.zenodo", token="dummy", affiliation="dummy", author="dummy")
    z.params

    # z._to_registry(deposit)
    #data1 = z.get_metadata("fastqc", "v0.1.1")
    #data2 = z.get_metadata("fastqc", "0.1.1")
    #assert data1 == data2

    z.get_id(deposit)
