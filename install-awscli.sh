#!/bin/bash

# Install AWS CLI v2 on GitHub Codespace
# This script installs AWS CLI v2 on a Linux-based GitHub Codespace

echo "Installing AWS CLI v2..."

# Make a temporary directory for the installation
mkdir -p /tmp/aws-cli
cd /tmp/aws-cli

# Download the AWS CLI v2 installer
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Install unzip if it's not already installed
if ! command -v unzip &> /dev/null; then
    echo "Installing unzip..."
    sudo apt-get update && sudo apt-get install -y unzip
fi

# Unzip the installer
unzip awscliv2.zip

# Install AWS CLI v2
sudo ./aws/install

# Verify the installation
aws --version

# Clean up
cd -
rm -rf /tmp/aws-cli

echo "AWS CLI v2 installation complete!"
echo "You can now run 'aws configure' to set up your AWS credentials."
