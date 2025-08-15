terraform {
  source = "Azure/aks/azurerm"
}

include {
  path = find_in_parent_folders()
}

inputs = {
  resource_group_name = "rg-multi-cloud-aks"
  kubernetes_version  = local.kubernetes_version
  cluster_name        = "multi-cloud-aks"
  location            = "East US"

  default_node_pool = {
    name       = "controlplane"
    node_count = 1
    vm_size    = "Standard_DS2_v2"
  }

  node_pools = [
    {
      name       = "workload"
      node_count = 2
      vm_size    = "Standard_DS3_v2"
    }
  ]
}