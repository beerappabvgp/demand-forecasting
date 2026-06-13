output "lambda_function_name" {
  description = "Name of the scheduler Lambda function (use this to invoke manually)"
  value       = aws_lambda_function.scheduler.function_name
}

output "lambda_function_arn" {
  description = "ARN of the scheduler Lambda function"
  value       = aws_lambda_function.scheduler.arn
}

output "stop_schedule" {
  description = "Cron schedule for stop (UTC)"
  value       = aws_cloudwatch_event_rule.stop_schedule.schedule_expression
}

output "start_schedule" {
  description = "Cron schedule for start (UTC)"
  value       = aws_cloudwatch_event_rule.start_schedule.schedule_expression
}
