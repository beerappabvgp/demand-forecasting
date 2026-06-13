variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "ecs_service_name" {
  description = "Name of the ECS service to start/stop"
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet ID where NAT Gateway will be (re)created"
  type        = string
}

variable "route_table_id" {
  description = "Private route table ID to update with NAT GW route"
  type        = string
}

variable "initial_nat_gw_id" {
  description = "Current NAT Gateway ID (used to seed SSM on first apply)"
  type        = string
}

variable "nat_eip_allocation_id" {
  description = "Elastic IP allocation ID to reuse for NAT Gateway each morning"
  type        = string
}
