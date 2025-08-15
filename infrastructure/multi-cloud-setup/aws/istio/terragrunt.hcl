terraform {
  source = "terraform-helm-release"
}

include {
  path = find_in_parent_folders()
}

inputs = {
  name       = "istio"
  chart      = "istiod"
  repository = "https://istio-release.storage.googleapis.com/charts"
  namespace  = "istio-system"

  values = [
    file("${path_relative_from_include()}/istio-values.yaml")
  ]
}