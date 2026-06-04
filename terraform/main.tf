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
