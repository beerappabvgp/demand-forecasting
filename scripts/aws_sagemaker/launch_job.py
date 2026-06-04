import os
from sagemaker.pytorch import PyTorch

# Ensure you have set your AWS credentials in your environment before running
# export AWS_ACCESS_KEY_ID=...
# export AWS_SECRET_ACCESS_KEY=...
# export AWS_DEFAULT_REGION=ap-south-1

ROLE_ARN = "arn:aws:iam::473469900710:role/demand-forecasting-sagemaker-execution-role"
SILVER_BUCKET = "demand-forecasting-production-silver-3lhyuk"

estimator = PyTorch(
    entry_point="train.py",
    source_dir="sagemaker_bundle",  # Only 492KB — just src/ + train.py, no .venv!
    role=ROLE_ARN,
    framework_version="2.0.0",
    py_version="py310",
    instance_count=1,
    instance_type="ml.m5.xlarge",
    hyperparameters={
        "epochs": 1,
        "batch_size": 256,
        "seq_len": 14,
        "learning_rate": 0.0001
    }
)

print("Launching SageMaker Training Job...")
estimator.fit({
    "train": f"s3://{SILVER_BUCKET}/processed/",
    "val": f"s3://{SILVER_BUCKET}/processed/"
})
print("Training Job Completed!")
