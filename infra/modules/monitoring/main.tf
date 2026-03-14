resource "azurerm_log_analytics_workspace" "this" {
  name                = var.workspace_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_monitor_action_group" "this" {
  name                = var.action_group_name
  resource_group_name = var.resource_group_name
  short_name          = substr(var.action_group_short_name, 0, 12)
  tags                = var.tags

  dynamic "email_receiver" {
    for_each = toset(var.email_receivers)
    content {
      name          = "email-${replace(email_receiver.value, "@", "-")}"
      email_address = email_receiver.value
    }
  }
}
