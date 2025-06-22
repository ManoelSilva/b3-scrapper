variable "region" {
  description = "AWS region to deploy resources."
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "S3 bucket name to store raw data."
  type        = string
  default     = "861115334572-raw"
} 