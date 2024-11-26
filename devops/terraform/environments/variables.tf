variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "timestream_retention_period" {
  description = "Retention period for Timestream data in days"
  type        = number
}

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PROVISIONED or PAY_PER_REQUEST)"
  type        = string
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes in the Redis cluster"
  type        = number
}

variable "quantum_device_type" {
  description = "AWS Braket quantum device type"
  type        = string
}

variable "sagemaker_instance_type" {
  description = "SageMaker notebook instance type"
  type        = string
}

variable "quantum_qubit_count" {
  description = "Number of qubits for quantum processing"
  type        = number
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "project" {
  description = "Project name"
  type        = string
}

variable "enable_quantum_pipeline" {
  description = "Enable quantum processing pipeline"
  type        = bool
}

variable "enable_eye_tracking" {
  description = "Enable eye tracking features"
  type        = bool
}

variable "enable_gut_microbiome" {
  description = "Enable gut microbiome analysis"
  type        = bool
}

variable "min_capacity" {
  description = "Minimum capacity for auto-scaling"
  type        = number
}

variable "max_capacity" {
  description = "Maximum capacity for auto-scaling"
  type        = number
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
}

variable "enable_point_in_time_recovery" {
  description = "Enable point-in-time recovery for databases"
  type        = bool
}

variable "enable_enhanced_monitoring" {
  description = "Enable enhanced monitoring"
  type        = bool
}

variable "monitoring_interval" {
  description = "Monitoring interval in seconds"
  type        = number
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
}

variable "budget_amount" {
  description = "Monthly budget amount in USD"
  type        = number
}

variable "enable_cost_alerts" {
  description = "Enable cost alerts"
  type        = bool
}

# Production-specific variables
variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "enable_cross_region_backup" {
  description = "Enable cross-region backup"
  type        = bool
  default     = false
}

variable "replica_regions" {
  description = "List of regions for cross-region replication"
  type        = list(string)
  default     = []
}

variable "enable_encryption_at_rest" {
  description = "Enable encryption at rest"
  type        = bool
  default     = true
}

variable "enable_ssl" {
  description = "Enable SSL/TLS"
  type        = bool
  default     = true
}

variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate"
  type        = string
  default     = ""
}

variable "enable_performance_insights" {
  description = "Enable Performance Insights"
  type        = bool
  default     = false
}

variable "performance_insights_retention" {
  description = "Performance Insights retention period in days"
  type        = number
  default     = 7
}

variable "dynamodb_read_capacity" {
  description = "DynamoDB read capacity units"
  type        = number
  default     = 5
}

variable "dynamodb_write_capacity" {
  description = "DynamoDB write capacity units"
  type        = number
  default     = 5
}

variable "redis_automatic_failover" {
  description = "Enable Redis automatic failover"
  type        = bool
  default     = false
}

variable "redis_transit_encryption" {
  description = "Enable Redis in-transit encryption"
  type        = bool
  default     = true
}

variable "redis_at_rest_encryption" {
  description = "Enable Redis at-rest encryption"
  type        = bool
  default     = true
}
