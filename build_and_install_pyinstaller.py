"""
This script ensures that PyInstaller, as specified by PYINSTALLER_VERSION, is installed locally. 
It checks for an existing installation and, if absent, fetches and builds PyInstaller from source using `git archive`.
Building locally mitigates AV detection issues commonly associated with pre-built binaries.
"""
import os
from pathlib import Path
import subprocess
from importlib import metadata
import tarfile
import requests

PYINSTALLER_VERSION = '6.6.0'
PYINSTALLER_ARCHIVE_URL = f"https://github.com/pyinstaller/pyinstaller/archive/refs/tags/v{PYINSTALLER_VERSION}.tar.gz"


def is_pyinstaller_installed():

    try:
        dist = metadata.distribution('pyinstaller')
        if dist:
            print(f"PyInstaller is already installed at {dist.locate_file('')}")
            return True
    except metadata.PackageNotFoundError:
        return False
    return False


def fetch_and_build_pyinstaller(local_path):

    tar_path = local_path / f"pyinstaller-{PYINSTALLER_VERSION}.tar.gz"
    extracted_path = local_path / f"pyinstaller-{PYINSTALLER_VERSION}"

    # Fetch the tarball if not already present
    if not tar_path.exists():
        print(f"Fetching PyInstaller version {PYINSTALLER_VERSION} from {PYINSTALLER_ARCHIVE_URL}")
        response = requests.get(PYINSTALLER_ARCHIVE_URL, stream=True)
        response.raise_for_status()
        with open(tar_path, 'wb') as tar_file:
            for chunk in response.iter_content(chunk_size=8192):
                tar_file.write(chunk)

    # Extract the tarball
    if not extracted_path.exists():
        print(f"Extracting PyInstaller version {PYINSTALLER_VERSION}")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=local_path)

    # Build and install PyInstaller
    setup_path = extracted_path / 'setup.py'
    if setup_path.exists():
        subprocess.run([os.sys.executable, "-m", "pip", "install", "."], cwd=str(extracted_path), check=True)


def main():
    script_dir = Path(__file__).resolve().parent
    print(f"Using script directory: {script_dir}")
    
    pyinstaller_src_path = Path(script_dir, "pyinstaller-src")
    pyinstaller_src_path.mkdir(exist_ok=True)

    #if not is_pyinstaller_installed():
    fetch_and_build_pyinstaller(pyinstaller_src_path)


if __name__ == "__main__":
    main()
