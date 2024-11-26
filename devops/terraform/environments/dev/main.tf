terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    bucket = "flowstate-terraform-state-dev"
    key    = "dev/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "../../modules/vpc"
  
  environment = "dev"
  vpc_cidr    = var.vpc_cidr
}

module "quantum_computing" {
  source = "../../modules/quantum_computing"
  
  environment = "dev"
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
}

module "data_storage" {
  source = "../../modules/data_storage"
  
  environment        = "dev"
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  timestream_db_name = "flowstate_timeseries_dev"
  s3_bucket_name    = "flowstate-data-dev"
}
