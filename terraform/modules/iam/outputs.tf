output "glue_role_arn" {
  value = aws_iam_role.glue_role.arn
}

output "sagemaker_role_arn" {
  value = aws_iam_role.sagemaker_role.arn
}
