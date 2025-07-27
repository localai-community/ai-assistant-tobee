output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = "${aws_api_gateway_deployment.main.invoke_url}"
}

output "backend_endpoint" {
  description = "Backend API endpoint"
  value       = "${aws_api_gateway_deployment.main.invoke_url}/backend"
}

output "frontend_endpoint" {
  description = "Frontend API endpoint"
  value       = "${aws_api_gateway_deployment.main.invoke_url}/frontend"
}

output "backend_lambda_function_name" {
  description = "Name of the backend Lambda function"
  value       = aws_lambda_function.backend_container.function_name
}

output "frontend_lambda_function_name" {
  description = "Name of the frontend Lambda function"
  value       = aws_lambda_function.frontend_container.function_name
}

output "backend_lambda_arn" {
  description = "ARN of the backend Lambda function"
  value       = aws_lambda_function.backend_container.arn
}

output "frontend_lambda_arn" {
  description = "ARN of the frontend Lambda function"
  value       = aws_lambda_function.frontend_container.arn
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "backend_ecr_repository_url" {
  description = "URL of the backend ECR repository"
  value       = aws_ecr_repository.backend.repository_url
}

output "frontend_ecr_repository_url" {
  description = "URL of the frontend ECR repository"
  value       = aws_ecr_repository.frontend.repository_url
}

output "lambda_security_group_id" {
  description = "ID of the Lambda security group"
  value       = aws_security_group.lambda.id
} 