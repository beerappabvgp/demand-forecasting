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
      ManagedBy   = "Terraform"
    }
  }
}

module "vpc" {
  source       = "./modules/vpc"
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

module "s3" {
  source       = "./modules/s3"
  project_name = var.project_name
  environment  = var.environment
}

module "ecr" {
  source       = "./modules/ecr"
  project_name = var.project_name
  environment  = var.environment
}

module "iam" {
  source        = "./modules/iam"
  project_name  = var.project_name
  environment   = var.environment
  s3_bronze_arn = module.s3.bronze_bucket_arn
  s3_silver_arn = module.s3.silver_bucket_arn
  s3_mlflow_arn = module.s3.mlflow_bucket_arn
}

module "glue" {
  source        = "./modules/glue"
  project_name  = var.project_name
  environment   = var.environment
  bronze_bucket = module.s3.bronze_bucket_name
  silver_bucket = module.s3.silver_bucket_name
  mlflow_bucket = module.s3.mlflow_bucket_name
  glue_role_arn = module.iam.glue_role_arn
}

module "alb" {
  source            = "./modules/alb"
  project_name      = var.project_name
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  alb_sg_id         = module.vpc.alb_sg_id
}

module "ecs" {
  source                 = "./modules/ecs"
  project_name           = var.project_name
  vpc_id                 = module.vpc.vpc_id
  private_subnet_ids     = module.vpc.private_subnet_ids
  ecs_sg_id              = module.vpc.ecs_sg_id
  target_group_arn       = module.alb.target_group_arn
  ecs_execution_role_arn = module.iam.ecs_execution_role_arn
  ecs_autoscale_role_arn = module.iam.ecs_autoscale_role_arn
  ecr_repository_url     = module.ecr.repository_url
}

module "scheduler" {
  source       = "./modules/scheduler"
  project_name = var.project_name
  aws_region   = var.aws_region

  # ECS targets
  ecs_cluster_name = "${var.project_name}-cluster"
  ecs_service_name = "${var.project_name}-service"

  # NAT Gateway management
  public_subnet_id      = module.vpc.first_public_subnet_id
  route_table_id        = module.vpc.private_route_table_id
  nat_eip_allocation_id = module.vpc.nat_eip_allocation_id
  initial_nat_gw_id     = module.vpc.nat_gateway_id
}
