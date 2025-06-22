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

resource "aws_lambda_layer_version" "requests" {
  filename   = "../../build/layers/layer_requests.zip"
  layer_name = "requests"
  compatible_runtimes = ["python3.12"]
}

resource "aws_lambda_layer_version" "numpy" {
  filename   = "../../build/layers/layer_numpy.zip"
  layer_name = "numpy"
  compatible_runtimes = ["python3.12"]
}

data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

resource "aws_lambda_function" "b3_scrapper" {
  function_name = "b3_scrapper"
  handler       = "lambda_handler.handle"
  runtime       = "python3.12"
  filename      = "../../build/lambda.zip"
  source_code_hash = filebase64sha256("../../build/lambda.zip")
  timeout = 120

  environment {
    variables = {
      BUCKET_NAME = var.bucket_name
      B3_API_URL  = var.B3_URL
    }
  }

  layers = [
    aws_lambda_layer_version.requests.arn,
    "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python312:18",
    aws_lambda_layer_version.numpy.arn
  ]

  role = data.aws_iam_role.lab_role.arn
}

resource "aws_cloudwatch_event_rule" "daily_19h" {
  name                = "b3_scrapper_daily_19h"
  schedule_expression = "cron(0 22 * * ? *)" # 19:00 BRT = 22:00 UTC
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_19h.name
  target_id = "b3_scrapper_lambda"
  arn       = aws_lambda_function.b3_scrapper.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.b3_scrapper.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_19h.arn
} 