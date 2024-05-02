#!/bin/bash

# The directory to start from
start_dir="$1"

# The function to add .gitignore to a directory
add_gitignore() {
    dir="$1"
    gitignore="${dir}/.gitignore"

    # Check if directory is empty and .gitignore doesn't exist
    if [[ -z "$(ls -A "$dir")" && ! -e "$gitignore" ]]; then
        # Add the .gitignore file
        echo -e "*\n!.gitignore" > "$gitignore"
    fi
}

# Export the function so it's available to subshells
export -f add_gitignore

# Use find to recursively call add_gitignore on all directories
find "$start_dir" -type d -exec bash -c 'add_gitignore "$0"' {} \;