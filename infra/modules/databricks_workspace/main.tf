resource "azurerm_databricks_workspace" "this" {
  name                          = var.workspace_name
  location                      = var.location
  resource_group_name           = var.resource_group_name
  sku                           = var.sku
  managed_resource_group_name   = var.managed_resource_group_name
  public_network_access_enabled = var.public_network_access_enabled

  custom_parameters {
    no_public_ip = true
  }

  tags = var.tags
}
