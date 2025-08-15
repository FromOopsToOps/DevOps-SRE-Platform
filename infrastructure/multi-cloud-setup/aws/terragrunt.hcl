terraform {
  source = "terraform-aws-modules/eks/aws"
}

include {
  path = find_in_parent_folders()
}

inputs = {
  cluster_name    = "multi-cloud-eks"
  cluster_version = local.kubernetes_version
  subnet_ids      = ["subnet-xxxxxxxx", "subnet-yyyyyyyy"]

  eks_managed_node_groups = {
    control-plane = {
      desired_size   = 1
      max_size       = 1
      min_size       = 1
      instance_types = ["t3.medium"]
    }
    workload = {
      desired_size   = 2
      max_size       = 3
      min_size       = 2
      instance_types = ["t3.large"]
    }
  }
}