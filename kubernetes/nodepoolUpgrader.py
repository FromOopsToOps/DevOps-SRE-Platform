This is a neat tool I built to help alleviate the effort for teams without Terraform.
It looks on a certain cluster if the control plane is on a different version than the nodes are
and if that's the case, upgrades the nodepools to the same version on the control plane. 
I wrote this to help teams solve the warning "Kube Version Mismatch" common on GCP 
when you have the control plane on auto upgrade but not the node pools.


# ---
#!/usr/bin/env python3

import argparse
import subprocess
import json
from tabulate import tabulate
import sys
from datetime import datetime
from packaging import version
import logging

def strip_gke_suffix(v):
# removes the GKE tag from the version string
    return v.split('-gke')[0]

# Functions to generate the log file output
log_lines = []

def log(msg, end='\n'):
    print(msg, end=end)
    log_lines.append(msg + end)

def write_log_file(project, region, cluster):
    filename = f"{project}-{region}-{cluster}.log"
    with open(filename, "w") as f:
        f.writelines(log_lines)
    print(f"\nLog written to {filename}")

def extract_json_from_text(text):
# this was tricky: gcloud command offers trailing AND leading information on the output, for example
# when it outputs warnings and/or there are error messages at the end of the json.
# This whole function was written only to extract the useful json from the output.
    # Find first JSON opening char
    first_brace = text.find('{')
    first_bracket = text.find('[')

    # Determine which comes first (and exists)
    if first_brace == -1 and first_bracket == -1:
        raise ValueError("No JSON object or array found in text")

    if first_brace == -1:
        start = first_bracket
        open_char = '['
        close_char = ']'
    elif first_bracket == -1:
        start = first_brace
        open_char = '{'
        close_char = '}'
    else:
        if first_brace < first_bracket:
            start = first_brace
            open_char = '{'
            close_char = '}'
        else:
            start = first_bracket
            open_char = '['
            close_char = ']'

    # Now find the matching closing brace/bracket (handle nested correctly)
    depth = 0
    for i in range(start, len(text)):
        if text[i] == open_char:
            depth += 1
        elif text[i] == close_char:
            depth -= 1
            if depth == 0:
                end = i + 1
                return text[start:end]

    raise ValueError("No matching closing bracket found for JSON.")

def run_cmd(cmd, return_json=True, dry_run=False):
    log(f"Running: {' '.join(cmd)}")

    if dry_run and any(op in cmd for op in ["update", "upgrade", "apply", "delete"]):
        log("Dry run: skipping execution")
        return {} if return_json else ""

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        decoded = output.decode()

        if not return_json:
            return decoded

        # Extract valid JSON substring from output (ignore warnings)
        json_str = extract_json_from_text(decoded)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            log(f"JSON decode error: {e}")
            log(f"Raw (trimmed) output preview:\n{json_str[:300]}...")
            raise

    except subprocess.CalledProcessError as e:
        log(f"Command failed:\n{e.output.decode()}")
        sys.exit(1)

def connect_to_cluster(region, project, cluster_name, dry_run):
# this function just separates the connection logic to the cluster
    log(f"Connecting to cluster {cluster_name} in {region}...")
    if dry_run:
        return
    run_cmd([
        "gcloud", "container", "clusters", "get-credentials", cluster_name,
        f"--region={region}", f"--project={project}"
    ], return_json=False)
    log("Connected to cluster.")

def get_node_pools(cluster_name, region, project, dry_run):
    return run_cmd([
        "gcloud", "container", "node-pools", "list",
        f"--cluster={cluster_name}",
        f"--region={region}",
        f"--project={project}",
        "--format=json"
    ], dry_run=dry_run)

def check_surge_upgrade(nodepool, cluster_name, region, project, dry_run):
# surge upgrade = rolling upgrade
# that's why we check for it before running the upgrade.
# the alternative would be a blue-green upgrade which requires some manual validation.
    name = nodepool["name"]
    settings = nodepool.get("upgradeSettings", {})
    surge = settings.get("maxSurge", 0)
    unavailable = settings.get("maxUnavailable", 1)

    if surge >= 1 and unavailable == 0:
        log(f"Node pool '{name}' already has surge upgrade settings.")
        return True

    log(f"Node pool '{name}' does not have recommended surge upgrade settings.")

    if dry_run:
        log(f"DRY RUN: Would apply surge upgrade settings to node pool '{name}'")
        return False

    choice = input(f"Apply --max-surge-upgrade=1 --max-unavailable-upgrade=0 to '{name}'? (y/n): ").strip().lower()
    if choice == 'y':
        run_cmd([
            "gcloud", "container", "node-pools", "update", name,
            f"--cluster={cluster_name}",
            f"--region={region}",
            f"--project={project}",
            "--max-surge-upgrade=1",
            "--max-unavailable-upgrade=0"
        ], return_json=False)
        log(f"Surge upgrade settings applied to '{name}'")
        return True
    return False

