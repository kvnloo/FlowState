terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    bucket = "flowstate-terraform-state-prod"
    key    = "prod/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "../../modules/vpc"
  
  environment = "prod"
  vpc_cidr    = var.vpc_cidr
}

module "quantum_computing" {
  source = "../../modules/quantum_computing"
  
  environment = "prod"
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
}

module "data_storage" {
  source = "../../modules/data_storage"
  
  environment        = "prod"
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  timestream_db_name = "flowstate_timeseries_prod"
  s3_bucket_name    = "flowstate-data-prod"
}
