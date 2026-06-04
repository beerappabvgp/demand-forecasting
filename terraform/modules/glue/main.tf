resource "aws_s3_object" "glue_script" {
  bucket = var.mlflow_bucket
  key    = "glue-scripts/etl_bronze_to_silver.py"
  source = "${path.root}/../glue/etl_bronze_to_silver.py"
  etag   = filemd5("${path.root}/../glue/etl_bronze_to_silver.py")
}

resource "aws_glue_job" "etl" {
  name     = "${var.project_name}-etl-bronze-to-silver"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.mlflow_bucket}/glue-scripts/etl_bronze_to_silver.py"
    python_version  = "3"
  }

  default_arguments = {
    "--bronze_bucket"             = var.bronze_bucket
    "--silver_bucket"             = var.silver_bucket
    "--job-language"              = "python"
    "--enable-continuous-cloudwatch-log" = "true"
  }

  glue_version      = "4.0"
  number_of_workers = 2
  worker_type       = "G.1X"
  timeout           = 60
}
