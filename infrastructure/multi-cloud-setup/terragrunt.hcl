remote_state {
  backend = "s3"
  config = {
    bucket         = "your-tf-state-bucket"
    key            = "multi-cloud-k8s/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

inputs = {
  kubernetes_version = "1.29"
}