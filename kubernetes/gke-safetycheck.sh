This is an automation script that I wrote that would connect to clusters in a region
then check, node by node, and output if they are SAFE or UNSAFE in the case of the
security vulnerability https://cloud.google.com/kubernetes-engine/docs/how-to/disable-kubelet-readonly-port
Then prints a neat list for the devops to review and apply fixes to.

# ---
#!/bin/bash

# Define ANSI color codes for printf
RED="\e[31m"
YELLOW="\e[33m"
GREEN="\e[32m"
BLUE="\e[34m"
RESET="\e[0m"

# Clear up temp files
rm -f projects nodes clusters target-list error.log result.txt

# Step 1: Get the list of all available regions
# Uncomment below to list all regions automatically
# gcloud compute regions list --format="value(name)" > regions

# Fetch list of projects
gcloud projects list --format="value(projectId)" > projects

# Step 2: Iterate through each project and fetch clusters
while read -r region_name; do
    while read -r project_name; do
        printf "${BLUE}Trying $project_name in $region_name...${RESET}\n"
        
        cluster_list=$(gcloud container clusters list --project "$project_name" --region "$region_name" --format="value(name,location)" 2>/tmp/project_error.log)

        if grep -q "code=403" /tmp/project_error.log; then
            printf "${RED}  You are not allowed in $project_name${RESET}\n"
            rm -f /tmp/project_error.log
            continue
        fi
        rm -f /tmp/project_error.log

        if [[ -z "$cluster_list" ]]; then
            printf "${YELLOW}  No clusters found for project: $project_name${RESET}\n"
            continue
        fi

        while read -r cluster_name region; do
            printf "${BLUE}  Trying the $cluster_name cluster...${RESET}\n"
            
            # Get credentials for the cluster
            gcloud container clusters get-credentials "$cluster_name" --region "$region" --project "$project_name" >/tmp/cluster_error.log || continue

            if grep -q "Forbidden" /tmp/cluster_error.log; then
                printf "${RED}    You are not allowed in $cluster_name${RESET}\n"
                rm -f /tmp/cluster_error.log
                continue
            fi
            rm -f /tmp/cluster_error.log

            # Get node list and store in a file
            printf "${BLUE}    Getting node list...${RESET}\n"
            kubectl get nodes --no-headers 2>>error.log | awk -v cluster="$cluster_name" -v project="$project_name" -v region="$region" '{print project, cluster, region, $1}' >> nodes

            # Remove duplicates
            sort -u nodes -o target-list
        done <<< "$cluster_list"
    done < projects
done < regions

# Step 3: Process target list and check node security
while read -r project_name cluster_name region node_name; do
    printf "${BLUE}Processing cluster: $cluster_name in region: $region${RESET}\n"
        
    # Get credentials for the cluster
    gcloud container clusters get-credentials "$cluster_name" --region "$region" --project "$project_name" 2>>error.log || continue
    
    metrics_output=$(kubectl get --raw "/api/v1/nodes/$node_name/proxy/metrics" | grep 'server_type=readwrite' 2>/dev/null)

    # Now determine if the cluster node is safe or not  
    if [[ -z "$metrics_output" ]]; then
        result="SAFE"
        color=$GREEN
    elif echo "$metrics_output" | grep -q 'server_type="readonly"'; then
        result="UNSAFE"
        color=$RED
    else
        result="Impossible to determine"
        color=$YELLOW
    fi

    printf "${color}$project_name $cluster_name $node_name $result${RESET}\n" >> result.txt
    unset metrics_output
done < target-list

rm -f projects nodes clusters target-list error.log result.txt