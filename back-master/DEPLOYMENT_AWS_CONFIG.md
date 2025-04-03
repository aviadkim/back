# Required AWS Configuration for Deployment

This document outlines the manual configuration steps required in AWS for the `financial-docs` Elastic Beanstalk application deployment to function correctly.

## 1. Elastic Beanstalk Environment Properties

The following environment variables need to be set directly on the `financial-docs-env` Elastic Beanstalk environment configuration:

*   **`MONGO_URI`**: The full connection string for the production MongoDB database.
    *   Example: `mongodb+srv://<user>:<password>@<cluster-host>/<database_name>?retryWrites=true&w=majority`
*   **`SQLALCHEMY_DATABASE_URI`**: The full connection string for the production relational database (if used).
    *   Example: `postgresql://<user>:<password>@<host>:<port>/<database_name>`

    *(Note: Configure only the database type(s) actually used by the application)*

## 2. Secrets Management (SSM Parameter Store)

The application fetches secrets from AWS Systems Manager (SSM) Parameter Store using the `container_command` in `.ebextensions/01-environment.config`. The following parameters **must** be created in SSM Parameter Store in the `eu-central-1` region:

*   **`SECRET_KEY`**: (Type: `SecureString`) A strong, random secret key for Flask session management, CSRF protection, etc.
*   **`JWT_SECRET`**: (Type: `SecureString`) A strong, random secret key for signing JWT tokens.
*   **`HUGGINGFACE_API_KEY`**: (Type: `SecureString`) Your Hugging Face API key (if using Hugging Face models).
*   **`OPENAI_API_KEY`**: (Type: `SecureString`) Your OpenAI API key (if using OpenAI models).

*(Note: Add/remove parameters based on the actual secrets required by the application)*

## 3. IAM Permissions (EC2 Instance Profile Role)

The IAM Role attached to the EC2 instances running within the Elastic Beanstalk environment (the "Instance Profile Role") **MUST** have the following permissions:

*   **`ssm:GetParameter`**: Required to allow the `container_command` to fetch the secrets listed above from SSM Parameter Store. The permission should be scoped to the specific parameter names (e.g., `arn:aws:ssm:eu-central-1:<account-id>:parameter/SECRET_KEY`, `arn:aws:ssm:eu-central-1:<account-id>:parameter/JWT_SECRET`, etc.).

## 4. Security Group Configuration

The Security Group associated with the Elastic Beanstalk environment **MUST** allow:

*   **Inbound Traffic:** Allow traffic on the port the application listens on (Port `10000` as configured) from necessary sources (e.g., your load balancer, specific IPs).
*   **Outbound Traffic:**
    *   Allow outbound connections on port `443` (HTTPS) to external APIs (e.g., Hugging Face, OpenAI, SSM, database endpoints).
    *   Allow outbound connections to your database (MongoDB or relational) on its specific port(s) if it's hosted outside the EB environment VPC.

## 5. Database Accessibility

Ensure that the database(s) (MongoDB, PostgreSQL, etc.) are running and configured to allow network connections from the VPC/subnets used by the Elastic Beanstalk environment. This might involve configuring database security groups, network ACLs, or VPC peering.