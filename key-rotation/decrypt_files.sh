#!/bin/bash

# Check if directory, sops config file and public key are passed as arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 directory sops_config public_key"
    exit 1
fi

# Change to the directory passed as an argument
cd "$1" || exit

# Get the list of files to be decrypted from the python script key_rotation.py
files_to_decrypt=$(key_rotation.py list-files --folder "$1" --sops-config "$2" --age-key "$3")

# Iterate over the files
for file in $files_to_decrypt
do
    # Check if the file is encrypted
    if sops -d $file > /dev/null 2>&1; then
        # If the file is encrypted decrypt it using the sops command
        sops --decrypt --in-place $file
        echo "Decrypted $file"
    else
        echo "$file is not encrypted"
    fi
done