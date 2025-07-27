terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "opentofu"
    }
  }
}

# ECR repositories for container images
resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "frontend" {
  name                 = "${var.project_name}-frontend"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
}

# Use default VPC
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Groups
resource "aws_security_group" "lambda" {
  name_prefix = "${var.project_name}-lambda-"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-lambda-sg"
  }
}

# IAM roles for Lambda functions
resource "aws_iam_role" "lambda_backend" {
  name = "${var.project_name}-backend-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "lambda_frontend" {
  name = "${var.project_name}-frontend-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_backend_basic" {
  role       = aws_iam_role.lambda_backend.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_frontend_basic" {
  role       = aws_iam_role.lambda_frontend.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda functions are defined in container-lambda.tf for containerized deployment

# API Gateway
resource "aws_api_gateway_rest_api" "main" {
  name = "${var.project_name}-api"
}

resource "aws_api_gateway_resource" "backend" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "backend"
}

resource "aws_api_gateway_resource" "frontend" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "frontend"
}

# Backend proxy resource
resource "aws_api_gateway_resource" "backend_proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.backend.id
  path_part   = "{proxy+}"
}

# Frontend proxy resource
resource "aws_api_gateway_resource" "frontend_proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.frontend.id
  path_part   = "{proxy+}"
}

# Backend methods
resource "aws_api_gateway_method" "backend_any" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.backend.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "backend_proxy_any" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.backend_proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

# Frontend methods
resource "aws_api_gateway_method" "frontend_any" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.frontend.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "frontend_proxy_any" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.frontend_proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

# Lambda permissions and API Gateway integrations are defined in container-lambda.tf

# API Gateway deployment
resource "aws_api_gateway_deployment" "main" {
  depends_on = [
    aws_api_gateway_integration.backend_container,
    aws_api_gateway_integration.backend_container_proxy,
    aws_api_gateway_integration.frontend_container,
    aws_api_gateway_integration.frontend_container_proxy,
  ]

  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name  = var.environment
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
} 