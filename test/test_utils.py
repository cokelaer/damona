from damona.utils import download_with_progress





def test_download(tmpdir):

    directory = tmpdir.mkdir("images")
    destination = directory / "test_1.0.0.img"
    download_with_progress("https://zenodo.org/record/7817800/files/minimap2_2.24.0.img", destination)
