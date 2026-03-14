project             = "btcpipeline"
environment         = "prod"
location            = "westeurope"
resource_group_name = "rg-btcpipeline-prod"

eventhub_sku               = "Premium"
eventhub_capacity          = 1
eventhub_partition_count   = 8
eventhub_message_retention = 1

public_network_access_enabled = false
alert_email_receivers         = []

tags = {
  owner       = "data-platform"
  cost_center = "analytics"
}
