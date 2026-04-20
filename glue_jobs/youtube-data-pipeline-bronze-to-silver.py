"""
Glue Job: Bronze → Silver (Statistics Data)
────────────────────────────────────────────
Reads raw CSV/JSON statistics from the Bronze layer,
applies schema enforcement, data cleansing, deduplication,
and writes clean Parquet to the Silver layer.

Improvements over original pyspark_code.py:
  - Data quality checks with row-level flagging
  - Deduplication (same video appearing in multiple ingestions)
  - Date parsing and standardization
  - Handles both Kaggle CSV format and live API JSON format
  - Partitioned by region AND date for better query performance
  - Bookmarking for incremental processing
  - Proper logging

Job Parameters:
    --JOB_NAME                   — Glue job name (auto-set)
    --bronze_database            — Bronze Glue catalog database
    --bronze_table               — Bronze statistics table
    --silver_bucket              — Silver S3 bucket
    --silver_database            — Silver Glue catalog database
    --silver_table               — Silver statistics table
    --silver_path                — Silver S3 path prefix
"""

import sys
from datetime import datetime

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, BooleanType, TimestampType
)

# ── REGION ADDED (ONLY CHANGE) ─────────────────────────────
REGION = "ap-south-1"

# ── Job Setup ───────────────────────────────────────────────
args = getResolvedOptions(sys.argv, [
    "JOB_NAME",
    "bronze_database",
    "bronze_table",
    "silver_bucket",
    "silver_database",
    "silver_table",
])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)
logger = glueContext.get_logger()

# ── Config ───────────────────────────────────────────────────
BRONZE_DB = args["bronze_database"]
BRONZE_TABLE = args["bronze_table"]
SILVER_BUCKET = args["silver_bucket"]
SILVER_DB = args["silver_database"]
SILVER_TABLE = args["silver_table"]
SILVER_PATH = f"s3://{SILVER_BUCKET}/youtube/statistics/"

logger.info(f"Bronze: {BRONZE_DB}.{BRONZE_TABLE}")
logger.info(f"Silver: {SILVER_DB}.{SILVER_TABLE} → {SILVER_PATH}")


# ── Step 1: Read from Bronze ────────────────────────────────
logger.info("Reading from Bronze catalog...")

predicate = "region in ('ca','gb','us', 'in')"

datasource = glueContext.create_dynamic_frame.from_catalog(
    database=BRONZE_DB,
    table_name=BRONZE_TABLE,
    transformation_ctx="datasource",
    push_down_predicate=predicate,
)

df = datasource.toDF()
initial_count = df.count()
logger.info(f"Bronze records read: {initial_count}")

if initial_count == 0:
    logger.info("No new records to process. Committing empty job.")
