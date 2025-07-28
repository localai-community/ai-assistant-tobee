# Docker image build and push resources
resource "null_resource" "backend_image" {
  triggers = {
    dockerfile_hash = filemd5("${path.module}/Dockerfile.backend")
    source_hash     = filemd5("${path.root}/../backend/requirements.txt")
  }

  provisioner "local-exec" {
    command = <<-EOT
      # Login to ECR
      aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
      
      # Build and push backend image
      docker build -f ${path.module}/Dockerfile.backend -t ${aws_ecr_repository.backend.repository_url}:latest ${path.root}
      docker push ${aws_ecr_repository.backend.repository_url}:latest
    EOT
  }

  depends_on = [aws_ecr_repository.backend]
}

resource "null_resource" "frontend_image" {
  triggers = {
    dockerfile_hash = filemd5("${path.module}/Dockerfile.frontend")
    source_hash     = filemd5("${path.root}/../frontend/requirements.txt")
  }

  provisioner "local-exec" {
    command = <<-EOT
      # Login to ECR
      aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
      
      # Build and push frontend image
      docker build -f ${path.module}/Dockerfile.frontend -t ${aws_ecr_repository.frontend.repository_url}:latest ${path.root}
      docker push ${aws_ecr_repository.frontend.repository_url}:latest
    EOT
  }

  depends_on = [aws_ecr_repository.frontend]
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Containerized Lambda functions using ECR images
resource "aws_lambda_function" "backend_container" {
  function_name = "${var.project_name}-backend-container"
  role          = aws_iam_role.lambda_backend.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.backend.repository_url}:latest"
  timeout       = var.backend_timeout
  memory_size   = var.backend_memory_size

  environment {
    variables = {
      ENVIRONMENT = var.environment
      LOG_LEVEL  = var.log_level
    }
  }

  vpc_config {
    subnet_ids         = data.aws_subnets.default.ids
    security_group_ids = [aws_security_group.lambda.id]
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_backend_basic,
    null_resource.backend_image
  ]
}

resource "aws_lambda_function" "frontend_container" {
  function_name = "${var.project_name}-frontend-container"
  role          = aws_iam_role.lambda_frontend.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.frontend.repository_url}:latest"
  timeout       = var.frontend_timeout
  memory_size   = var.frontend_memory_size

  environment {
    variables = {
      ENVIRONMENT = var.environment
      LOG_LEVEL  = var.log_level
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_frontend_basic,
    null_resource.frontend_image
  ]
}

# Additional IAM permissions for ECR access
resource "aws_iam_role_policy" "lambda_ecr_access" {
  name = "${var.project_name}-lambda-ecr-access"
  role = aws_iam_role.lambda_backend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_vpc_access" {
  name = "${var.project_name}-lambda-vpc-access"
  role = aws_iam_role.lambda_backend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AssignPrivateIpAddresses",
          "ec2:UnassignPrivateIpAddresses"
        ]
        Resource = "*"
      }
    ]
  })
}

# Container-specific API Gateway integrations
resource "aws_api_gateway_integration" "backend_container" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.backend.id
  http_method = aws_api_gateway_method.backend_any.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.backend_container.invoke_arn
}

resource "aws_api_gateway_integration" "backend_container_proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.backend_proxy.id
  http_method = aws_api_gateway_method.backend_proxy_any.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.backend_container.invoke_arn
}

resource "aws_api_gateway_integration" "frontend_container" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.frontend.id
  http_method = aws_api_gateway_method.frontend_any.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.frontend_container.invoke_arn
}

resource "aws_api_gateway_integration" "frontend_container_proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.frontend_proxy.id
  http_method = aws_api_gateway_method.frontend_proxy_any.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.frontend_container.invoke_arn
}

# Lambda permissions for containerized functions
resource "aws_lambda_permission" "backend_container" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.backend_container.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "frontend_container" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.frontend_container.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
} 