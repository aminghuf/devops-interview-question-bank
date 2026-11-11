import re, json, sys, pathlib

src = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])

TOPICS = {
    "01-linux-shell-networking.md": ("linux", "Linux, Shell & Networking"),
    "02-docker.md": ("docker", "Docker & Containers"),
    "03-kubernetes.md": ("k8s", "Kubernetes"),
    "04-cicd-jenkins-git-gitops-ansible.md": ("cicd", "CI/CD, Git, GitOps & Ansible"),
    "05-terraform-iac.md": ("terraform", "Terraform & IaC"),
    "06-aws.md": ("aws", "AWS"),
    "07-gcp-azure-devsecops.md": ("cloud2", "GCP, Azure & DevSecOps"),
    "08-monitoring-observability-sre.md": ("sre", "Monitoring, Observability & SRE"),
    "09-behavioral.md": ("behavioral", "Behavioral & Project Experience"),
    "10-shell-scripting.md": ("scripting", "Shell Scripting (real scripts)"),
    "11-europe.md": ("europe", "Europe: companies, compliance & process"),
}
LEVELS = {"Basic": "basic", "Advanced": "advanced", "Scenario-Based": "scenario"}

questions = []
topics = []
for fname, (tid, tname) in TOPICS.items():
    text = (src / fname).read_text(encoding="utf-8")
    # drop the collapsible index
    text = re.sub(r"<details>.*?</details>", "", text, flags=re.S)
    topics.append({"id": tid, "name": tname})
    level = None
    cur = None
    def flush():
        if cur:
            body_lines = cur.pop("_body")
            body = "\n".join(body_lines).strip()
            cur["body"] = body
            questions.append(cur)
    for line in text.splitlines():
        m = re.match(r"^## (Basic|Advanced|Scenario-Based)\s*$", line)
        if m:
            level = LEVELS[m.group(1)]
            continue
        m = re.match(r"^### Q(\d+)\.\s+(.*)$", line)
        if m:
            flush()
            cur = {"id": f"{tid}-{int(m.group(1))}", "topic": tid, "level": level,
                   "n": int(m.group(1)), "q": m.group(2).strip(), "also": "", "simple": "",
                   "say": "", "asked": "", "_body": []}
            continue
        if cur is None:
            continue
        m = re.match(r"^Also asked as:\s*(.*)$", line)
        if m and not cur["also"]:
            cur["also"] = m.group(1).strip(); continue
        m = re.match(r"^Asked at:\s*(.*)$", line)
        if m and not cur["asked"]:
            cur["asked"] = m.group(1).strip(); continue
        m = re.match(r"^> \*\*In simple words:\*\*\s*(.*)$", line)
        if m and not cur["simple"]:
            cur["simple"] = m.group(1).strip(); continue
        m = re.match(r"^> \*\*What to say to the interviewer:\*\*\s*(.*)$", line)
        if m and not cur["say"]:
            cur["say"] = m.group(1).strip(); continue
        cur["_body"].append(line)
    flush()

# sanity
missing = [q["id"] for q in questions if not (q["simple"] and q["say"] and q["level"])]
print("questions:", len(questions), "missing fields:", missing[:10], len(missing))
from collections import Counter
print(Counter(q["level"] for q in questions))
print(Counter(q["topic"] for q in questions))
out.write_text(json.dumps({"topics": topics, "questions": questions}, ensure_ascii=False), encoding="utf-8")
print("bytes:", out.stat().st_size)
