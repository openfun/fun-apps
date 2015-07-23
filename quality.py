#! /usr/bin/env python

import argparse
import os
from glob import glob
import subprocess


FUNAPPS_DIR = os.path.dirname(__file__)

def main():
    args = parse_args()
    paths = find_module_and_packages(args.root_path)
    run(paths)

def parse_args():
    parser = argparse.ArgumentParser(description="Run quality tests on fun-apps")
    parser.add_argument("-i", "--input", dest='root_path', default='.', help="Path to module or package")
    return parser.parse_args()

def find_module_and_packages(root_path):
    if os.path.isdir(root_path):
        package_glob = os.path.join(root_path, "*/__init__.py")
        return [os.path.dirname(path) for path in glob(package_glob)]
    else:
        return [root_path]

def run(paths):
    pylintrc_path = os.path.join(FUNAPPS_DIR, "pylint.cfg")
    cmd = [
        'pylint',
        '--rcfile={}'.format(pylintrc_path),
    ] + paths
    subprocess.call(cmd)


if __name__ == "__main__":
    main()
