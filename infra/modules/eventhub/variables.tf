variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "namespace_name" {
  type = string
}

variable "eventhub_name" {
  type = string
}

variable "sku" {
  type    = string
  default = "Standard"
}

variable "capacity" {
  type    = number
  default = 1
}

variable "partition_count" {
  type    = number
  default = 4
}

variable "message_retention" {
  type    = number
  default = 1
}

variable "consumer_groups" {
  type    = list(string)
  default = ["bronze-job", "silver-job", "gold-job"]
}

variable "public_network_access_enabled" {
  type    = bool
  default = false
}

variable "log_analytics_workspace_id" {
  type    = string
  default = null
}

variable "enable_diagnostics" {
  type    = bool
  default = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
