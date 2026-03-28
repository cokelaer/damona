###########################################################################
# Damona is a project to manage reproducible containers                   #
#                                                                         #
# Authors: see CONTRIBUTORS.rst                                           #
# Copyright © 2020-2021  Institut Pasteur, Paris and CNRS.                #
# See the COPYRIGHT file for details                                      #
#                                                                         #
# Damona is free software: you can redistribute it and/or modify          #
# it under the terms of the GNU General Public License as published by    #
# the Free Software Foundation, either version 3 of the License, or       #
# (at your option) any later version.                                     #
#                                                                         #
# Damona  is distributed in the hope that it will be useful,              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of          #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
# GNU General Public License for more details.                            #
#                                                                         #
# You should have received a copy of the GNU General Public License       #
# along with this program (COPYING file).                                 #
# If not, see <http://www.gnu.org/licenses/>.                             #
###########################################################################
""".. rubric:: Standalone application dedicated to Damona"""
import functools
import os
import pathlib
import subprocess
import sys
import time

import click
import click_completion
import packaging
import requests
import rich_click as click
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

click_completion.init()


URL = "https://raw.githubusercontent.com/cokelaer/damona/refs/heads/main/damona/software/registry.yaml"

from damona import Damona, Environ, Environment, version
from damona.common import BinaryReader, ImageReader, get_container_cmd, get_damona_path
from damona.install import (
    BiocontainersInstaller,
    LocalImageInstaller,
    RemoteImageInstaller,
)
from damona.registry import BiocontainersRegistry, Registry

click.rich_click.TEXT_MARKUP = "markdown"
click.rich_click.OPTIONS_TABLE_COLUMN_TYPES = ["required", "opt_short", "opt_long", "help"]
click.rich_click.OPTIONS_TABLE_HELP_SECTIONS = ["help", "deprecated", "envvar", "default", "required", "metavar"]
click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.COMMAND_GROUPS = {
    "damona": [
        {
            "name": "Environment management",
            "commands": ["create", "remove", "rename", "env", "activate", "deactivate"],
        },
        {
            "name": "Package management",
            "commands": ["install", "uninstall", "clean", "export", "info"],
        },
        {
            "name": "Registry",
            "commands": ["search", "list", "stats"],
        },
        {
            "name": "Developer tools",
            "commands": ["check", "build", "catalog"],
        },
    ]
}

