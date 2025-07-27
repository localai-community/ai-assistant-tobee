# AI Assistant Infrastructure

This directory contains OpenTofu scripts for deploying the AI Assistant solution as containerized Lambda functions on AWS.

## Architecture Overview

The infrastructure deploys:
- **Backend Lambda Function**: Containerized Python application with RAG and reasoning capabilities
- **Frontend Lambda Function**: Containerized Python web application
- **API Gateway**: REST API for routing requests to Lambda functions
- **VPC**: Private networking for Lambda functions with NAT Gateway
- **ECR Repositories**: Container image storage for backend and frontend
- **IAM Roles**: Security permissions for Lambda execution

## Prerequisites

1. **AWS CLI** installed and configured with appropriate credentials
2. **OpenTofu** installed (v1.0 or later)
3. **Docker** installed and running
4. **AWS Account** with appropriate permissions

## Quick Start

### 1. Configure Environment

**Option A: Use .env file (Recommended)**
```bash
# Run the setup script to create .env file
./setup-env.sh

# Or manually copy and edit
cp .env.example .env
nano .env
```

**Option B: Configure AWS Credentials**
```bash
# Configure default profile
aws configure

# Or configure a specific profile
aws configure --profile my-profile
```

**Note:** The deployment scripts will automatically load configuration from the `.env` file, or use `AWS_PROFILE` and `AWS_REGION` environment variables if they're set externally.

### 2. Deploy Infrastructure

```bash
./deploy.sh
```

This script will:
- Initialize OpenTofu
- Create all AWS resources
- Build and push Docker images to ECR
- Deploy Lambda functions with container images

### 3. Access the Application

After deployment, you'll get URLs for:
- API Gateway: `https://[api-id].execute-api.[region].amazonaws.com/dev`
- Backend endpoint: `https://[api-id].execute-api.[region].amazonaws.com/dev/backend`
- Frontend endpoint: `https://[api-id].execute-api.[region].amazonaws.com/dev/frontend`

## Manual Deployment

### Initialize OpenTofu

```bash
cd infrastructure
tofu init
```

### Plan Deployment

```bash
tofu plan -var="aws_region=us-east-1" -var="aws_profile=default" -var="project_name=ai-assistant" -var="environment=dev"
```

### Apply Infrastructure

```bash
tofu apply -var="aws_region=us-east-1" -var="aws_profile=default" -var="project_name=ai-assistant" -var="environment=prod" -auto-approve
```

### Build and Push Docker Images

```bash
# Get ECR repository URLs
BACKEND_ECR_URL=$(tofu output -raw backend_ecr_repository_url)
FRONTEND_ECR_URL=$(tofu output -raw frontend_ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [account-id].dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -f Dockerfile.backend -t ${BACKEND_ECR_URL}:latest .
docker push ${BACKEND_ECR_URL}:latest

# Build and push frontend
docker build -f Dockerfile.frontend -t ${FRONTEND_ECR_URL}:latest .
docker push ${FRONTEND_ECR_URL}:latest
```

## Configuration

### Variables

Edit `variables.tf` or pass variables via command line:

- `aws_region`: AWS region for deployment (default: us-east-1)
- `aws_profile`: AWS profile to use (default: default)
- `project_name`: Project name for resource naming (default: ai-assistant)
- `environment`: Environment name (default: dev)
- `log_level`: Log level for Lambda functions (default: INFO)
- `backend_timeout`: Backend Lambda timeout in seconds (default: 900)
- `frontend_timeout`: Frontend Lambda timeout in seconds (default: 30)
- `backend_memory_size`: Backend Lambda memory in MB (default: 2048)
- `frontend_memory_size`: Frontend Lambda memory in MB (default: 512)

### Environment Configuration

The deployment scripts support multiple ways to configure the environment:

**Option 1: Use .env file (Recommended)**
```bash
# Copy and edit the environment file
cp .env.example .env
nano .env

# Deploy
./deploy.sh
```

**Option 2: Use Environment Variables**
```bash
export AWS_PROFILE=my-profile
export AWS_REGION=us-west-2
export ENVIRONMENT=dev
./deploy.sh
```

