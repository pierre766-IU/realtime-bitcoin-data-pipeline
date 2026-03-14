output "storage_account_id" {
  value = azurerm_storage_account.this.id
}

output "storage_account_name" {
  value = azurerm_storage_account.this.name
}

output "primary_dfs_endpoint" {
  value = azurerm_storage_account.this.primary_dfs_endpoint
}

output "containers" {
  value = [for c in azurerm_storage_container.this : c.name]
}
