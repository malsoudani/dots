#!/bin/bash

# Prompt for GitHub username and email
read -p "Enter your GitHub username: " github_username
read -p "Enter your GitHub email: " github_email

# Generate SSH key
ssh_key_file="$HOME/.ssh/github_rsa"

if [ -f "$ssh_key_file" ]; then
    echo "SSH key already exists at $ssh_key_file"
else
    echo "Generating a new SSH key..."
    ssh-keygen -t rsa -b 4096 -C "$github_email" -f "$ssh_key_file" -N ""
    if [[ $? -ne 0 ]]; then
        echo "Failed to generate SSH key."
        exit 1
    fi
    echo "SSH key generated successfully."
fi

# Start the SSH agent
eval "$(ssh-agent -s)"

# Add SSH private key to the SSH agent
ssh-add "$ssh_key_file"
if [[ $? -ne 0 ]]; then
    echo "Failed to add SSH key to the SSH agent."
    exit 1
fi

echo "SSH key added to SSH agent successfully."

# Copy the SSH public key to clipboard
if command -v pbcopy &> /dev/null; then
    pbcopy < "${ssh_key_file}.pub"
    echo "SSH key copied to clipboard."
else
    cat "${ssh_key_file}.pub"
    echo "Copy the above SSH key to your clipboard."
fi

# Prompt for GitHub personal access token (PAT)
read -sp "Enter your GitHub personal access token (PAT): " github_pat
echo

read -p "Enter a name for this SSH key (e.g., 'My Computer'): " ssh_key_title

# Use curl to add the SSH key to GitHub via API
response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $github_pat" \
    --data "{\"title\":\"$ssh_key_title\",\"key\":\"$(cat ${ssh_key_file}.pub)\"}" \
    https://api.github.com/user/keys)

if [[ $response -eq 201 ]]; then
    echo "SSH key added to GitHub successfully."
elif [[ $response -eq 401 ]]; then
    echo "Authentication failed. Please check your personal access token."
elif [[ $response -eq 404 ]]; then
    echo "API endpoint not found. Please ensure you're using a valid token with the 'write:public_key' scope."
else
    echo "Failed to add SSH key to GitHub. HTTP status code: $response"
fi

echo "You can now use SSH with GitHub repositories."
