terraform {
  required_version = ">= 1.5, < 2.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

variable "port" {
  description = "Porta local do conversor."
  type        = number
  default     = 8000
  validation {
    condition     = var.port >= 1024 && var.port <= 65535 && floor(var.port) == var.port
    error_message = "Use uma porta inteira entre 1024 e 65535."
  }
}

resource "local_file" "deployment_manifest" {
  filename = "${path.module}/generated/deployment.json"
  content = jsonencode({
    application = "termo-conversor"
    host        = "127.0.0.1"
    port        = var.port
    command     = "python -m conversor.server --port ${var.port}"
    healthcheck = "http://127.0.0.1:${var.port}/health"
  })
}

output "application_url" {
  value = "http://127.0.0.1:${var.port}"
}

