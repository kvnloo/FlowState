# AWS Braket for quantum computing resources
resource "aws_braket_quantum_task" "qft_processor" {
  action = jsonencode({
    braketSchemaHeader = {
      name    = "braket.task_result.schema"
      version = "1"
    }
    
    # Configuration for Quantum Fourier Transform
    program = {
      qftCircuit = {
        instructions = [
          {
            target   = 0
            type     = "h"
          },
          {
            control  = 0
            target   = 1
            type     = "cnot"
          }
        ]
      }
    }
    
    deviceParameters = {
      paradigmParameters = {
        qubitCount = 4
      }
    }
  })
  
  device_arn   = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
  output_s3_bucket = aws_s3_bucket.quantum_results.id
  output_s3_key_prefix = "qft-results"
  
  tags = {
    Environment = var.environment
  }
}

# S3 bucket for quantum computation results
resource "aws_s3_bucket" "quantum_results" {
  bucket = "flowstate-quantum-${var.environment}"
  
  tags = {
    Environment = var.environment
  }
}

# SageMaker for quantum-classical hybrid processing
resource "aws_sagemaker_notebook_instance" "quantum_processing" {
  name          = "flowstate-quantum-notebook-${var.environment}"
  role_arn      = aws_iam_role.quantum_processing.arn
  instance_type = "ml.t3.medium"
  
  tags = {
    Environment = var.environment
  }
}

# IAM role for quantum processing
resource "aws_iam_role" "quantum_processing" {
  name = "flowstate-quantum-processing-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policies for quantum processing
resource "aws_iam_role_policy" "quantum_access" {
  name = "quantum-access"
  role = aws_iam_role.quantum_processing.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "braket:*",
          "s3:*"
        ]
        Resource = [
          aws_s3_bucket.quantum_results.arn,
          "${aws_s3_bucket.quantum_results.arn}/*"
        ]
      }
    ]
  })
}

# Lambda function for quantum processing pipeline
resource "aws_lambda_function" "quantum_pipeline" {
  filename      = "lambda_quantum_pipeline.zip"
  function_name = "flowstate-quantum-pipeline-${var.environment}"
  role          = aws_iam_role.quantum_processing.arn
  handler       = "index.handler"
  runtime       = "python3.9"
  
  environment {
    variables = {
      QUANTUM_BUCKET = aws_s3_bucket.quantum_results.id
      ENVIRONMENT    = var.environment
    }
  }
  
  tags = {
    Environment = var.environment
  }
}
