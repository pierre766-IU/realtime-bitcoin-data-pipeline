output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "eventhub_namespace" {
  value = module.eventhub.namespace_name
}

output "eventhub_name" {
  value = module.eventhub.eventhub_name
}

output "event_hubs_bootstrap" {
  value = "${module.eventhub.namespace_name}.servicebus.windows.net:9093"
}

output "storage_account_name" {
  value = module.adls.storage_account_name
}

output "adls_dfs_endpoint" {
  value = module.adls.primary_dfs_endpoint
}

output "delta_base_path" {
  value = "abfss://delta@${module.adls.storage_account_name}.dfs.core.windows.net/bitcoin"
}

output "checkpoint_base_path" {
  value = "abfss://checkpoints@${module.adls.storage_account_name}.dfs.core.windows.net/bitcoin"
}

output "key_vault_name" {
  value = module.keyvault.key_vault_name
}

output "key_vault_uri" {
  value = module.keyvault.vault_uri
}

output "databricks_workspace_url" {
  value = module.databricks_workspace.workspace_url
}

output "log_analytics_workspace_name" {
  value = module.monitoring.log_analytics_workspace_name
}
