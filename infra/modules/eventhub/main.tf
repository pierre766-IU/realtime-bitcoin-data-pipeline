resource "azurerm_eventhub_namespace" "this" {
  name                          = var.namespace_name
  location                      = var.location
  resource_group_name           = var.resource_group_name
  sku                           = var.sku
  capacity                      = var.capacity
  public_network_access_enabled = var.public_network_access_enabled
  minimum_tls_version           = "1.2"
  tags                          = var.tags
}

resource "azurerm_eventhub" "this" {
  name                = var.eventhub_name
  namespace_name      = azurerm_eventhub_namespace.this.name
  resource_group_name = var.resource_group_name
  partition_count     = var.partition_count
  message_retention   = var.message_retention
}

resource "azurerm_eventhub_consumer_group" "this" {
  for_each            = toset(var.consumer_groups)
  name                = each.value
  namespace_name      = azurerm_eventhub_namespace.this.name
  eventhub_name       = azurerm_eventhub.this.name
  resource_group_name = var.resource_group_name
}

resource "azurerm_monitor_diagnostic_setting" "eventhub_namespace" {
  count                      = var.enable_diagnostics ? 1 : 0
  name                       = "diag-${var.namespace_name}"
  target_resource_id         = azurerm_eventhub_namespace.this.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "OperationalLogs"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}
