aws_region = "us-west-2"
vpc_cidr   = "10.1.0.0/16"  # Different CIDR for prod

# Data Storage Configuration
timestream_retention_period = 365  # days
dynamodb_billing_mode      = "PROVISIONED"
redis_node_type           = "cache.r6g.large"
redis_num_cache_nodes     = 2

# Quantum Computing Configuration
quantum_device_type       = "arn:aws:braket:us-west-2::device/qpu/rigetti/Aspen-M-3"  # Real quantum processor
sagemaker_instance_type  = "ml.c5.xlarge"
quantum_qubit_count      = 8

# Tags
environment = "prod"
project     = "flowstate"

# Feature Flags
enable_quantum_pipeline  = true
enable_eye_tracking     = true
enable_gut_microbiome   = true

# Scaling Parameters
min_capacity = 2
max_capacity = 8

# Backup Configuration
backup_retention_days = 30
enable_point_in_time_recovery = true

# Monitoring
enable_enhanced_monitoring = true
monitoring_interval       = 30  # seconds

# Cost Management
cost_center = "research-prod"
budget_amount = 5000  # USD per month
enable_cost_alerts = true

# High Availability Configuration
multi_az = true
enable_cross_region_backup = true
replica_regions = ["us-east-1"]

# Security
enable_encryption_at_rest = true
enable_ssl = true
ssl_certificate_arn = "arn:aws:acm:us-west-2:ACCOUNT_ID:certificate/CERTIFICATE_ID"

# Performance
enable_performance_insights = true
performance_insights_retention = 7  # days

# DynamoDB Specific
dynamodb_read_capacity  = 50
dynamodb_write_capacity = 25

# Redis Specific
redis_automatic_failover = true
redis_transit_encryption = true
redis_at_rest_encryption = true
