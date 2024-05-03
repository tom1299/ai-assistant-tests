import os
import re
import argparse
import yaml

DEFAULT_SOPS_CONFIG = '.sops.yaml'

def list_files(directory):
    for root, _, files in os.walk(directory):
        for filename in files:
            yield os.path.join(root, filename)

def match_files_with_keys(sops_file, directory, public_key):
    with open(sops_file, 'r', encoding='utf-8') as file:
        sops_config = yaml.safe_load(file)

    creation_rules = sops_config.get('creation_rules', [])
    matched_files = {}

    for filepath in list_files(directory):
        for rule in creation_rules:
            if re.match(rule['path_regex'], filepath) and public_key in rule['age']:
                if rule['age'] not in matched_files:
                    matched_files[rule['age']] = []
                matched_files[rule['age']].append(filepath)

    return matched_files

def main():
    parser = argparse.ArgumentParser(
        description='List files that need to be encrypted based on sops configuration.'
    )
    parser.add_argument('--folder', required=True, help='The directory to search for files.')
    parser.add_argument('--sops-config', default=DEFAULT_SOPS_CONFIG, help='The path to the sops configuration file.')
    parser.add_argument('--age-key', required=True, help='The age public key the files returned should be matched encrypted with.')
    parser.add_argument('--list-files', action='store_true', help='Flag to list files.')

    args = parser.parse_args()

    if args.list_files:
        matched_files = match_files_with_keys(args.sops_config, args.folder, args.age_key)

        sops_dir = os.path.dirname(os.path.abspath(args.sops_config))

        for files in matched_files.values():
            for filepath in files:
                rel_path = os.path.relpath(filepath, start=sops_dir)
                print(rel_path)

if __name__ == "__main__":
    main()