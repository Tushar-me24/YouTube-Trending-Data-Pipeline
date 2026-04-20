# 🚀 YouTube Trending Data Engineering Pipeline (AWS | End-to-End ETL System)
A production-style cloud data engineering pipeline that ingests YouTube trending video data across 10 global regions, processes it through a Medallion Architecture (Bronze → Silver → Gold), enforces data quality gates, and generates analytics-ready datasets for business insights using AWS services.
<img width="2784" height="1536" alt="image" src="https://github.com/user-attachments/assets/28cd19df-2e58-42fa-9fc8-9411dbc41a3c" />
📌 Key Highlights
🔄 Fully automated end-to-end ETL pipeline
☁️ Built on AWS serverless + distributed architecture
📊 Processes data from YouTube Data API v3 + Kaggle datasets
🧱 Implements Medallion Architecture (Bronze, Silver, Gold)
🧪 Includes data quality validation layer with fail-safe controls
🚨 Real-time failure alerts using AWS SNS
⚡ Orchestrated using AWS Step Functions (state machine)
📈 Query-ready analytics via Amazon Athena
🏗️ Architecture Overview

The pipeline follows a scalable Medallion Architecture:

Bronze Layer → Raw ingestion (YouTube API + Kaggle data)
Silver Layer → Cleaned, validated, and standardized datasets
Data Quality Gate → Validation checkpoints before transformation
Gold Layer → Business-level aggregated analytics tables

Orchestration Flow:

Data ingestion (YouTube API / Kaggle)
Raw storage in S3 (Bronze)
Transformation via AWS Glue & Lambda (Silver)
Data quality validation (DQ Lambda)
Aggregation into analytics tables (Gold)
Alerts & monitoring via SNS + CloudWatch
⚙️ Tech Stack
Category	Tools & Services
Cloud	AWS (S3, Glue, Lambda, Step Functions, SNS, Athena, EventBridge)
Processing	PySpark, AWS Glue ETL
Storage	Amazon S3 (Parquet + Snappy compression)
Orchestration	AWS Step Functions
Monitoring	CloudWatch, SNS
Language	Python 3, SQL
Libraries	Pandas, Boto3, AWS Wrangler
📁 Project Structure
youtube-data-pipeline-2026/
│
├── lambdas/
│   ├── youtube_api_integration/     # Ingests trending data from YouTube API
│   └── json_to_parquet/             # Converts reference JSON → Parquet
│
├── glue_jobs/
│   ├── bronze_to_silver.py          # Raw → Clean transformation
│   └── silver_to_gold.py            # Aggregation layer
│
├── data_quality/
│   └── dq_lambda.py                 # Data validation checks
│
├── step_functions/
│   └── orchestration.json           # Pipeline workflow definition
│
├── scripts/
│   └── aws_setup.sh                 # Infrastructure helper scripts
│
├── data/
│   └── reference & historical datasets
│
└── architecture.png                 # System design diagram
🔄 Data Flow
🟫 Bronze Layer (Raw Data Ingestion)
Pulls trending videos from YouTube Data API v3
Loads historical Kaggle datasets for benchmarking
Stores raw JSON/CSV in S3

Example path:

s3://bronze-bucket/youtube/raw_statistics/region=IN/date=2026-04-01/
🟨 Silver Layer (Cleaned & Structured Data)

Processed using AWS Glue + PySpark:

Schema enforcement
Type casting & normalization
Null handling & deduplication
Derived metrics:
engagement_rate
like_ratio

Output stored in Parquet format (optimized for analytics)

🧪 Data Quality Gate

Before moving to Gold layer:

Row count validation
Null threshold checks
Schema validation
Data freshness check

If validation fails:

❌ Pipeline stops
🚨 SNS alert triggered
🟩 Gold Layer (Business Analytics)

Final analytics-ready datasets:

📊 trending_analytics
Daily region-wise trending insights
Views, likes, engagement metrics
📺 channel_analytics
Channel performance ranking
Trending frequency analysis
🏷️ category_analytics
Category-level distribution
View share % across regions

All tables are:

Stored in Parquet (Snappy compressed)
Registered in Glue Data Catalog
Queryable via Amazon Athena
🌍 Supported Regions

US, GB, CA, DE, FR, IN, JP, KR, MX, RU

🚀 How the Pipeline Runs
Automated Execution (Recommended)
Triggered via AWS EventBridge
Runs every 6 hours
Fully serverless execution
Step Execution Order
YouTube API ingestion → Bronze S3
Parallel processing:
Glue: Bronze → Silver
Lambda: Reference data processing
Data Quality validation
Glue: Silver → Gold aggregation
SNS notification (success/failure)
📊 Example Athena Query
SELECT channel_title, total_views, times_trending
FROM channel_analytics
WHERE region = 'IN'
ORDER BY total_views DESC
LIMIT 10;
🔔 Monitoring & Alerting
📌 Step Functions dashboard → pipeline execution tracking
📌 CloudWatch logs → debugging & observability
📌 SNS alerts → real-time failure notifications
📌 Athena → ad-hoc analytics validation
🧠 What This Project Demonstrates

This project showcases:

Real-world data engineering architecture design
AWS serverless pipeline development
Scalable ETL system implementation
Strong understanding of data modeling & transformation
Production-grade monitoring & failure handling
End-to-end analytics pipeline ownership
🎯 Future Improvements
Streaming ingestion using Kafka / Kinesis
Data lakehouse with Iceberg / Delta format
Dashboard layer using QuickSight / Power BI
CI/CD for pipeline deployment
⭐ Why This Project Matters

This is not just a data pipeline—it demonstrates:

“Ability to design, build, and operate a production-grade cloud data system end-to-end.”
