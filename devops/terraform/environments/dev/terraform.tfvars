aws_region = "us-west-2"
vpc_cidr   = "10.0.0.0/16"

# Data Storage Configuration
timestream_retention_period = 7    # days
dynamodb_billing_mode      = "PAY_PER_REQUEST"
redis_node_type           = "cache.t3.micro"
redis_num_cache_nodes     = 1

# Quantum Computing Configuration
quantum_device_type       = "sv1"  # Amazon Braket simulator
sagemaker_instance_type  = "ml.t3.medium"
quantum_qubit_count      = 4

# Tags
environment = "dev"
project     = "flowstate"

# Feature Flags
enable_quantum_pipeline  = true
enable_eye_tracking     = true
enable_gut_microbiome   = true

# Scaling Parameters
min_capacity = 1
max_capacity = 2

# Backup Configuration
backup_retention_days = 7
enable_point_in_time_recovery = true

# Monitoring
enable_enhanced_monitoring = true
monitoring_interval       = 60  # seconds

# Cost Management
cost_center = "research-dev"
budget_amount = 1000  # USD per month
enable_cost_alerts = true