**Option 3: Use Command Line Variables**
```bash
tofu apply -var="aws_profile=my-profile" -var="aws_region=us-west-2" -var="project_name=ai-assistant" -var="environment=dev" -auto-approve
```

**Option 4: Use terraform.tfvars**
Create `infrastructure/terraform.tfvars`:
```hcl
aws_region  = "us-west-2"
aws_profile = "my-profile"
project_name = "ai-assistant"
environment = "dev"
```

**Configuration Priority:**
The scripts use the following priority order:
1. `.env` file variables (if file exists)
2. Environment variables (if set)
3. Default values

**Examples:**

**Using .env files for different environments:**
```bash
# Development environment
cp .env.example .env.dev
# Edit .env.dev with dev settings
ENV_FILE=.env.dev ./deploy.sh

# Production environment
cp .env.example .env.prod
# Edit .env.prod with prod settings
ENV_FILE=.env.prod ./deploy.sh
```

**Using environment variables:**
```bash
# Deploy to different regions
export AWS_REGION=us-west-2 && ./deploy.sh
export AWS_REGION=eu-west-1 && ./deploy.sh
export AWS_REGION=ap-southeast-1 && ./deploy.sh

# Deploy with different profiles and regions
export AWS_PROFILE=dev && export AWS_REGION=us-east-1 && ./deploy.sh
export AWS_PROFILE=staging && export AWS_REGION=us-west-2 && ./deploy.sh
export AWS_PROFILE=prod && export AWS_REGION=eu-west-1 && ./deploy.sh
```

### Environment-Specific Deployments

For production deployment:

```bash
tofu apply -var="aws_region=us-east-1" -var="aws_profile=default" -var="project_name=ai-assistant" -var="environment=prod" -var="backend_memory_size=4096" -auto-approve
```

## Monitoring and Logs

### CloudWatch Logs

Lambda function logs are automatically sent to CloudWatch:
- Backend: `/aws/lambda/ai-assistant-backend-container`
- Frontend: `/aws/lambda/ai-assistant-frontend-container`

### API Gateway Monitoring

Monitor API usage and errors in the AWS Console under API Gateway.

## Security

### IAM Permissions

The Lambda functions have minimal required permissions:
- Basic Lambda execution role
- ECR access for container images
- VPC access for networking

### Network Security

- Lambda functions run in private subnets
- NAT Gateway provides internet access
- Security groups restrict traffic appropriately

## Cleanup

### Destroy Infrastructure

```bash
./destroy.sh
```

Or manually:

```bash
cd infrastructure
tofu destroy -var="aws_region=us-east-1" -var="aws_profile=default" -var="project_name=ai-assistant" -var="environment=dev" -auto-approve
```

## Troubleshooting

### Common Issues

1. **Docker Build Failures**
   - Ensure Docker is running
   - Check Dockerfile syntax
   - Verify requirements.txt exists

2. **ECR Push Failures**
   - Ensure AWS credentials are configured
   - Check ECR repository exists
   - Verify Docker login to ECR

3. **Lambda Timeout**
   - Increase timeout in variables
   - Check Lambda logs in CloudWatch
   - Verify container image size

4. **API Gateway Errors**
   - Check Lambda function status
   - Verify API Gateway integration
   - Review CloudWatch logs

### Debugging

1. **Check Lambda Logs**
   ```bash
   aws logs tail /aws/lambda/ai-assistant-backend-container --follow
   ```

2. **Test API Endpoints**
   ```bash
   curl -X POST https://[api-id].execute-api.[region].amazonaws.com/dev/backend/health
   ```

3. **Verify Infrastructure**
   ```bash
   tofu plan
   tofu show
   ```

## Cost Optimization

- Use appropriate memory sizes for Lambda functions
- Consider using provisioned concurrency for production
- Monitor CloudWatch metrics for optimization opportunities
- Use AWS Cost Explorer to track spending

## Scaling

The solution automatically scales based on demand:
- Lambda functions scale from 0 to thousands of concurrent executions
- API Gateway handles traffic spikes automatically
- Consider using Application Load Balancer for more complex routing needs

## Support

For issues or questions:
1. Check CloudWatch logs first
2. Review OpenTofu state and plan
3. Verify AWS service quotas and limits
4. Consult AWS documentation for service-specific issues 