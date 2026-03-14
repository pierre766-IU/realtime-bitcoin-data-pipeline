project             = "btcpipeline"
environment         = "dev"
location            = "westeurope"
resource_group_name = "rg-btcpipeline-dev"

eventhub_sku               = "Standard"
eventhub_capacity          = 1
eventhub_partition_count   = 4
eventhub_message_retention = 1

public_network_access_enabled = false
alert_email_receivers         = []

tags = {
  owner       = "data-platform"
  cost_center = "analytics"
}
