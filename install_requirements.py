"""
This script automates the setup and management of this project's dependencies. It is intended to be run in the same directory as 
'requirements.txt.template' and 'requirements.txt'. 
The script checks for PyInstaller's presence, builds it if necessary to avoid AV detection issues, updates 'requirements.txt' to exclude 
PyInstaller, and installs all required packages.
"""

import os
from pathlib import Path
import re
import subprocess
import pkg_resources

def get_pyinstaller_version(template_path):
    with open(template_path, 'r') as file:
        content = file.read()
    match = re.search(r'pyinstaller==([0-9.]+)', content)
    if match:
        return match.group(1)
    else:
        raise ValueError("PyInstaller version not found in the template.")

def is_pyinstaller_installed():
    try:
        dist = pkg_resources.get_distribution('pyinstaller')
        if dist:
            print(f"PyInstaller is already installed at {dist.location}")
            return True
    except pkg_resources.DistributionNotFound:
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

def update_requirements_txt(template_path, output_path):
    with open(template_path, 'r') as file:
        content = file.readlines()
    updated_content = []
    for line in content:
        if not line.lower().startswith('pyinstaller='):
            updated_content.append(line)
    with open(output_path, 'w') as file:
        file.writelines(updated_content)
        print(f'Updated requirements.txt at "{output_path}"')

def install_requirements(requirements_path):
    print("Installing packages from requirements.txt...")
    subprocess.run([os.sys.executable, "-m", "pip", "install", "-r", str(requirements_path)], check=True)
    print("Packages installed.")

def main():
    script_dir = Path(__file__).resolve().parent
    print(f"Using script directory: {script_dir}")
    
    pyinstaller_src_path = Path(script_dir, "pyinstaller-src")
    requirements_template_path = Path(script_dir, "requirements.txt.template")
    requirements_path = Path(script_dir, "requirements.txt")
    
    if not is_pyinstaller_installed():
        pyinstaller_version = get_pyinstaller_version(requirements_template_path)
        clone_and_build_pyinstaller(pyinstaller_version, pyinstaller_src_path)
        
    update_requirements_txt(requirements_template_path, requirements_path)
    install_requirements(requirements_path)

if __name__ == "__main__":
    main()
