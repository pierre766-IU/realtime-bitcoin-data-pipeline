locals {
  common_tags = merge(var.tags, {
    environment = var.environment
    system      = "bitcoin-streaming-pipeline"
    managed_by  = "terraform"
  })

  name_seed                 = lower(replace("${var.project}${var.environment}", "-", ""))
  storage_account_name      = substr("${local.name_seed}dls", 0, 24)
  key_vault_name            = substr("${local.name_seed}kv", 0, 24)
  eventhub_namespace_name   = substr("${local.name_seed}ehns", 0, 50)
  eventhub_name             = "bitcoin-stream"
  databricks_workspace_name = "${var.project}-${var.environment}-dbw"
  monitor_workspace_name    = "log-${var.project}-${var.environment}"
  action_group_name         = "ag-${var.project}-${var.environment}"
  managed_rg_name           = "rg-${var.project}-${var.environment}-dbx-managed"
}

resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

module "monitoring" {
  source                  = "../../modules/monitoring"
  resource_group_name     = azurerm_resource_group.this.name
  location                = azurerm_resource_group.this.location
  workspace_name          = local.monitor_workspace_name
  action_group_name       = local.action_group_name
  action_group_short_name = "btcops"
  email_receivers         = var.alert_email_receivers
  tags                    = local.common_tags
}

module "adls" {
  source                        = "../../modules/adls"
  resource_group_name           = azurerm_resource_group.this.name
  location                      = azurerm_resource_group.this.location
  storage_account_name          = local.storage_account_name
  containers                    = ["delta", "checkpoints", "bronze-deadletter"]
  public_network_access_enabled = var.public_network_access_enabled
  log_analytics_workspace_id    = module.monitoring.log_analytics_workspace_id
  enable_diagnostics            = true
  tags                          = local.common_tags
}

module "eventhub" {
  source                        = "../../modules/eventhub"
  resource_group_name           = azurerm_resource_group.this.name
  location                      = azurerm_resource_group.this.location
  namespace_name                = local.eventhub_namespace_name
  eventhub_name                 = local.eventhub_name
  sku                           = var.eventhub_sku
  capacity                      = var.eventhub_capacity
  partition_count               = var.eventhub_partition_count
  message_retention             = var.eventhub_message_retention
  consumer_groups               = ["bronze-job", "silver-job", "gold-job"]
  public_network_access_enabled = var.public_network_access_enabled
  log_analytics_workspace_id    = module.monitoring.log_analytics_workspace_id
  enable_diagnostics            = true
  tags                          = local.common_tags
}

module "keyvault" {
  source                        = "../../modules/keyvault"
  resource_group_name           = azurerm_resource_group.this.name
  location                      = azurerm_resource_group.this.location
  key_vault_name                = local.key_vault_name
  public_network_access_enabled = var.public_network_access_enabled
  tags                          = local.common_tags
}

module "databricks_workspace" {
  source                        = "../../modules/databricks_workspace"
  resource_group_name           = azurerm_resource_group.this.name
  location                      = azurerm_resource_group.this.location
  workspace_name                = local.databricks_workspace_name
  managed_resource_group_name   = local.managed_rg_name
  public_network_access_enabled = var.public_network_access_enabled
  tags                          = local.common_tags
}
