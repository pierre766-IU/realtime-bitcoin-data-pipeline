variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "workspace_name" {
  type = string
}

variable "sku" {
  type    = string
  default = "premium"
}

variable "managed_resource_group_name" {
  type    = string
  default = null
}

variable "public_network_access_enabled" {
  type    = bool
  default = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
