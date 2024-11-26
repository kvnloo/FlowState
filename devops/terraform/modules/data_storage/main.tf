# Amazon Timestream for time-series data (biometric data, performance metrics)
resource "aws_timestreamwrite_database" "timeseries" {
  database_name = var.timestream_db_name
  
  tags = {
    Environment = var.environment
  }
}

# S3 for storing raw data and large files
resource "aws_s3_bucket" "data" {
  bucket = var.s3_bucket_name
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# DynamoDB for metadata and relationships
resource "aws_dynamodb_table" "metadata" {
  name           = "flowstate-metadata-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "pk"
  range_key      = "sk"
  
  attribute {
    name = "pk"
    type = "S"
  }
  
  attribute {
    name = "sk"
    type = "S"
  }
  
  attribute {
    name = "gsi1pk"
    type = "S"
  }
  
  attribute {
    name = "gsi1sk"
    type = "S"
  }
  
  global_secondary_index {
    name               = "gsi1"
    hash_key           = "gsi1pk"
    range_key          = "gsi1sk"
    projection_type    = "ALL"
  }
  
  tags = {
    Environment = var.environment
  }
}

# ElastiCache for Redis (caching and real-time analytics)
resource "aws_elasticache_cluster" "cache" {
  cluster_id           = "flowstate-cache-${var.environment}"
  engine              = "redis"
  node_type           = "cache.t3.micro"
  num_cache_nodes     = 1
  parameter_group_name = "default.redis6.x"
  port                = 6379
  
  tags = {
    Environment = var.environment
  }
}

# IAM roles and policies
resource "aws_iam_role" "data_access" {
  name = "flowstate-data-access-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "timestream_access" {
  name = "timestream-access"
  role = aws_iam_role.data_access.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "timestream:WriteRecords",
          "timestream:Select",
          "timestream:DescribeTable",
          "timestream:ListMeasures"
        ]
        Resource = aws_timestreamwrite_database.timeseries.arn
      }
    ]
  })
}
