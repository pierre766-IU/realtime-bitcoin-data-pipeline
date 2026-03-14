output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "eventhub_namespace" {
  value = module.eventhub.namespace_name
}

output "eventhub_name" {
  value = module.eventhub.eventhub_name
}

output "storage_account_name" {
  value = module.adls.storage_account_name
}

output "adls_dfs_endpoint" {
  value = module.adls.primary_dfs_endpoint
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
