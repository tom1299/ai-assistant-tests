#!/bin/bash

# Check if directory, sops config file and public key are passed as arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 directory sops_config public_key"
    exit 1
fi

# Change to the directory passed as an argument
cd "$1" || exit

# Get the list of files to be encrypted from the python script key_rotation.py
files_to_encrypt=$(key_rotation.py list-files --folder "$1" --sops-config "$2" --age-key "$3")

# Iterate over the files
for file in $files_to_encrypt
do
    # Check if the file is not encrypted
    if ! sops -d $file > /dev/null 2>&1; then
        # If the file is not encrypted, encrypt it using the sops command
        sops --encrypt --in-place $file
        echo "Encrypted $file"
    else
        echo "$file is already encrypted"
    fi
done