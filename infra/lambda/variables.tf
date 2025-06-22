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

variable "B3_URL" {
  description = "B3 URL for scraping."
  type        = string
  default     = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/"
} 