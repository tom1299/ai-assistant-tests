"""
This module provides a script to list files that need to be encrypted based on sops configuration.
"""

import os
import re
import argparse
import yaml

DEFAULT_SOPS_CONFIG = '.sops.yaml'

def list_files(directory):
    """
    Generator function to list all files in a given directory.

    Args:
        directory (str): The directory to search for files.

    Yields:
        str: The path to a file.
    """
    for root, _, files in os.walk(directory):
        for filename in files:
            yield os.path.join(root, filename)

def match_files_with_keys(sops_file, directory):
    """
    Matches the file paths with the path_regex in the sops_file and generates a dictionary
    where the keys are the public_key values and the values are lists of matched files.

    Args:
        sops_file (str): The path to the sops configuration file.
        directory (str): The directory to search for files.

    Returns:
        dict: A dictionary where the keys are the public_key values and the values are
        lists of matched files.
    """
    with open(sops_file, 'r', encoding='utf-8') as file:
        sops_config = yaml.safe_load(file)

    creation_rules = sops_config.get('creation_rules', [])
    matched_files = {}

    for filepath in list_files(directory):
        for rule in creation_rules:
            if re.match(rule['path_regex'], filepath):
                if rule['age'] not in matched_files:
                    matched_files[rule['age']] = []
                matched_files[rule['age']].append(filepath)

    return matched_files

def main():
    """
    Main function that parses command-line arguments and prints out the public_key and list
    of matched files.
    """
    parser = argparse.ArgumentParser(
        description='List files that need to be encrypted based on sops configuration.'
    )
    parser.add_argument('directory', help='The directory to search for files.')
    parser.add_argument(
        '--sops-config',
        default=DEFAULT_SOPS_CONFIG,
        help='The path to the sops configuration file.'
    )

    args = parser.parse_args()

    matched_files = match_files_with_keys(args.sops_config, args.directory)

    sops_dir = os.path.dirname(os.path.abspath(args.sops_config))

    for files in matched_files.values():
        for filepath in files:
            rel_path = os.path.relpath(filepath, start=sops_dir)
            print(rel_path)

if __name__ == "__main__":
    main()
