This was a fun thought exercise. I wanted to showcase some use of AI and I thought of this:

in this script we load all the Alert Manager rules installed on a cluster, dumps them to a file
then uses AI to refine and rewrite the descriptions of those rules, to make them more accurate.
The rules are re-written based on the current rule being evaluated.


# ---
#!/usr/bin/env python3

import argparse
import subprocess
import sys
import re
import os
import yaml
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # This loads variables from .env
# Create an httpx.Client with SSL verification disabled; this is necessary to avoid SSL complications
# due to the corporate VPN
http_client = httpx.Client(verify=False)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
client = OpenAI(
    api_key=api_key,
    http_client=http_client
)

# Below you find the prompt I'm using. This is an example of how to integrate it, since I don't have
# a paid subscription to fully test.
def generate_summary_with_chatgpt(alert_name, expr_text, current_summary=None):
    base_prompt = f"""You are a DevOps assistant. Rewrite the summary for a Prometheus alert.
- It must describe what the alert is about in plain language;
- It must be a single sentence with no more than 60 characters;
- Use context from the expression and alert name if available;
- Be concise but clear;
- Always rewrite if the summary seems too vague or generic;
- Include obvious metrics (for example time frames) from expression into the summary;

Alert: {alert_name}
Expression:
{expr_text}
"""

    if current_summary:
        base_prompt += f"Current summary: {current_summary}\n"

    base_prompt += "New summary:"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": base_prompt}],
            max_tokens=60,
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip('" \n')
        print(f"\n✅ ChatGPT response: {summary}")
        return summary

    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return None

RULES_FILE = "rules.txt"
ENABLE_FLATTEN = True  # Toggle this to False to skip flattening
ENABLE_CHATGPT_SUMMARY = False # Toggle this to True to make ChatGPT rewrite the summaries

def run_kubectl_get_rules():
    try:
        result = subprocess.run(
            ["kubectl", "get", "prometheusrule", "--all-namespaces", "-o", "yaml"],
            capture_output=True,
            check=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Failed to retrieve Prometheus rules:", e.stderr)
        sys.exit(1)

def write_rules_to_file(data):
    with open(RULES_FILE, "w") as f:
        f.write(data)
    print(f"Rules written to {RULES_FILE}")

def flatten_descriptions_in_file():
    print("Flattening multiline 'description' and 'summary' annotations...")

    with open(RULES_FILE, "r") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r'^(\s*)(description|summary):\s*(.*)', line)

        if match:
            indent = match.group(1)
            key = match.group(2)
            inline_value = match.group(3).strip()
            value_lines = []

            # Start with any value on the same line
            if inline_value:
                value_lines.append(inline_value)

            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent > len(indent):
                    value_lines.append(next_line.strip())
                    i += 1
                else:
                    break

            flat_text = ' '.join(value_lines)

            # Escape single quotes by doubling them (YAML single-quote rule)
            escaped_text = flat_text.replace("'", "''")

            # Use single quotes to safely wrap the entire string
            new_lines.append(f"{indent}{key}: '{escaped_text}'\n")
        else:
            new_lines.append(line)
            i += 1

    with open(RULES_FILE, "w") as f:
        f.writelines(new_lines)

    print("Flattening complete.")


def enhance_summaries_with_chatgpt():
    print("Enhancing summaries with ChatGPT...")

    try:
        with open(RULES_FILE, "r") as f:
            data = yaml.safe_load(f)
            print("✅ YAML structure loaded.")
            print("Top-level keys:", list(data.keys()) if data else "⚠️ Empty")
    except yaml.YAMLError as e:
        print(f"❌ Failed to parse YAML: {e}")
        return

    modified = False
    items = data.get("items", [])
    groups = []

    for item in items:
        spec = item.get("spec", {})
        groups.extend(spec.get("groups", []))

    for group in groups:
        for rule in group.get("rules", []):
            expr = rule.get("expr", "")
            annotations = rule.setdefault("annotations", {})
            current_summary = annotations.get("summary")
            alert_name = rule.get("alert", "")

            # Always generate a new summary
            print(f"→ Generating summary for alert: {alert_name}")
            new_summary = generate_summary_with_chatgpt(
                alert_name,
                expr,
                current_summary if current_summary else None
            )
            if new_summary:
                if new_summary != current_summary:
                    annotations["summary"] = new_summary
                    print(f"- Rewritten summary for {alert_name}: {new_summary}")
                    modified = True
                else:
                    print(f"- Summary for {alert_name} unchanged after rewrite.")
            else:
                print(f"- No summary generated for {alert_name}.")

    if modified:
        with open(RULES_FILE, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        print("Summaries forcibly rewritten in rules.txt")
    else:
        print("No summaries rewritten.")
        print("No summaries needed updates.")

def main():
    parser = argparse.ArgumentParser(description="Dump Alertmanager rules from a GKE cluster")

    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--cluster", required=True, help="GKE cluster name")
    
    location_group = parser.add_mutually_exclusive_group(required=True)
    location_group.add_argument("--zone", help="GKE cluster zone")
    location_group.add_argument("--region", help="GKE cluster region")

    args = parser.parse_args()

    print(f"Project: {args.project}")
    print(f"Cluster: {args.cluster}")
    print(f"Location: {'zone ' + args.zone if args.zone else 'region ' + args.region}")

    auth_cmd = [
        "gcloud", "container", "clusters", "get-credentials",
        args.cluster,
        "--project", args.project
    ]
    if args.zone:
        auth_cmd += ["--zone", args.zone]
    else:
        auth_cmd += ["--region", args.region]

    try:
        subprocess.run(auth_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("Failed to authenticate to cluster:", e)
        sys.exit(1)

    print("Fetching Alertmanager rules...")
    rules_yaml = run_kubectl_get_rules()
    write_rules_to_file(rules_yaml)

    if ENABLE_FLATTEN:
        flatten_descriptions_in_file()

    if ENABLE_CHATGPT_SUMMARY:
        enhance_summaries_with_chatgpt()

if __name__ == "__main__":
    main()