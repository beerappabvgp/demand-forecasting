resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "aws_s3_bucket" "bronze" {
  bucket        = "${var.project_name}-${var.environment}-bronze-${random_string.suffix.result}"
  force_destroy = true
}

resource "aws_s3_bucket" "silver" {
  bucket        = "${var.project_name}-${var.environment}-silver-${random_string.suffix.result}"
  force_destroy = true
}

resource "aws_s3_bucket" "mlflow" {
  bucket        = "${var.project_name}-${var.environment}-mlflow-${random_string.suffix.result}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "bronze_acl" {
  bucket                  = aws_s3_bucket.bronze.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "silver_acl" {
  bucket                  = aws_s3_bucket.silver.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "mlflow_acl" {
  bucket                  = aws_s3_bucket.mlflow.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