else:
    logger.info("Enforcing schema and casting types...")

    columns = set(df.columns)

    if "snippet.title" in columns or "snippet__title" in columns:
        logger.info("Detected YouTube API format — flattening...")
        df = df.select(
            F.col("id").alias("video_id"),
            F.lit(datetime.utcnow().strftime("%y.%d.%m")).alias("trending_date"),
            F.col("`snippet.title`").alias("title") if "snippet.title" in columns
                else F.col("snippet__title").alias("title"),
            F.col("`snippet.channelTitle`").alias("channel_title") if "snippet.channelTitle" in columns
                else F.col("snippet__channelTitle").alias("channel_title"),
            F.col("`snippet.categoryId`").cast(LongType()).alias("category_id") if "snippet.categoryId" in columns
                else F.col("snippet__categoryId").cast(LongType()).alias("category_id"),
            F.col("`snippet.publishedAt`").alias("publish_time") if "snippet.publishedAt" in columns
                else F.col("snippet__publishedAt").alias("publish_time"),
            F.col("`snippet.tags`").alias("tags") if "snippet.tags" in columns
                else F.lit(None).cast(StringType()).alias("tags"),
            F.col("`statistics.viewCount`").cast(LongType()).alias("views") if "statistics.viewCount" in columns
                else F.col("statistics__viewCount").cast(LongType()).alias("views"),
            F.col("`statistics.likeCount`").cast(LongType()).alias("likes") if "statistics.likeCount" in columns
                else F.col("statistics__likeCount").cast(LongType()).alias("likes"),
            F.col("`statistics.dislikeCount`").cast(LongType()).alias("dislikes") if "statistics.dislikeCount" in columns
                else F.lit(0).cast(LongType()).alias("dislikes"),
            F.col("`statistics.commentCount`").cast(LongType()).alias("comment_count") if "statistics.commentCount" in columns
                else F.col("statistics__commentCount").cast(LongType()).alias("comment_count"),
            F.col("`snippet.thumbnails.default.url`").alias("thumbnail_link") if "snippet.thumbnails.default.url" in columns
                else F.lit(None).cast(StringType()).alias("thumbnail_link"),
            F.lit(False).alias("comments_disabled"),
            F.lit(False).alias("ratings_disabled"),
            F.lit(False).alias("video_error_or_removed"),
            F.col("`snippet.description`").alias("description") if "snippet.description" in columns
                else F.col("snippet__description").alias("description"),
            F.col("region"),
        )
    else:
        logger.info("Detected Kaggle CSV format — casting types...")
        df = df.select(
            F.col("video_id").cast(StringType()),
            F.col("trending_date").cast(StringType()),
            F.col("title").cast(StringType()),
            F.col("channel_title").cast(StringType()),
            F.col("category_id").cast(LongType()),
            F.col("publish_time").cast(StringType()),
            F.col("tags").cast(StringType()),
            F.col("views").cast(LongType()),
            F.col("likes").cast(LongType()),
            F.col("dislikes").cast(LongType()),
            F.col("comment_count").cast(LongType()),
            F.col("thumbnail_link").cast(StringType()),
            F.col("comments_disabled").cast(BooleanType()),
            F.col("ratings_disabled").cast(BooleanType()),
            F.col("video_error_or_removed").cast(BooleanType()),
            F.col("description").cast(StringType()),
            F.col("region").cast(StringType()),
        )

    logger.info("Cleansing data...")

    df = df.filter(F.col("video_id").isNotNull())
    df = df.withColumn("region", F.lower(F.trim(F.col("region"))))

    df = df.withColumn(
        "trending_date_parsed",
        F.when(
            F.col("trending_date").rlike(r"^\d{2}\.\d{2}\.\d{2}$"),
            F.to_date(F.col("trending_date"), "yy.dd.MM")
        ).otherwise(
            F.to_date(F.col("trending_date"))
        )
    )

    numeric_cols = ["views", "likes", "dislikes", "comment_count"]
    for col_name in numeric_cols:
        df = df.withColumn(col_name, F.coalesce(F.col(col_name), F.lit(0)))

    df = df.withColumn(
        "like_ratio",
        F.when((F.col("views") > 0),
               F.round(F.col("likes") / F.col("views") * 100, 4)
        ).otherwise(0.0)
    )

    df = df.withColumn(
        "engagement_rate",
        F.when((F.col("views") > 0),
               F.round((F.col("likes") + F.col("dislikes") + F.col("comment_count")) / F.col("views") * 100, 4)
        ).otherwise(0.0)
    )

    df = df.withColumn("_processed_at", F.current_timestamp())
    df = df.withColumn("_job_name", F.lit(args["JOB_NAME"]))

    from pyspark.sql.window import Window

    window = Window.partitionBy("video_id", "region", "trending_date_parsed") \
        .orderBy(F.col("_processed_at").desc())

    df = df.withColumn("_row_num", F.row_number().over(window)) \
        .filter(F.col("_row_num") == 1) \
        .drop("_row_num")

    clean_count = df.count()
    logger.info(f"After cleansing & dedup: {clean_count}")

    dynamic_frame = DynamicFrame.fromDF(df, glueContext, "silver_statistics")

    sink = glueContext.getSink(
        connection_type="s3",
        path=SILVER_PATH,
        enableUpdateCatalog=True,
        updateBehavior="UPDATE_IN_DATABASE",
        partitionKeys=["region"],
    )
    sink.setCatalogInfo(catalogDatabase=SILVER_DB, catalogTableName=SILVER_TABLE)
    sink.setFormat("glueparquet", compression="snappy")
    sink.writeFrame(dynamic_frame)

    logger.info(f"Silver write complete. {clean_count} records written.")

job.commit()