# manager = Damona()
def url_exists(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


__all__ = ["main", "build"]

from damona import logger

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def common_logger(func):
    @click.option(
        "--log-level",
        default="INFO",
        type=click.Choice(["INFO", "DEBUG", "WARNING", "CRITICAL", "ERROR"]),
        help="Set the logging level.",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from damona import logger

        logger.remove()
        logger.add(
            sys.stderr,
            level=kwargs.get("log_level", "INFO"),
            format="<green>{time}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
        )
        return func(*args, **kwargs)

    return wrapper


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=version)
def main():
    """Damona is an environment manager for singularity containers.

    It is to singularity container what conda is to packaging.

    The default environment is called 'base'. You can create and activate
    a new environment as follows:

        damona create --name TEST
        damona activate TEST

    Once an environment is activated, you can install a Damona-registered image
    (and its registered binaries):

        damona install fastqc:0.11.9

    More information on https://damona.readthedocs.io.
    Please report issues on https://github.com/cokelaer/damona
    Contact: Thomas Cokelaer at pasteur dot fr

    "Make everything as simple as possible, but not simpler." -- Albert Einstein
    """
    ######################## !!!!!!!!!!!! ####################
    # this function cannot print anything because the damona
    # activate command prints bash commands read by damona.sh
    ######################## !!!!!!!!!!!! ####################
    pass


@main.command()
@click.argument("environment", required=True, type=click.STRING)
@click.option("--from-bundle", type=click.STRING, help="A bundle file created with 'damona export --bundle'.")
@click.option("--from-yaml", type=click.STRING, help="A YAML file created with 'damona export --yaml'.")
@click.option(
    "--force",
    is_flag=True,
    help="When restoring from a bundle or YAML, overwrite existing binaries and images.",
)
@common_logger
def create(**kwargs):
    """Create a new environment

    Here we create an environment called TEST:

        damona create TEST

    You can then activate it:

        damona activate TEST

    You can create an environment from a environment.yaml file that was created with the 'export --yaml' command
    or manually built using the following syntax:


        name: sequana_rnaseq

        images:
            - sequana_tools_0.14.5.img

        binaries:
            - bwa
            - samtools
            - bamtools

    """
    envs = Environ()
    if kwargs["from_bundle"]:
        envs.create_from_bundle(kwargs["environment"], bundle=kwargs["from_bundle"], force=kwargs["force"])
    elif kwargs["from_yaml"]:
        envs.create_from_yaml(kwargs["environment"], yaml=kwargs["from_yaml"], force=kwargs["force"])
    else:
        envs.create(kwargs["environment"])


@main.command()
@click.argument("environment", required=True, type=click.STRING)
@click.option("--force", is_flag=True, help="Remove without asking for confirmation.")
@common_logger
def remove(**kwargs):
    """Remove an environment and all its binaries.

    Remove the environment named TEST:

        damona remove TEST

    To remove a package (binary + image) from the active environment, use:

        damona uninstall fastqc

    """
    env = Environ()
    env.delete(kwargs["environment"], force=kwargs["force"])


@main.command()
@click.argument("environment", required=True, type=click.STRING)
@click.option("--new-name", required=True, type=click.STRING, help="New name for the environment.")
@common_logger
def rename(**kwargs):
    """Rename an existing environment."""
    env = Environment(kwargs["environment"])
    env.rename(kwargs["new_name"])


# =================================================================== env
@main.command()
@common_logger
def env(**kwargs):
    """List all environments with their size and binary counts.

    Print information about current environments:

        damona env

    The currently active environment is marked with a checkmark.
    """
    envs = Environ()
    console = Console()

    table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
    table.add_column("Environment", style="bold", min_width=20)
    table.add_column("Info")

    current_env = envs.get_current_env_name()
    if envs.N != 0:
        for this in envs.environments:
            name = this.name
            marker = " ✓" if name == current_env else ""
            table.add_row(name + marker, str(this))

    console.print(f"\nThere are currently [bold]{envs.N}[/bold] Damona environment(s):\n")
    console.print(table)
    console.print(f"\nYour current env is [bold green]'{current_env}'[/bold green].\n")


# =================================================================== activate
@main.command()
@click.argument("name", required=True, type=click.STRING)
def activate(**kwargs):
    """Activate a damona environment.

    The main Damona environment can be activated using:

        damona activate base

    Then, activation of a specific environment is done as:

        damona activate my_favorite_env

    """
    # DO NOT PRINT ANYTHING HERE OTHERWISE YOU'LL BREAK
    # DAMONA BASH EXPORT.If yo do, use # as commented text
    envs = Environ()
    envs.activate(kwargs["name"])


# =================================================================== deactivate
@main.command()
@click.argument("name", required=False, type=click.STRING, default=None)
@common_logger
def deactivate(**kwargs):
    """Deactivate the current Damona environment.

    deactivate the current environment:

        damona deactivate

    """
    # DO NOT PRINT ANYTHING HERE OTHERWISE YOU'LL BREAK
    # DAMONA BASH EXPORT.If yo do, use # as commented text
    env = Environ()
    env.deactivate(kwargs["name"])


# =================================================================== install
@main.command()
@click.argument("image", required=True, type=click.STRING)
@click.option("--force-image", is_flag=True, help="Overwrite the image if it already exists.")
@click.option("--force", is_flag=True, help="Overwrite both the image and its binaries.")
@click.option("--force-binaries", is_flag=True, help="Overwrite binaries even if they already exist.")
@click.option(
    "--local-registry-only", is_flag=True, default=False, help="Use the local registry only, ignore the online URL."
)
@click.option(
    "--registry",
    default=URL,
    help="URL of the online registry file. Override to use a custom registry.",
)
@click.option(
    "--binaries",
    default=None,
    help="Comma-separated list of binary names to install. Defaults to the image name.",
)
@common_logger
def install(**kwargs):
    """Download and install an image and its binaries into the active environment.

    Install a registered image by name, optionally specifying a version:

        damona install fastqc
        damona install fastqc:0.11.9

    If the version is omitted, the latest available version is installed.

    You may also install a local image file. By convention, image filenames must
    follow the pattern NAME_[v]x.y.z[_info].img (extension can be .img or .sif).
    The binary name defaults to the image name, but can be overridden:

        damona install fastqc_0.11.9.img
        damona install tool_0.4.2.img --binaries fastqc,tool2

    Images are stored in ~/.config/damona/images/ (or the directory set by
    the DAMONA_PATH environment variable).

    """
    logger.debug(kwargs)

    env = Environ()
    cenv = env.get_current_env()

    image_path = pathlib.Path(kwargs["image"]).absolute()

    force_image = kwargs["force_image"]
    force_binaries = kwargs["force_binaries"]

    if kwargs["force"]:
        force_image, force_binaries = True, True

    if kwargs["binaries"]:
        if "," in kwargs["binaries"]:
            binaries = kwargs["binaries"].split(",")
        else:
            binaries = [kwargs["binaries"]]
    else:
        binaries = None

    if kwargs["image"].startswith("biocontainers/"):
        p = BiocontainersInstaller(kwargs["image"], binaries=binaries)
        p.pull_image(force=force_image)
        p.install_binaries(force=force_binaries)
    elif os.path.exists(image_path) is False:
        url = kwargs["registry"]
        if url_exists(url) and kwargs["local_registry_only"] is False:
            logger.info(f"Installing from online registry ({url})")
            registry = Registry(from_url=url)
            p = RemoteImageInstaller(kwargs["image"], from_url=kwargs["registry"], cmd=sys.argv, binaries=binaries)
        else:
            logger.info("Installing from local registry")
            registry = Registry(from_url=None)
            p = RemoteImageInstaller(kwargs["image"], from_url=None, cmd=sys.argv, binaries=binaries)

        if p.is_valid():
            p.pull_image(force=force_image)
            p.install_binaries(force=force_binaries)
            with open(cenv / "history.log", "a+") as fout:
                cmd = " ".join(["damona"] + sys.argv[1:])
                fout.write(f"\n{time.asctime()}: {cmd}")
        else:
            logger.critical("Something wrong with your image/binaries. See message above")
            sys.exit(1)
    else:
        # This install the image and associated binary/binaries
        logger.info(f"Installing local container in {cenv}")

        lii = LocalImageInstaller(image_path, cmd=sys.argv, binaries=binaries)
        if lii.is_valid():
            lii.install_image(force=force_image)
            lii.install_binaries(force=force_binaries)
            with open(cenv / "history.log", "a+") as fout:
                cmd = " ".join(["damona"] + sys.argv[1:])
                fout.write(f"\n{time.asctime()}: {cmd}")
        else:
            logger.critical("Something wrong with your image/binaries. See message above")
            sys.exit(1)


# =================================================================== uninstall
@main.command()
@click.argument("name", required=True, type=click.STRING)
@click.option(
    "--environment", type=click.STRING, default=None, help="Target environment. Defaults to the currently active one."
)
# @click.option("--force", is_flag=True, help="force the removal of binaries or images")
@common_logger
def uninstall(**kwargs):
    """Uninstall a binary or an image from an environment.

    To uninstall an image (identified by the .img extension), pass its filename:

        damona uninstall fastqc_0.11.8.img

    To uninstall a binary from the active environment (and the image if it becomes orphaned):

        damona uninstall fastqc

    An image is only deleted from disk when it is no longer referenced by any environment.
    """
    # First, let us figure out the current or user-defined environment
    envs = Environ()
    env_name = kwargs["environment"]
    if not env_name:
        env_name = envs.get_current_env_name(warning=False)
        if env_name is None:
            logger.error(
                "You must activate a damina environment or use the --environment to define one where binary:image will be removed."
            )
            sys.exit(1)

    env = Environment(env_name)
    dam = Damona()

    # then, let us figure out what the user wants (remove a binary or image ?) and do it
    name = kwargs["name"]
    if kwargs["name"].endswith(".img"):
        # we delete the image if it is an orphan
        p = get_damona_path() / "images" / kwargs["name"]
        if p.exists():
            ir = ImageReader(p)
            ir.delete()
        else:
            logger.warning(f"input file {p} does not exists")

    else:
        # Search for the name in the installed binaries
        if name in env:
            logger.info(f"Removing binary {name}")
            binary = [x for x in env.get_installed_binaries() if x.name == name]
            binary = binary[0]
            br = BinaryReader(binary)
            br.image

            # keep this info before deleting the file
            image_name = br.get_image()

            # we now delete the executable
            binary.unlink()

            # and the image if required
            p = get_damona_path() / "images" / (image_name.replace(":", "_") + ".img")
            ir = ImageReader(p)
            ir.delete()
        else:
            logger.warning(f"{name} was not found in the environment {env_name}. Not removed")

    with open(env.path / "history.log", "a+") as fout:
        cmd = " ".join(["damona"] + sys.argv[1:])
        fout.write(f"\n{time.asctime()}: {cmd}")


# =================================================================== clean
@main.command()
@click.option(
    "--do-remove", is_flag=True, help="Actually delete the orphaned binaries and images (dry-run by default)."
)
@common_logger
def clean(**kwargs):
    """Find and remove orphaned images and binaries across all environments.

    An orphaned binary points to a missing image; an orphaned image has no
    binary referencing it in any environment. This can happen after upgrades.

    By default this is a dry run — use --do-remove to actually delete:

        damona clean
        damona clean --do-remove

    To remove an entire environment, use:

        damona remove NAME

    """
    logger.debug(kwargs)

    dmn = Damona()

    # First we deal with orphans from the binaries directories
    orphans = dmn.find_orphan_binaries()
    if len(orphans) == 0:
        # nothing to do
        logger.info("No binary orphan found")
    else:
        logger.info(f"Found {len(orphans)} binary orphans.")
        if kwargs["do_remove"]:
            for x in orphans:
                os.remove(os.path.expanduser(x))
                logger.info(f"Removed {x}")
        else:
            logger.warning("Please use --do-remove to confirm that you want to remove the orphans")

    # Second, we find images that have no more binaries
    orphans = dmn.find_orphan_images()
    if len(orphans) == 0:
        logger.info("No orphan images found")
    else:
        logger.info(f"Found {len(orphans)} image orphans.")

        if kwargs["do_remove"]:  # pragma: no cover
            for x in orphans:
                os.remove(os.path.expanduser(x))
                logger.info(f"Removed {x}")
        else:
            logger.warning("Please use --do-remove to confirm that you want to remove the orphans")


# =================================================================== search
@main.command()
@click.argument("pattern", required=True, type=click.STRING)
@click.option("--images-only", is_flag=True, default=False, help="Show matching images only, not binaries.")
@click.option("--include-biocontainers", is_flag=True, default=False, help="Also search the BioContainers registry.")
@click.option(
    "--local-registry-only", is_flag=True, default=False, help="Use the local registry only, ignore the online URL."
)
@click.option("--binaries-only", is_flag=True, default=False, help="Show matching binaries only, not images.")
@click.option(
    "--registry",
    default=URL,
    show_default=True,
    help="URL of the online registry file. Override to use a custom registry.",
)
@common_logger
def search(**kwargs):
    """Search the registry for a container image or binary.

    Search by name in the official Damona registry:

        damona search fastqc

    Use `"*"` to list all available software and versions:

        damona search "*"

    On fish shells, quote the wildcard differently:

        damona search '"*"'

    You can define a custom registry in ~/.config/damona/damona.cfg:

        [urls]
        alias=https://example.com/damona/registry.yaml

    Then pass it via --registry or its alias. To also search BioContainers:

        damona search fastqc --include-biocontainers

    """
    url = kwargs.get("registry")

    if kwargs["pattern"] == "*":
        pattern = None
    else:
        pattern = kwargs["pattern"]

    if url_exists(url) and kwargs["local_registry_only"] is False:
        logger.info(f"Searching online registry ({url})")
        registry = Registry(from_url=url)
    else:
        logger.info("Searching local registry")
        registry = Registry(from_url=None)

    console = Console()
    recommended = None
    recommended_url = None
    recommended_size = None

    if not kwargs["binaries_only"]:
        modules = registry.get_list(pattern=pattern)
        table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
        table.add_column("Release", style="bold", min_width=25)
        table.add_column("Size", justify="right", min_width=8)
        table.add_column("URL")
        for mod in modules:
            name, version = mod.split(":")
            dl_url = registry.registry[mod]._data[name]["releases"][version]["download"]
            try:
                size = registry.registry[mod]._data[name]["releases"][version]["filesize"]
                if size > 1e9:
                    size_str = f"{round(size / 1e9, 2)}G"
                else:
                    size_str = f"{round(size / 1e6, 2)}M"
            except Exception:
                logger.warning(f"{mod}. could not extract filesize")
                size_str = "-1"

            table.add_row(mod, size_str, dl_url)
            if not recommended:
                recommended = mod
                recommended_url = dl_url
                recommended_size = size_str
            else:
                recommended_version = recommended.split(":")[1]
                try:
                    if packaging.version.parse(version) > packaging.version.parse(recommended_version):
                        recommended = mod
                        recommended_url = dl_url
                        recommended_size = size_str
                except packaging.version.InvalidVersion:
                    pass

        console.print(f"\nPattern '[bold]{pattern}[/bold]' found in these releases:")
        console.print(table)

    if not kwargs["images_only"]:
        modules = registry.get_binaries(pattern=pattern)
        table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
        table.add_column("Release", style="bold", min_width=25)
        table.add_column("Binaries")
        table.add_column("Size", justify="right", min_width=8)
        for mod in sorted(modules.keys()):
            v = modules[mod]
            name, version = mod.split(":")
            try:
                size = registry.registry[mod]._data[name]["releases"][version]["filesize"]
                if size > 1e9:
                    size_str = f"{round(size / 1e9, 2)}G"
                else:
                    size_str = f"{round(size / 1e6, 2)}M"
            except Exception:
                logger.warning(f"{mod}. could not extract filesize")
                size_str = "-1"

            table.add_row(mod, ", ".join(v), size_str)

        console.print(f"\nPattern '[bold]{pattern}[/bold]' found as binaries:")
        console.print(table)

    if kwargs["include_biocontainers"]:
        console.print("\n[bold]Searching biocontainers:[/bold]")
        br = BiocontainersRegistry()
        for name, data in br.data.items():
            if pattern in name:
                console.print(f"Pattern '[bold]{name}[/bold]' Found in these releases:")
                for version, location in data["releases"].items():
                    download = f"{location['download']})"
                    download = download.replace("docker://quay.io/", "").split("--")[0]
                    download = download.replace("docker://", "").split("--")[0]
                    install = f"(damona install {download})"
                    console.print(f" - {name}:{version}: {install} ")
            elif pattern is None:
                console.print(f" - {name}")

    if recommended:
        content = f"[bold green]damona install {recommended}[/bold green]"
        if recommended_size:
            content += f"  [dim]({recommended_size})[/dim]"
        if recommended_url:
            content += f"\n[dim italic]For your information, url is {recommended_url}[/dim italic]"
        console.print(
            Panel(
                content,
                title="ℹ️  Recommended installation (latest version and dedicated container)",
                border_style="green",
            )
        )


# ============================================================  export
@main.command()
@click.argument("environment", required=True, type=click.STRING)
@common_logger
def info(**kwargs):
    """Show images and binaries installed in an environment.

    damona info base
    damona info myenv

    """
    logger.debug(kwargs)
    envname = kwargs["environment"]

    manager = Environ()

    x = [ee for ee in manager.environments if ee.name == envname]
    if len(x) == 0:
        logger.error(f"Environment '{envname}' does not exist. Use 'damona env' to get the list")
        sys.exit(1)
    else:
        environ = x[0]
        console = Console()
        console.print(f"\n[bold]Environment:[/bold] {envname}\n")

        img_table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
        img_table.add_column("Images", style="dim", min_width=30)
        for item in sorted(environ.get_images()):
            img_table.add_row(pathlib.Path(item).name)
        console.print(img_table)

        bin_table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
        bin_table.add_column("Binaries", min_width=30)
        for item in sorted(environ.get_installed_binaries()):
            bin_table.add_row(pathlib.Path(item).name)
        console.print(bin_table)


# ============================================================  export
@main.command()
@click.argument("environment", required=True, type=click.STRING)
@click.option("--yaml", help="Output YAML file path.")
@click.option("--bundle", default=None, help="Output tar bundle file path.")
@common_logger
def export(**kwargs):
    """Export an environment as a YAML file or a tar bundle.

    A YAML file records the image and binary names (lightweight, no data):

        damona export TEST --yaml test_env.yaml

    A tar bundle copies the actual image files (portable, larger):

        damona export TEST --bundle test_bundle.tar

    The exported file can be used to recreate the environment:

        damona create TEST1 --from-yaml   test_env.yaml
        damona create TEST1 --from-bundle test_bundle.tar

    """
    from damona import Environment

    logger.debug(kwargs)

    environment = kwargs["environment"]
    envname = kwargs["environment"]

    # TODO This should be based on the binaries of the environment, not the images
    # to do so, we'll need an installed.txt file

    env = Environment(envname)
    if kwargs["bundle"]:
        bundle_file = kwargs["bundle"]
        output = env.create_bundle(output_name=kwargs["bundle"])
        logger.info(
            f"Use this command to recreate the environment: \n\n\tdamona create NEW_NAME --from-bundle {bundle_file}"
        )
    elif kwargs["yaml"]:
        yaml_file = kwargs["yaml"]
        env.create_yaml(output_name=yaml_file)
        logger.info(
            f"Use this command to recreate the environment: \n\n\tdamona create NEW_NAME --from-yaml {yaml_file}"
        )
    else:
        raise click.UsageError("Please specify --yaml or --bundle. See 'damona export --help'.")


# ============================================================  stats


@main.command()
@click.option("--include-biocontainers", is_flag=True, help="Also count BioContainers entries (experimental).")
@click.option("--include-downloads", is_flag=True, help="Fetch and show download counts from Zenodo (slow).")
@common_logger
def stats(**kwargs):
    """Show registry statistics and local installation summary.

    Prints the number of containers, versions, and unique binaries in the
    registry, plus how many images are installed locally and their disk usage:

        damona stats

    """
    import contextlib
    import io

    from damona import admin

    console = Console()
    with contextlib.redirect_stdout(io.StringIO()):
        data = admin.stats()
    if kwargs["include_biocontainers"]:
        with contextlib.redirect_stdout(io.StringIO()):
            bc_data = admin.stats(True)

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Key", style="bold cyan", min_width=25)
    table.add_column("Value", justify="right")
    table.add_row("Containers", str(data["software"]))
    table.add_row("Versions", str(data["version"]))
    table.add_row("Unique binaries", str(data["unique_binaries"]))
    if kwargs["include_biocontainers"]:
        table.add_row("Biocontainers", str(bc_data.get("software", "N/A")))
    console.print(Panel(table, title="[bold]Damona Registry Stats[/bold]", border_style="cyan"))

    if kwargs["include_downloads"]:
        console.print("\n[bold]Detailed summary of downloads for each container:[/bold]")
        from damona import admin, zenodo

        all_software = sorted(admin.get_software_names())
        N = 0
        console.print(f"{'Software':<25} {'Downloads':>10}")
        console.print("-" * 36)
        for software in all_software:
            downloads = zenodo.get_stats_software(software)
            console.print(f"{software:<25} {str(downloads):>10}")
            try:
                N += int(str(downloads).replace(",", ""))
            except (AttributeError, ValueError):
                pass
        console.print("-" * 36)
        console.print(f"[bold]Total:[/bold] {N}")

    envs = Environ()
    N = len(envs.images)
    usage = envs.images.get_disk_usage()
    console.print(
        Panel(
            f"[bold]{N}[/bold] image(s) installed, using [bold]{usage} Mb[/bold] of disk space.",
            title="[bold]Local Installation[/bold]",
            border_style="cyan",
        )
    )


# ===================================================================  list


@main.command()
@common_logger
def list(**kwargs):
    """List all containers available in the local registry."""
    r = Registry()
    console = Console()
    table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
    table.add_column("Name", style="bold", min_width=20)
    table.add_column("Version", min_width=10)
    for entry in sorted(r.get_list()):
        name, version = entry.split(":")
        table.add_row(name, version)
    console.print(table)


# ===================================================================  catalog


def _get_base_image(name, version, damona_root):
    """Return a short base-image label extracted from the Singularity definition file."""
    import pathlib as _pathlib

    sif_path = _pathlib.Path(damona_root) / "software" / name / f"Singularity.{name}_{version}"
    if not sif_path.exists():
        return "?"

    bootstrap = None
    from_line = None
    with open(sif_path) as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.lower().startswith("bootstrap:"):
                bootstrap = stripped.split(":", 1)[1].strip().lower()
            elif stripped.lower().startswith("from:"):
                from_line = stripped.split(":", 1)[1].strip()
                break

    if from_line is None:
        return "?"

    from_lower = from_line.lower()
    # localimage pointing to a library .img file
    if bootstrap == "localimage" or (bootstrap is None and from_line.endswith(".img")):
        stem = _pathlib.Path(from_line).stem  # e.g. micromamba_1.5.8
        return stem.rsplit("_", 1)[0] if "_" in stem else stem

    # docker / library bootstrap — keep registry-prefix stripped
    label = from_line.split("/")[-1]  # drop registry host and org
    return label


@main.command(hidden=True)
@click.option(
    "--sort",
    default="name",
    type=click.Choice(["name", "size", "base"], case_sensitive=False),
    show_default=True,
    help="Sort rows by software name, download size, or base image.",
)
@common_logger
def catalog(**kwargs):
    """Show a developer overview: latest version, size, and base image for every container.

    Iterates the local registry and, for each software, reports the latest
    available version, its download size, and the underlying base image
    inferred from the Singularity definition file:

        damona catalog

    Sort by size to quickly spot heavy containers:

        damona catalog --sort size

    Sort by base image to group containers sharing the same base:

        damona catalog --sort base

    Useful for spotting containers that use heavy bases (e.g. micromamba) vs
    lean ones (alpine, debian-slim) and for auditing image sizes at a glance.
    """
    import pathlib as _pathlib

    import packaging.version as _pv

    from damona import __path__ as _damona_path

    damona_root = _damona_path[0]
    registry = Registry(from_url=None)
    console = Console()

    # Group versions by software name and collect all row data first
    software_versions: dict = {}
    for key in registry.get_list():
        sw_name, ver = key.split(":")
        software_versions.setdefault(sw_name, []).append(ver)

    rows = []
    for sw_name in software_versions:
        versions = software_versions[sw_name]
        try:
            latest = str(max(versions, key=lambda v: _pv.parse(v)))
        except Exception:
            latest = versions[-1]

        key = f"{sw_name}:{latest}"
        try:
            size = registry.registry[key]._data[sw_name]["releases"][latest]["filesize"]
            size_str = f"{round(size / 1e9, 2)}G" if size > 1e9 else f"{round(size / 1e6, 2)}M"
        except Exception:
            size = 0
            size_str = "?"

        base = _get_base_image(sw_name, latest, damona_root)
        rows.append((sw_name, latest, size_str, base, size))

    sort_key = kwargs["sort"].lower()
    if sort_key == "size":
        rows.sort(key=lambda r: r[4])
    elif sort_key == "base":
        rows.sort(key=lambda r: r[3].lower())
    else:
        rows.sort(key=lambda r: r[0].lower())

    table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
    table.add_column("Software", style="bold", min_width=22)
    table.add_column("Latest", min_width=12)
    table.add_column("Size", justify="right", min_width=8)
    table.add_column("Base image", min_width=24)

    for sw_name, latest, size_str, base, _ in rows:
        table.add_row(sw_name, latest, size_str, base)

    console.print(table)


# ============================================================  HIDDEN commands
# ============================================================  zenodo-upload


@main.command(hidden=True)
@click.argument("filename", required=True)
@click.option(
    "--token",
    default=None,
    help="Zenodo API token. If not given, read from ~/.config/damona/damona.cfg.",
)
@click.option(
    "--sandbox/--production",
    default=True,
    help="Target Zenodo sandbox (default) or production. Use --production when ready to publish for real.",
)
@click.option(
    "--no-check", default=False, is_flag=True, help="Skip the python/bash availability check inside the container."
)
@click.option(
    "--binaries",
    default=None,
    help="Space or comma separated binary names for new software (skips interactive prompt).",
)
@click.option(
    "--extra-binaries",
    default=None,
    help="Space or comma separated extra binaries specific to this release (skips interactive prompt).",
)
@common_logger
def publish(**kwargs):  # pragma: no cover
    """Publish a Singularity image to Zenodo. FOR DEVELOPERS ONLY.

    By default this targets the Zenodo sandbox so you can test without
    creating a real DOI.  The result is written to registry_sandbox.yaml.
    Switch to production with --production when the image is ready:

        damona publish mytool_1.0.0.img
        damona publish mytool_1.0.0.img --production

    Tokens and author metadata are read from ~/.config/damona/damona.cfg:

        [zenodo]
        token=APmm6p...
        orcid=0000-0001-...
        affiliation=Your Institute
        name=Surname, firstname

        [sandbox.zenodo]
        token=FFmbAE...
        orcid=0000-0001-...
        affiliation=Your Institute
        name=Surname, firstname

    """
    from damona.zenodo import Zenodo

    token = kwargs["token"]
    mode = "sandbox.zenodo" if kwargs["sandbox"] else "zenodo"
    filename = kwargs["filename"]

    # check that python and bash are available in the container.
    status = subprocess.run(f"{get_container_cmd()} exec {filename} python --version".split(), stdout=subprocess.PIPE)
    if status.returncode:
        click.echo("Damona Warning: could not find **python** command in the container")
        proceed = click.prompt("Do you want to proceed ?")
        if proceed:
            click.echo("Publishing without Python found in the container.")
        else:
            click.echo("Exiting...")
            sys.exit(1)

    status = subprocess.run(f"{get_container_cmd()} exec {filename} bash --version".split(), stdout=subprocess.PIPE)
    if status.returncode:
        click.echo("Damona ERROR: could not find **bash** command in the container", err=True)
        sys.exit(1)

    z = Zenodo(mode, token)
    logger.info(f"Publishing to {mode}")
    z._upload(filename, binaries=kwargs.get("binaries"), extra_binaries=kwargs.get("extra_binaries"))


# =================================================================== check
@main.command()
@click.argument("image", type=click.Path(exists=True))
@click.option(
    "--binaries",
    default=None,
    help="Comma-separated list of binaries to check. Defaults to those listed in the local registry.",
)
@common_logger
def check(**kwargs):
    """Check that all binaries in a built image are functional.

    Given a local Singularity image, run each registered binary inside the
    container and report whether it is found and executable.  Useful after
    building a new image to catch missing or broken tools before uploading.

    Check all binaries declared in the registry for fastqc:

        damona check ~/.config/damona/images/fastqc_0.11.9.img

    Override the binary list manually:

        damona check fastqc_0.11.9.img --binaries fastqc

    Exit code is 0 if all binaries pass, 1 if any fail.
    """
    from damona.common import get_container_cmd
    from damona.registry import Registry

    image = pathlib.Path(kwargs["image"]).resolve()
    console = Console()

    # Determine binary list
    if kwargs["binaries"]:
        binaries = [b.strip() for b in kwargs["binaries"].split(",")]
    else:
        # Try to infer from the local registry using the image filename
        reader = ImageReader(image)
        name = reader.guessed_executable
        version = reader.version
        reg = Registry(from_url=None)
        key = f"{name}:{version}"
        if key in reg.registry:
            binaries = reg.registry[key].binaries
        else:
            logger.critical(f"Could not find '{key}' in the local registry. Use --binaries to specify them explicitly.")
            raise SystemExit(1)

    container_cmd = get_container_cmd()
    container_runner = f"{container_cmd} exec {str(image)}"

    try:
        from versionix.parser import Versionix as _Versionix

        _versionix_available = True
    except ImportError:
        _versionix_available = False

    table = Table(title=f"Binary check: {image.name}", show_lines=False)
    table.add_column("Binary", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Output", style="dim")

    all_ok = True
    with Live(table, console=console, refresh_per_second=4):
        for binary in binaries:
            found = False
            version_str = ""

            # Existence probe: a single fast call is enough to detect "not found"
            try:
                probe = subprocess.run(
                    f"{container_cmd} exec {image} {binary} --version",
                    shell=True,
                    capture_output=True,
                    timeout=10,
                )
                probe_out = (probe.stdout + probe.stderr).decode(errors="replace")
            except subprocess.TimeoutExpired:
                probe_out = ""

            if "executable file not found" in probe_out or "command not found" in probe_out:
                found = False
            else:
                found = True
                if _versionix_available:
                    try:
                        version_str = _Versionix(binary, container_runner=container_runner).get_version()
                    except Exception:
                        version_str = probe_out.splitlines()[0][:60] if probe_out.strip() else ""
                else:
                    version_str = probe_out.splitlines()[0][:60] if probe_out.strip() else ""

            status = Text("PASS", style="bold green") if found else Text("FAIL", style="bold red")
            table.add_row(binary, status, version_str)
            if not found:
                all_ok = False

    if not all_ok:
        raise SystemExit(1)


# =================================================================== build
@main.command()
@click.argument("filename", required=True, type=click.STRING)
@click.option(
    "--destination",
    default=None,
    help="Output image filename (required when the source has no version, e.g. docker:// URLs).",
)
@click.option("--force", is_flag=True, help="Overwrite the output image if it already exists.")
@common_logger
def build(**kwargs):  # pragma: no cover
    """Build a Singularity image from a local recipe, a Damona recipe, or a Docker image.

    From a local Singularity recipe (filename must follow Singularity.NAME_x.y.z):

    \b
        damona build Singularity.salmon_1.3.0

    From a Damona-registered recipe (listed by 'damona list'):

        damona build salmon:1.3.0

    From a Docker Hub image:

        damona build docker://biocontainers/bowtie2:v2.4.1_cv1

    When the source URL carries no version, provide the output name explicitly:

        damona build docker://kapeel/hisat2 --destination hisat2_v2.0.0.img

    """
    logger.debug(kwargs)
    filename = kwargs["filename"]
    force = kwargs["force"]
    destination = kwargs["destination"]

    if destination:
        if destination.endswith(".img") is False:
            logger.warning("You should end your image with the .img extension")
        if "_" not in destination:
            logger.warning("You should name your image as NAME_x.y.z")

    if os.path.exists(filename) and os.path.isdir(filename) is False:
        # TODO check that it starts with Singularity
        # local recipes ?
        from damona.builders import BuilderFromSingularityRecipe

        builder = BuilderFromSingularityRecipe()
        builder.build(filename, destination=destination, force=force)
    elif kwargs["filename"].startswith("docker://"):
        from damona.builders import BuilderFromDocker

        builder = BuilderFromDocker()
        filename = filename.replace("docker://", "")
        builder.build(filename, destination=destination, force=force)
    else:  # could be a damona recipes
        logger.info("Not a docker URL, nor a local file.")


if __name__ == "__main__":  # pragma: no cover
    main()
