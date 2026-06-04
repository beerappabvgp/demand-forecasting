output "vpc_id" {
  description = "The ID of the custom VPC"
  value       = module.vpc.vpc_id
}

output "public_subnets" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnets" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "s3_bronze_bucket" {
  description = "Name of the S3 Bronze Bucket (Landing)"
  value       = module.s3.bronze_bucket_name
}

output "s3_silver_bucket" {
  description = "Name of the S3 Silver Bucket (Processed)"
  value       = module.s3.silver_bucket_name
}

output "s3_mlflow_bucket" {
  description = "Name of the S3 MLflow Artifacts Bucket"
  value       = module.s3.mlflow_bucket_name
}

output "ecr_serving_url" {
  description = "Registry URL for ECR Serving Repository"
  value       = module.ecr.repository_url
}

output "iam_glue_role_arn" {
  description = "IAM Role ARN for AWS Glue Service"
  value       = module.iam.glue_role_arn
}

output "iam_sagemaker_role_arn" {
  description = "IAM Role ARN for AWS SageMaker Service"
  value       = module.iam.sagemaker_role_arn
}

output "glue_job_name" {
  description = "Name of the AWS Glue ETL Job"
  value       = module.glue.glue_job_name
}
