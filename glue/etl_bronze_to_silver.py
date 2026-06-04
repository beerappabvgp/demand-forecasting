import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME", "bronze_bucket", "silver_bucket"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

BRONZE_PATH = f"s3://{args['bronze_bucket']}/raw/"
SILVER_PATH = f"s3://{args['silver_bucket']}/processed/"

print(f"Reading raw data from: {BRONZE_PATH}")
df = spark.read.parquet(BRONZE_PATH)

print(f"Raw row count: {df.count()}")

df_clean = (
    df
    .fillna(0)
    .dropDuplicates()
    .filter(F.col("sales").isNotNull())
    .filter(F.col("date").isNotNull())
)

print(f"Cleaned row count: {df_clean.count()}")
print(f"Writing processed data to: {SILVER_PATH}")

df_clean.write.mode("overwrite").parquet(SILVER_PATH)

print("ETL job complete.")
job.commit()
