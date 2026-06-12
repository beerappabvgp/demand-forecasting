output "glue_role_arn" {
  value = aws_iam_role.glue_role.arn
}

output "sagemaker_role_arn" {
  value = aws_iam_role.sagemaker_role.arn
}

output "ecs_execution_role_arn" {
  value = aws_iam_role.ecs_execution_role.arn
}

output "ecs_autoscale_role_arn" {
  value = aws_iam_role.ecs_autoscale_role.arn
}
