terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.58"
    }
  }
}

provider "azurerm" {
  features {}

  # explicitly specify subscription and tenant
  subscription_id = "5f2e6e04-94d5-48db-97d8-7acfab0f6c71"  # your Azure for Students subscription
  tenant_id       = "0907bb1e-21fc-476f-8843-02d09ceb59a7"  # tenant ID from az account show
}
