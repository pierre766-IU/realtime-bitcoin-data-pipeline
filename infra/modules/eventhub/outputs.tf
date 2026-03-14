output "namespace_id" {
  value = azurerm_eventhub_namespace.this.id
}

output "namespace_name" {
  value = azurerm_eventhub_namespace.this.name
}

output "eventhub_name" {
  value = azurerm_eventhub.this.name
}

output "consumer_groups" {
  value = [for cg in azurerm_eventhub_consumer_group.this : cg.name]
}
