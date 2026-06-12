variable "project_name" {
  type        = string
  description = "Project name"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of private subnets for ECS tasks"
}

variable "ecs_sg_id" {
  type        = string
  description = "Security Group ID for ECS tasks"
}

variable "target_group_arn" {
  type        = string
  description = "ARN of the ALB target group"
}

variable "ecs_execution_role_arn" {
  type        = string
  description = "ARN of the ECS execution role"
}

variable "ecs_autoscale_role_arn" {
  type        = string
  description = "ARN of the application autoscaling role"
}

variable "ecr_repository_url" {
  type        = string
  description = "URL of the ECR repository"
}
