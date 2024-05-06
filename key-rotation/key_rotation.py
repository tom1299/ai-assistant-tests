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

def update_sops_config(sops_file, old_public_key, new_public_key):
    with open(sops_file, 'r', encoding='utf-8') as file:
        sops_config = yaml.safe_load(file)

    creation_rules = sops_config.get('creation_rules', [])

    for rule in creation_rules:
        if old_public_key in rule['age']:
            # Split the keys by comma, add the new key, and join them back together
            keys = rule['age'].split(',')
            if new_public_key not in keys:
                keys.append(new_public_key)
            rule['age'] = ','.join(keys)

    with open(sops_file, 'w', encoding='utf-8') as file:
        yaml.dump(sops_config, file)


def main():
    parser = argparse.ArgumentParser(
        description='List files that need to be encrypted based on sops configuration.'
    )
    parser.add_argument('--folder', required=False, help='The directory to search for files.')
    parser.add_argument('--sops-config', default=DEFAULT_SOPS_CONFIG, help='The path to the sops configuration file.')
    parser.add_argument('--age-key', required=False, help='The age public key the files returned should be matched encrypted with.')
    parser.add_argument('--list-files', action='store_true', help='Flag to list files.')
    parser.add_argument('--old-age-key', help='The old age public key to be replaced.')
    parser.add_argument('--new-age-key', help='The new age public key to add.')
    parser.add_argument('--add-new-key', action='store_true', help='Flag to add new key.')

    args = parser.parse_args()

    if args.list_files and args.add_new_key:
        parser.error("arguments --list-files and --add-new-key are mutually exclusive")
    elif not args.list_files and not args.add_new_key:
        parser.error("one of the arguments --list-files or --add-new-key is required")

    if args.list_files:
        matched_files = match_files_with_keys(args.sops_config, args.folder, args.age_key)

        sops_dir = os.path.dirname(os.path.abspath(args.sops_config))

        for files in matched_files.values():
            for filepath in files:
                rel_path = os.path.relpath(filepath, start=sops_dir)
                print(rel_path)

    if args.old_age_key and args.new_age_key and args.add_new_key:
        update_sops_config(args.sops_config, args.old_age_key, args.new_age_key)

if __name__ == "__main__":
    main()