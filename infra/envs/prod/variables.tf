variable "subscription_id" {
  type    = string
  default = null
}

variable "project" {
  type    = string
  default = "btcpipeline"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,30}$", var.project))
    error_message = "project must match ^[a-z0-9-]{3,30}$."
  }
}

variable "environment" {
  type    = string
  default = "prod"

  validation {
    condition     = var.environment == "prod"
    error_message = "infra/envs/prod must use environment = prod."
  }
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "resource_group_name" {
  type    = string
  default = "rg-btcpipeline-prod"

  validation {
    condition     = can(regex("^rg-[a-z0-9-]+-prod$", var.resource_group_name))
    error_message = "resource_group_name must match ^rg-[a-z0-9-]+-prod$."
  }
}

variable "eventhub_sku" {
  type    = string
  default = "Premium"
}

variable "eventhub_capacity" {
  type    = number
  default = 1
}

variable "eventhub_partition_count" {
  type    = number
  default = 8
}

variable "eventhub_message_retention" {
  type    = number
  default = 1
}

variable "public_network_access_enabled" {
  type    = bool
  default = false
}

variable "alert_email_receivers" {
  type    = list(string)
  default = []
}

variable "tags" {
  type    = map(string)
  default = {}
}
