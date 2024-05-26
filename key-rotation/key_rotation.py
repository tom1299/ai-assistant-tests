#!/usr/bin/env python3

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

def update_sops_config(sops_file, old_public_key, new_public_key=None):
    with open(sops_file, 'r', encoding='utf-8') as file:
        sops_config = yaml.safe_load(file)

    creation_rules = sops_config.get('creation_rules', [])

    for rule in creation_rules:
        keys = rule['age'].split(',')
        if new_public_key:
            # If the new_public_key is provided, add it to the 'age' field
            if new_public_key not in keys:
                keys.append(new_public_key)
        else:
            # If the new_public_key is not provided, remove the old_public_key from the 'age' field
            if old_public_key in keys:
                keys.remove(old_public_key)
        rule['age'] = ','.join(keys)

    with open(sops_file, 'w', encoding='utf-8') as file:
        yaml.dump(sops_config, file)


def main():
    parser = argparse.ArgumentParser(
        description='List files that need to be encrypted based on sops configuration.'
    )
    subparsers = parser.add_subparsers(dest='command')

    list_files_parser = subparsers.add_parser('list-files')
    list_files_parser.add_argument('--folder', required=True, help='The directory to search for files.')
    list_files_parser.add_argument('--sops-config', default=DEFAULT_SOPS_CONFIG, help='The path to the sops configuration file.')
    list_files_parser.add_argument('--age-key', required=True, help='The age public key to list the files for.')

    add_key_parser = subparsers.add_parser('add-key')
    add_key_parser.add_argument('--sops-config', default=DEFAULT_SOPS_CONFIG, help='The path to the sops configuration file.')
    add_key_parser.add_argument('--new-age-key', required=True, help='The age public key to add.')
    add_key_parser.add_argument('--old-age-key', required=True, help='The age key that identifies the rules to add the new key to.')

    args = parser.parse_args()

    if args.command == 'list-files':
        matched_files = match_files_with_keys(args.sops_config, args.folder, args.age_key)

        for files in matched_files.values():
            for filepath in files:
                print(filepath)

    elif args.command == 'add-key':
        update_sops_config(args.sops_config, args.new_age_key, args.old_age_key)

if __name__ == "__main__":
    main()