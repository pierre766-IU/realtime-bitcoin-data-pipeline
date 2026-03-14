variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "key_vault_name" {
  type = string
}

variable "public_network_access_enabled" {
  type    = bool
  default = false
}

variable "secrets" {
  type      = map(string)
  default   = {}
  sensitive = true
}

variable "tags" {
  type    = map(string)
  default = {}
}
