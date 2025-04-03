#!/usr/bin/env python3
"""
Deployment script for Financial Document Analysis System
"""

import os
import sys
import subprocess
import boto3
import uuid
from datetime import datetime

def run_command(command, exit_on_error=True):
    """Run a shell command and print output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, text=True)
    if exit_on_error and result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result.returncode == 0

def main():
    # Set up variables
    stack_name = os.environ.get('STACK_NAME', 'financial-docs-analyzer')
    env_name = os.environ.get('ENV_NAME', 'dev')
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Deploy CloudFormation stack
    print("\n🚀 Deploying CloudFormation stack...")
    template_file = os.path.join(os.path.dirname(__file__), 'cloudformation-template.yaml')
    
    deploy_command = (
        f"aws cloudformation deploy "
        f"--template-file {template_file} "
        f"--stack-name {stack_name}-{env_name} "
        f"--parameter-overrides "
        f"EnvironmentName={env_name} "
        f"--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM "
        f"--region {aws_region}"
    )
    
    if not run_command(deploy_command):
        print("❌ CloudFormation deployment failed")
        sys.exit(1)
    
    # Get stack outputs
    print("\n📊 Getting deployment information...")
    try:
        cf = boto3.client('cloudformation')
        response = cf.describe_stacks(StackName=f"{stack_name}-{env_name}")
        outputs = response['Stacks'][0]['Outputs']
        
        app_url = next((o['OutputValue'] for o in outputs if o['OutputKey'] == 'ApplicationURL'), None)
        if app_url:
            print(f"\n🎉 Deployment successful! Your application is available at:")
            print(f"{app_url}")
            print("\nNote: It may take a few minutes for the application to become fully available.")
        else:
            print("⚠️ Deployment completed but couldn't find Application URL.")
    except Exception as e:
        print(f"❌ Error getting stack outputs: {e}")
    
    print("\n✅ Deployment process completed!")

if __name__ == "__main__":
    main()
