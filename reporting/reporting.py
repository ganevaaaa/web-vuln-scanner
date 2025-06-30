import json
# Global list to store findings
findings = []


def record_finding(page_url, action_url, field, payload, vuln_type, evidence):
    new_finding = {
        "page": page_url,
        "action": action_url,
        "field": field,
        "payload": payload,
        "vuln_type": vuln_type
    }
    if new_finding not in [{k: f[k] for k in new_finding} for f in findings]:
        new_finding["evidence"] = evidence

        severity_map = {
            "xss": "medium",
            "sqli": "high",
            "csrf": "medium",
            "cmdi": "high"
        }
        new_finding["severity"] = severity_map.get(vuln_type, "low")
        findings.append(new_finding)


def write_report_json(filename="report.json"):
    with open(filename, "w") as f:
        json.dump(findings, f, indent=2)
    print(f"\n[+] Report written to {filename}")
