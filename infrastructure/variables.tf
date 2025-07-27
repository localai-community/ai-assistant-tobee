variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "eu-central-1"
}

variable "aws_profile" {
  description = "AWS profile to use for deployment"
  type        = string
  default     = "default"
}

variable "project_name" {
  description = "Name of the project for resource naming"
  type        = string
  default     = "ai-assistant"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "log_level" {
  description = "Log level for Lambda functions"
  type        = string
  default     = "INFO"
}

variable "backend_timeout" {
  description = "Timeout for backend Lambda function in seconds"
  type        = number
  default     = 900
}

variable "frontend_timeout" {
  description = "Timeout for frontend Lambda function in seconds"
  type        = number
  default     = 30
}

variable "backend_memory_size" {
  description = "Memory size for backend Lambda function in MB"
  type        = number
  default     = 2048
}

variable "frontend_memory_size" {
  description = "Memory size for frontend Lambda function in MB"
  type        = number
  default     = 512
}

 