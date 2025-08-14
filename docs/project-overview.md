# Project Overview – WordPress on AWS Lightsail with Terraform

## 📌 Objective
Deploy a fully functional **WordPress** site on **AWS Lightsail** using **Infrastructure as Code (IaC)** with Terraform, ensuring a repeatable and automated provisioning process.

## 🎯 Goals
- Demonstrate knowledge of **AWS Lightsail** for simplified hosting.
- Showcase **Terraform** skills for IaC deployment.
- Deliver a setup that is **reproducible**, **documented**, and **easy to maintain**.

## 🛠️ Technical Stack
- **AWS Lightsail** – Compute, Networking, and DNS management
- **Terraform** – Infrastructure provisioning
- **WordPress** – CMS platform
- **GitHub** – Source control for Terraform configuration
- **AWS Route 53** *(optional)* – Domain management

## 📂 Project Structure
```
terraform/
├── main.tf        # Lightsail instance & networking resources
├── variables.tf   # Parameter definitions (instance size, region, etc.)
├── outputs.tf     # Outputs (public IP, WordPress URL)
└── provider.tf    # AWS provider configuration
```

## 🚀 Deployment Steps
1. **Clone Repository**  
   ```bash
   git clone https://github.com/FromOopsToOps/DevOps-SRE-Platform.git
   cd docs/terraform/
   ```
2. **Set Variables**  
   Modify `variables.tf` or use a `terraform.tfvars` file to define:
   - AWS region
   - Instance size
   - Key pair name
3. **Initialize Terraform**  
   ```bash
   terraform init
   ```
4. **Review Plan**  
   ```bash
   terraform plan
   ```
5. **Apply Infrastructure**  
   ```bash
   terraform apply
   ```
6. **Access WordPress**  
   Visit the public IP or domain name from the Terraform outputs.

## ✅ Expected Outcome
- A running WordPress site on AWS Lightsail
- Infrastructure managed entirely through Terraform
- Ability to **destroy and recreate** the environment on demand

## 📈 Possible Improvements
- Automate DNS setup with AWS Route 53
- Enable SSL using Let’s Encrypt
- Integrate with AWS CloudFront for CDN caching
