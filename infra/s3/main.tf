terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "b3_raw_data" {
  bucket = var.bucket_name
  force_destroy = true
} 