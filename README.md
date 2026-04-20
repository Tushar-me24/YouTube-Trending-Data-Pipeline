# 🚀 YouTube Trending Data Engineering Pipeline (AWS | End-to-End ETL System)
A cloud-native data engineering pipeline that ingests YouTube trending video data across 10 regions, processes it through a Medallion Architecture (Bronze → Silver → Gold), enforces automated data quality checks, and generates analytics-ready datasets using AWS serverless services.

The system is fully orchestrated using AWS Step Functions with monitoring, alerting, and failure handling built-in.
<img width="2784" height="1536" alt="image" src="https://github.com/user-attachments/assets/28cd19df-2e58-42fa-9fc8-9411dbc41a3c" />
⚡ Key Highlights
End-to-end serverless ETL pipeline on AWS
Multi-region ingestion using YouTube Data API v3
Medallion architecture (Bronze → Silver → Gold)
Automated data quality gate (blocking failures)
Fully orchestrated using AWS Step Functions
Real-time alerting via AWS SNS
Analytics-ready tables queryable via Athena
Production-grade logging via CloudWatch
🏗️ Architecture

The system follows a layered Medallion design:

Bronze Layer → Raw ingestion (API + Kaggle datasets)
Silver Layer → Cleaned, deduplicated, standardized data
Data Quality Gate → Validation before aggregation
Gold Layer → Business-level analytics tables

Orchestration is handled via AWS Step Functions, coordinating Lambda + Glue jobs with retry logic and failure handling.

<img width="1919" height="1186" alt="image" src="https://github.com/user-attachments/assets/4cda7ebb-1442-42b2-bb21-8ab3e76f4b98" />

<img width="1486" height="836" alt="image" src="https://github.com/user-attachments/assets/5262d3a2-9502-4a32-89dd-6000724aa4f5" />

⚙️ Tech Stack

Cloud: AWS (S3, Glue, Lambda, Step Functions, SNS, Athena, EventBridge)
Processing: PySpark (AWS Glue ETL)
Storage: Amazon S3 (Parquet + Snappy)
Orchestration: AWS Step Functions
Monitoring: CloudWatch, SNS
Languages: Python, SQL
Libraries: Pandas, Boto3, AWS Wrangler

🔄 Data Flow
Bronze Layer
YouTube API v3 ingestion
Kaggle historical datasets
Raw JSON/CSV stored in S3
Silver Layer
Schema enforcement
Deduplication (video-level uniqueness)
Derived metrics:
engagement_rate
like_ratio
Data Quality Gate

Validations:

Row count thresholds
Null percentage checks
Schema validation
Data freshness checks

❌ Failure → SNS alert + pipeline stop

Gold Layer

Outputs:

trending_analytics , 
channel_analytics , 
category_analytics , 

Stored as:

Parquet (Snappy compressed)
Partitioned by region
Registered in Glue Catalog
📊 Sample Analytics Query
SELECT channel_title, total_views, times_trending
FROM channel_analytics
WHERE region = 'IN'
ORDER BY total_views DESC
LIMIT 10;
🌍 Supported Regions

US, GB, CA, DE, FR, IN, JP, KR, MX, RU

🧠 What This Project Demonstrates
Designing production-grade data architectures
Building serverless ETL pipelines on AWS
Implementing data quality gates in distributed systems
Orchestrating workflows using Step Functions
Handling failure recovery + observability
End-to-end data ownership (ingestion → analytics)
🚀 Future Improvements
Real-time ingestion using Kafka / Kinesis
Lakehouse migration (Iceberg / Delta)
BI dashboards (QuickSight / Power BI)
CI/CD for infrastructure deployment
🏁 Summary

This project demonstrates the ability to design and implement a scalable, production-grade cloud data pipeline with full observability, reliability, and analytics readiness.
