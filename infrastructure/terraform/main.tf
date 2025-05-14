provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "crypto-trading-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
}

module "ecs" {
  source = "terraform-aws-modules/ecs/aws"

  cluster_name = "crypto-trading-cluster"

  cluster_configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
      log_configuration = {
        cloud_watch_log_group_name = "/ecs/crypto-trading"
      }
    }
  }

  autoscaling_capacity_providers = {
    capacity_provider = {
      target_capacity = 100
      default_capacity_provider_strategy = {
        weight = 100
      }
    }
  }
}

module "rds" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "crypto-trading-db"

  engine            = "postgres"
  engine_version    = "14"
  instance_class    = "db.t3.medium"
  allocated_storage = 100

  db_name  = "crypto_trading"
  username = "crypto_trading_user"
  port     = "5432"

  vpc_security_group_ids = [aws_security_group.rds.id]
  subnet_ids            = module.vpc.private_subnets
}