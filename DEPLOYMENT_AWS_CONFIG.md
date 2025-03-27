# Required AWS Configuration for Deployment

This document outlines the manual configuration required within AWS for the `financial-docs` Elastic Beanstalk environment (`financial-docs-env`) to function correctly after deployment via the GitHub Actions workflow (`deploy-to-eb.yml`).

## 1. Elastic Beanstalk Environment Properties

The following environment variables need to be set directly on the `financial-docs-env` Elastic Beanstalk environment configuration. **Do not commit sensitive values to the repository.**

*   **`MONGO_URI`**: The full connection string for the production MongoDB database.
    *   Example: `mongodb+srv://<user>:<password>@<cluster-address>/<database_name>?retryWrites=true&w=majority`
*   **`SQLALCHEMY_DATABASE_URI`**: The full connection string for the production relational database (if used alongside or instead of MongoDB).
    *   Example (PostgreSQL): `postgresql://<user>:<password>@<host>:<port>/<database_name>`

## 2. Secrets Management (SSM Parameter Store Recommended)

Sensitive configuration values should be stored securely in AWS Systems Manager (SSM) Parameter Store as `SecureString` parameters in the `eu-central-1` region. The `.ebextensions/01-environment.config` file is configured to fetch these during deployment.

*   **`SECRET_KEY`**: A long, random string used by Flask for session security.
*   **`JWT_SECRET`**: A long, random string used for signing JWT tokens.
*   **`HUGGINGFACE_API_KEY`**: Your Hugging Face API key for accessing AI models.
*   **`OPENAI_API_KEY`** (Optional): Your OpenAI API key if you intend to use OpenAI models.
*   **`MISTRAL_API_KEY`** (Optional): Your Mistral API key if you intend to use Mistral models.
*   _(Add any other required secrets like database credentials if not included in the URI, external API keys, etc.)_

**Note:** If you prefer to set these secrets directly as Elastic Beanstalk environment properties (less secure), you would need to modify `.ebextensions/01-environment.config` to remove the `container_commands` section that fetches them from SSM.

## 3. IAM Permissions for EC2 Instance Profile

The IAM role attached to the EC2 instances running within the Elastic Beanstalk environment (the "Instance Profile Role") **MUST** have permissions to access the secrets stored in SSM Parameter Store if using the `container_commands` method described above.

*   **Required Permission:** `ssm:GetParameter`
*   **Resource:** The ARN(s) of the specific SSM parameters being accessed (e.g., `arn:aws:ssm:eu-central-1:<account-id>:parameter/SECRET_KEY`, `arn:aws:ssm:eu-central-1:<account-id>:parameter/JWT_SECRET`, etc.). It's recommended to scope this permission as narrowly as possible.

## 4. Security Group Configuration

The Security Group associated with the Elastic Beanstalk environment **MUST** allow:

*   **Inbound Traffic:** On the port the application listens on (Port `10000` as configured) from the Elastic Load Balancer.
*   **Outbound Traffic:**
    *   On port `443` (HTTPS) to allow connections to external APIs (Hugging Face, OpenAI, AWS services like SSM and DynamoDB).
    *   On the relevant port(s) for your database (e.g., `27017` for MongoDB Atlas, `5432` for PostgreSQL) if it's hosted outside the VPC or requires specific outbound rules.

## 5. Database Accessibility

Ensure that the database (MongoDB or relational) is:

*   Running and operational.
*   Accessible from the VPC and subnet(s) where the Elastic Beanstalk environment is deployed. This might involve configuring database security groups, network ACLs, or VPC peering.

## 6. Confirm Docker Solution Stack Name

Before triggering the deployment workflow, verify the latest valid Docker platform solution stack name for Amazon Linux 2023 in the `eu-central-1` region using the AWS CLI:

```bash
aws elasticbeanstalk list-available-solution-stacks --region eu-central-1 --output text | grep "Docker" | grep "Amazon Linux 2023"
```

Update the `--solution-stack-name` value in `.github/workflows/deploy-to-eb.yml` (line ~98) with the latest appropriate name found.