output "bronze_bucket_name" {
  value = aws_s3_bucket.bronze.id
}

output "bronze_bucket_arn" {
  value = aws_s3_bucket.bronze.arn
}

output "silver_bucket_name" {
  value = aws_s3_bucket.silver.id
}

output "silver_bucket_arn" {
  value = aws_s3_bucket.silver.arn
}

output "mlflow_bucket_name" {
  value = aws_s3_bucket.mlflow.id
}

output "mlflow_bucket_arn" {
  value = aws_s3_bucket.mlflow.arn
}
