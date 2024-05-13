"""
This script ensures that PyInstaller, as specified by PYINSTALLER_VERSION, is installed locally. 
It checks for an existing installation and, if absent, clones and builds PyInstaller from source.
Building locally mitigates AV detection issues commonly associated with pre-built binaries.
"""

import os
from pathlib import Path
import subprocess
from importlib import metadata

PYINSTALLER_VERSION = '6.6.0'

def is_pyinstaller_installed():
    try:
        dist = metadata.distribution('pyinstaller')
        if dist:
            print(f"PyInstaller is already installed at {dist.locate_file('')}")
            return True
    except metadata.PackageNotFoundError:
        return False
    return False

def clone_and_build_pyinstaller(version, local_path):
    repo_url = "https://github.com/pyinstaller/pyinstaller.git"
    setup_path = Path(local_path, 'setup.py')
    if not local_path.exists() or not setup_path.exists():
        subprocess.run(["git", "clone", repo_url, str(local_path)], check=True)
    subprocess.run(["git", "checkout", f"v{version}"], cwd=str(local_path), check=True)
    if setup_path.exists():
        subprocess.run([os.sys.executable, "-m", "pip", "install", "."], cwd=str(local_path), check=True)

def main():
    script_dir = Path(__file__).resolve().parent
    print(f"Using script directory: {script_dir}")
    
    pyinstaller_src_path = Path(script_dir, "pyinstaller-src")
    
    if not is_pyinstaller_installed():
        clone_and_build_pyinstaller(PYINSTALLER_VERSION, pyinstaller_src_path)

if __name__ == "__main__":
    main()
