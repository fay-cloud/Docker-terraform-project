# Get the existing storage account
data "azurerm_storage_account" "existing" {
  name                = "datalakesproj"
  resource_group_name = "databasereource"
}

# Create a container in that existing storage account
resource "azurerm_storage_container" "my_container" {
  name                  = "my-new-container"
  storage_account_id    = data.azurerm_storage_account.existing.id
  container_access_type = "private"
}