def get_all_workloads(dry_run):
# checks for us if we have workloads with replica counts 1 and below
# which would **fault** in case of a rolling upgrade
    log("Checking deployments for replica count...")
    if dry_run:
        return [{"namespace": "example-ns", "name": "demo-deployment", "replicas": 1}]
    workloads = []
    output = subprocess.check_output(["kubectl", "get", "deployments", "--all-namespaces", "-o=json"])
    data = json.loads(output)
    for item in data["items"]:
        replicas = item["spec"].get("replicas", 1)
        if replicas <= 1:
            workloads.append({
                "namespace": item["metadata"]["namespace"],
                "name": item["metadata"]["name"],
                "replicas": replicas
            })
    return workloads

def get_pdb_coverage(dry_run):
# checks for us if we have workloads with a Pod Disruption Budget set in a way
# that would allow for a NO POD SERVING situation during upgrade
    if dry_run:
        return set()
    output = subprocess.check_output(["kubectl", "get", "pdb", "--all-namespaces", "-o=json"])
    data = json.loads(output)
    covered = set()
    for pdb in data["items"]:
        ns = pdb["metadata"]["namespace"]
        selector = pdb["spec"].get("selector", {}).get("matchLabels", {})
        if selector:
            match = ",".join([f"{k}={v}" for k, v in selector.items()])
            try:
                deployments = subprocess.check_output([
                    "kubectl", "get", "deploy", "-n", ns, "-l", match, "-o=json"
                ])
                deploys = json.loads(deployments)
                for dep in deploys.get("items", []):
                    covered.add((ns, dep["metadata"]["name"]))
            except:
                continue
    return covered

def upgrade_nodepool(name, current_version, target_version, cluster_name, region, project, dry_run):
# checks if the nodepool is already upgraded, if not, offers to upgrade it.
# on Dry Run mode it will only show WHAT would be upgraded.
    if current_version == target_version:
        return {"nodepool": name, "status": "Already up-to-date"}

    log(f"Upgrading node pool '{name}' from {current_version} to {target_version}")
    if dry_run:
        return {"nodepool": name, "status": f"DRY RUN: Would upgrade to {target_version}"}

    try:
        subprocess.check_output([
            "gcloud", "container", "clusters", "upgrade", cluster_name,
            f"--node-pool={name}",
            f"--cluster-version={target_version}",
            f"--region={region}",
            f"--project={project}",
            "--quiet"
        ])

        return {"nodepool": name, "status": "Upgrade successful"}
    except subprocess.CalledProcessError as e:
        return {"nodepool": name, "status": f"Upgrade failed: {e.output.decode()}"}

def get_control_plane_version(cluster_name, region, project, dry_run):
    output = run_cmd([
        "gcloud", "container", "clusters", "describe", cluster_name,
        f"--region={region}",
        f"--project={project}",
        "--format=json"
    ], dry_run=dry_run)
    return output.get("currentMasterVersion", "1.X.X")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--cluster", required=True)
    parser.add_argument("--dry-run", action="store_true", help="Simulate without making changes")
    args = parser.parse_args()

    dry_run = args.dry_run
    log(f"Started {'DRY RUN' if dry_run else 'LIVE'} mode at {datetime.now()}\n")

    connect_to_cluster(args.region, args.project, args.cluster, dry_run)

    control_plane_version_raw = get_control_plane_version(args.cluster, args.region, args.project, dry_run)
    control_plane_version = strip_gke_suffix(control_plane_version_raw)
    log(f"Control plane version: {control_plane_version_raw}")

    nodepools = get_node_pools(args.cluster, args.region, args.project, dry_run)

    upgrades_needed = False
    for np in nodepools:
        current_version = strip_gke_suffix(np.get("version", ""))
        if version.parse(current_version) < version.parse(control_plane_version):
            upgrades_needed = True
            break

    if not upgrades_needed:
        log("All node pools are already at the control plane version. No upgrades needed.")
        write_log_file(args.project, args.region, args.cluster)
        sys.exit(0)

    results = []
    for np in nodepools:
        check_surge_upgrade(np, args.cluster, args.region, args.project, dry_run)
        name = np["name"]
        current_version_raw = np.get("version", "")
        current_version = strip_gke_suffix(current_version_raw)
        if version.parse(current_version) >= version.parse(control_plane_version):
            results.append({"nodepool": name, "status": "Already up-to-date"})
            continue
        result = upgrade_nodepool(name, current_version_raw, control_plane_version_raw,
                                  args.cluster, args.region, args.project, dry_run)
        results.append(result)

    workloads = get_all_workloads(dry_run)
    pdb_covered = get_pdb_coverage(dry_run)
    risky = [w for w in workloads if (w["namespace"], w["name"]) not in pdb_covered]

    if risky:
        log("\nSome workloads have 1 or fewer replicas and are not covered by a PodDisruptionBudget:")
        log(tabulate(risky, headers="keys"))
        if not dry_run:
            choice = input("\nContinue with upgrade anyway? (y/n): ").strip().lower()
            if choice != 'y':
                log("Aborting upgrade due to risky workloads.")
                write_log_file(args.project, args.region, args.cluster)
                sys.exit(0)
        else:
            log("DRY RUN: Would prompt to continue despite risky workloads.")

    log("\nUpgrade Summary:\n")
    log(tabulate(results, headers="keys"))
    write_log_file(args.project, args.region, args.cluster)

if __name__ == "__main__":
    main()
