output "lambda_function_name" {
  value = aws_lambda_function.b3_scrapper.function_name
}

output "requests_layer_arn" {
  value = aws_lambda_layer_version.requests.arn
}

output "numpy_arn" {
  value = aws_lambda_layer_version.numpy.arn
}