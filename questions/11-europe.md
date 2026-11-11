# Europe: companies, compliance & process

## Basic

### Q1. Why do most European companies use GitLab CI or GitHub Actions instead of Jenkins, and what does a .gitlab-ci.yml look like?
Asked at: Zalando, Delivery Hero, N26, SAP, Italian scale-ups (Satispay, Prima); German Mittelstand.

> **In simple words:** Jenkins is a workshop you have to build and maintain yourself; GitLab CI is a kitchen that comes with the house. European teams, who often self-host GitLab for data-residency reasons, take the built-in kitchen.

- **Why GitLab CI dominates in Europe:** GitLab is self-hostable on EU servers (GDPR, works-council comfort), the pipeline lives in the repo as code, and runners scale on Kubernetes. Jenkins survives mostly in banks and older enterprises.
- **Why GitHub Actions is second:** same "pipeline as code" model, huge marketplace; chosen by companies already on GitHub Enterprise.
- **Mental model of `.gitlab-ci.yml`:** `stages` run in order, `jobs` inside a stage run in parallel, each job runs in a container `image`, `rules` decide when it runs, `artifacts` and `cache` pass files between jobs.
- Be ready to translate your Jenkins experience: Jenkinsfile stage = GitLab stage, agent = runner, shared library = `include:` templates.

**Example:**

```yaml
stages: [test, build, deploy]
variables: { IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA }
test:
  stage: test
  image: python:3.12
  script: [pip install -r requirements.txt, pytest -q]
build:
  stage: build
  image: docker:27
  services: [docker:27-dind]
  script:
    - docker build -t $IMAGE .
    - docker push $IMAGE
deploy-prod:
  stage: deploy
  script: kubectl set image deploy/api api=$IMAGE
  environment: production
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual   # a human clicks: common change-control pattern in the EU
```

> **What to say to the interviewer:** Most European companies I see run GitLab CI or GitHub Actions because the pipeline lives in the repo and the platform can be self-hosted in the EU. I think in stages, jobs, runners and rules, and I map that straight onto Jenkins concepts when a team still uses it.

### Q2. As an infrastructure engineer, what does GDPR actually require from you?
Asked at: nearly every EU company in the behavioural or security round; N26, Doctolib, Booking.com.

> **In simple words:** GDPR says personal data is borrowed, not owned. You may only keep it for a reason, for a limited time, protected, inside agreed borders, and you must be able to find it and delete it when asked.

The infra-relevant principles:

- **Data minimisation and purpose limitation:** don't collect or log what you don't need. IPs, emails and user IDs in logs are personal data.
- **Storage limitation:** retention policies on logs, backups, metrics, Kafka topics. "Forever" is a finding.
- **Security (Art. 32):** encryption at rest and in transit, access control, audit logs, pseudonymisation.
- **Data subject rights:** right of access and right to erasure must be technically possible, including in caches and backups (or documented why not).
- **Transfers:** data leaving the EU/EEA needs a legal basis (adequacy decision, SCCs); the US Data Privacy Framework exists but companies still prefer EU regions.
- **Breach notification:** 72 hours to the authority, so monitoring and incident process must detect and document fast.
- **Processors:** every SaaS you wire in (PagerDuty, Datadog, a US registry) needs a DPA. The infra engineer is often the one who notices a new tool was added.

**Example:** retention as code in Loki and S3:

```yaml
# loki limits_config
retention_period: 30d
# S3 lifecycle (Terraform)
rule { id = "logs" expiration { days = 30 } noncurrent_version_expiration { noncurrent_days = 7 } }
```

> **What to say to the interviewer:** For me GDPR translates into four engineering habits: no personal data in logs or metrics labels, retention on everything, encryption and audit trails by default, and keeping data inside EU regions unless legal has signed off on a transfer. And I know a breach has a 72-hour clock, so detection matters.

### Q3. Data residency vs data sovereignty: what is the difference, and why is "we use eu-central-1" not the full answer?
Asked at: German and French enterprises, public-sector suppliers, Scaleway/OVH customers, SAP.

> **In simple words:** Residency is *where the data sits*. Sovereignty is *whose laws can reach it*. A safe in Frankfurt owned by an American bank is in Germany, but a US court can still order it opened.

- **Data residency:** the data is stored and processed in a given geography (an EU region). Solves latency and most GDPR transfer questions.
- **Data sovereignty:** the data is subject only to the laws of that geography. A US-headquartered provider is subject to the US CLOUD Act, so EU-region storage alone does not give sovereignty.
- Levels companies talk about: EU region on a hyperscaler, EU region plus customer-held keys (BYOK/HYOK, external KMS), EU-owned provider (OVHcloud, Scaleway, Hetzner, IONOS, STACKIT), and the hyperscalers' sovereign offerings (AWS European Sovereign Cloud, Azure/Google sovereign partner clouds).
- Why interviewers ask: regulated sectors (banks under DORA, hospitals, public sector) have to prove it, and platform teams design for it.

**Example:** restrict Terraform to EU regions and EU-only KMS:

```hcl
provider "aws" { region = "eu-central-1" }
resource "aws_kms_key" "app" { multi_region = false }
# SCP in the org: deny any action outside eu-* regions
```

> **What to say to the interviewer:** Residency is location, sovereignty is jurisdiction. Picking an EU region handles residency; sovereignty needs customer-controlled keys, EU-owned providers or the hyperscalers' sovereign clouds. I design so the data layer can be moved, which is also good resilience practice.

### Q4. When would a European company choose Hetzner, OVHcloud or Scaleway over AWS, and what do you lose?
Asked at: startups in Berlin, Paris, Milan; cost-focused scale-ups; Bending Spoons-style companies.

> **In simple words:** Hetzner is the local hardware store: much cheaper, solid, but you assemble things yourself. AWS is the department store with everything pre-built and a bigger bill.

- **Why they choose it:** 3-10x lower compute and egress cost, EU ownership (sovereignty), simple pricing, strong bare-metal. Egress is often free or nearly free, a big deal versus AWS.
- **What you give up:** fewer managed services (no RDS/MSK equivalent at Hetzner), smaller region count, less mature IAM, weaker ecosystem for Terraform modules and SaaS integrations, you run your own Kubernetes control plane or use their managed offering (Scaleway Kapsule, OVH Managed Kubernetes).
- **Typical pattern:** stateless workloads on Hetzner Kubernetes (k3s/Talos/kubeadm or Cluster API), managed Postgres from a specialist (Aiven, Neon) or self-managed with operators, object storage from the provider or Backblaze/Wasabi, hyperscaler only for one or two managed services.
- Interviewers want to see you can run things without a managed backstop: backups, upgrades, networking, load balancing.

**Example:** Hetzner Kubernetes bootstrap with Terraform (kube-hetzner module):

```hcl
module "kube-hetzner" {
  source = "kube-hetzner/kube-hetzner/hcloud"
  control_plane_nodepools = [{ name = "cp", server_type = "cx22", location = "fsn1", count = 3 }]
  agent_nodepools = [{ name = "work", server_type = "cx32", location = "fsn1", count = 3 }]
}
```

> **What to say to the interviewer:** I'd pick Hetzner or Scaleway when cost or EU ownership matters more than managed services, and I'd keep state in a managed database and object storage so the cluster stays disposable. The trade-off is that I own upgrades, backups and networking, so I'd automate those first.

### Q5. Azure is common in European enterprises. What do you need to know about Entra ID, AKS and Azure DevOps?
Asked at: enterprises and consultancies in Germany, Netherlands, Italy (Accenture, Reply, NTT Data), insurers and banks.

> **In simple words:** In Europe, if a company runs Microsoft 365, it usually runs Azure too, because the identity system is already there. Learn the Azure names for the things you already know.

- **Entra ID (was Azure AD):** the identity backbone. Service principals and managed identities replace access keys; RBAC roles are assigned on scopes (management group > subscription > resource group > resource). Workload identity federation lets AKS pods and GitHub Actions authenticate without secrets.
- **AKS:** managed Kubernetes. Know node pools, Azure CNI vs kubenet, the cluster autoscaler, AKS-managed upgrades, integration with Key Vault via the CSI driver, and Azure Monitor / Container Insights.
- **Azure DevOps:** Repos, Pipelines (YAML), Boards, Artifacts. Pipelines use `stages`/`jobs`/`steps`, agents (Microsoft-hosted or self-hosted scale sets), service connections to Azure, environments with approvals.
- **Landing zones:** enterprises deploy via Cloud Adoption Framework landing zones, Bicep or Terraform (azurerm), Azure Policy for guardrails.

**Example:** AKS pod using a managed identity to read Key Vault, no secret anywhere:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api
  annotations:
    azure.workload.identity/client-id: "<client-id>"
---
# pod: add label azure.workload.identity/use: "true", then the Azure SDK picks up the federated token automatically
```

> **What to say to the interviewer:** I translate my AWS knowledge: Entra ID instead of IAM, managed identities instead of keys, resource groups and subscriptions as scopes, AKS with Azure CNI, and YAML pipelines in Azure DevOps or GitHub Actions. I prefer workload identity federation so no static secrets exist.

### Q6. OpenShift vs vanilla Kubernetes: why do European banks and insurers run OpenShift, and what changes for you?
Asked at: Intesa Sanpaolo, UniCredit, Allianz, Deutsche Bank suppliers, IBM/Red Hat partners, public sector.

> **In simple words:** OpenShift is Kubernetes with the safety rails, the receptionist and the support contract already included. Regulated companies pay for the support contract and the stricter defaults.

- **What OpenShift adds:** opinionated security (SCCs, random UIDs, restricted by default), built-in registry, Routes (before Ingress), integrated OAuth, Operators via OLM, built-in monitoring and logging stacks, Red Hat support and a certified lifecycle.
- **Why regulated companies pick it:** auditors like a vendor-supported, certified platform; on-prem and air-gapped installs; works with existing RHEL and IBM contracts.
- **What changes for you:** containers must not assume root or a fixed UID; use `Route` or Ingress via the router; `oc` CLI alongside `kubectl`; projects instead of namespaces (same thing with extras); Helm charts need SCC-friendly securityContexts; upgrades are cluster-wide, operator-driven.
- Also know the lighter alternatives seen in the EU: Rancher/RKE2 (SUSE, German), Tanzu, plain kubeadm.

**Example:** make an image run under OpenShift's random UID:

```dockerfile
RUN chgrp -R 0 /app && chmod -R g=u /app
USER 1001
```

> **What to say to the interviewer:** OpenShift is Kubernetes plus stricter defaults, built-in registry, routes, operators and vendor support, which is why regulated European companies choose it. For me the practical difference is designing images and charts that run non-root with arbitrary UIDs, and using `oc` where it adds value.

### Q7. GitOps with Argo CD or Flux is the default deployment model in many EU companies. How does it work and why is it preferred?
Asked at: Zalando, Adidas, Spotify, Delivery Hero, N26, most Kubernetes-platform teams.

> **In simple words:** Instead of pushing changes into the cluster, you write down the desired state in Git and a robot inside the cluster keeps reality matching it. Git becomes the audit log.

- **Pull model:** the CI pipeline only builds and pushes an image and bumps a tag in a config repo. Argo CD / Flux watch the repo and reconcile the cluster. No CI runner needs cluster credentials.
- **Why Europeans like it:** auditability (every change is a commit with a reviewer), separation of duties for compliance, easy rollback (`git revert`), drift detection and self-heal, multi-cluster from one repo.
- **Structure:** app-of-apps or ApplicationSets, Kustomize overlays or Helm values per environment, image updater or CI bumps tags, sync waves for ordering, PR-based promotion dev > staging > prod.
- **Pitfalls to mention:** secrets (use SOPS, Sealed Secrets or External Secrets), CRDs ordering, auto-sync on prod versus manual sync with approval.

**Example:** minimal Argo CD Application:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: api, namespace: argocd }
spec:
  project: default
  source: { repoURL: https://gitlab.example.eu/platform/deploy.git, path: apps/api/overlays/prod, targetRevision: main }
  destination: { server: https://kubernetes.default.svc, namespace: api }
  syncPolicy: { automated: { prune: true, selfHeal: true } }
```

> **What to say to the interviewer:** CI builds and pushes, Git holds the desired state, Argo CD or Flux reconciles the cluster. That gives us an audit trail, separation of duties and trivial rollback, which is why it fits compliance-heavy European environments. I keep secrets out of Git with External Secrets or SOPS.

### Q8. Which observability stack would you choose and why do European teams lean towards Grafana, Prometheus and OpenTelemetry over Datadog or New Relic?
Asked at: most mid-size EU companies; Grafana Labs (Swedish) is a frequent reference.

> **In simple words:** European teams like tools they can run on their own servers with open standards, so the data stays in-house and they are not locked to one vendor's price list.

- **Typical stack:** Prometheus (or Mimir/Thanos for scale) for metrics, Loki for logs, Tempo for traces, Grafana for dashboards and alerting, OpenTelemetry Collector as the single agent.
- **Why:** self-hostable in the EU (data residency), open standards (OpenTelemetry) so vendors are swappable, cost predictable at scale, strong Kubernetes integration (kube-prometheus-stack).
- **When SaaS wins:** small teams with no capacity to run storage; Datadog, Elastic Cloud and Grafana Cloud all offer EU regions and DPAs.
- Always mention cardinality control, SLO-based alerting and retention, which is both a cost and a GDPR topic.

**Example:** OpenTelemetry Collector shipping to Loki and Tempo:

```yaml
receivers: { otlp: { protocols: { grpc: {}, http: {} } } }
exporters:
  loki: { endpoint: http://loki:3100/loki/api/v1/push }
  otlp/tempo: { endpoint: tempo:4317, tls: { insecure: true } }
service:
  pipelines:
    logs: { receivers: [otlp], exporters: [loki] }
    traces: { receivers: [otlp], exporters: [otlp/tempo] }
```

> **What to say to the interviewer:** I default to Prometheus, Loki, Tempo and Grafana with OpenTelemetry as the only agent, because it is vendor-neutral, self-hostable in the EU and cost-predictable. I'd move to Grafana Cloud or Datadog in an EU region only if the team cannot carry the operational load.

### Q9. How does on-call work in Europe, and how do you talk about your on-call experience?
Asked at: Spotify, Klarna, Zalando, Booking.com, N26; any "you build it, you run it" team.

> **In simple words:** In Europe, on-call is treated as paid, bounded work, not heroism. Interviewers want to hear that you have carried a pager responsibly and that you improve the system so the pager rings less.

- **Legal frame:** the EU Working Time Directive and national rules (Germany's Arbeitszeitgesetz, Italy's reperibilità) mean on-call is compensated, rest periods are enforced, and rotations are agreed with works councils where they exist. Follow-the-sun across offices is common in larger companies.
- **Culture:** "you build it, you run it" (Adyen, Zalando, Spotify). Product teams own their services; a platform team owns the shared layer. Blameless postmortems are the norm.
- **What to say about yourself:** rotation size and frequency, the tooling (PagerDuty, Opsgenie, Grafana OnCall), how you triage, the worst incident and what you changed afterwards, how you reduced alert noise.
- **Good questions to ask them:** how often does the pager fire, is on-call paid, how are postmortems run, what is the escalation path.

**Example:** an answer skeleton:

```
Rotation: 1 week in 6, two-person primary/secondary, Grafana OnCall.
Volume: ~3 pages/week, down from ~12 after we moved to SLO-based alerts.
Worst page: Kafka consumer lag at 03:00; fixed by increasing partitions and adding a lag SLO.
Follow-up: wrote the runbook, added a dashboard, automated the restart.
```

> **What to say to the interviewer:** I've done one week in six as primary with a secondary, and my focus was shrinking the pager: SLO-based alerts, runbooks and automation cut pages from a dozen a week to a few. I believe on-call should be paid, bounded and blameless, and I'd ask you how yours is run.

### Q10. What does the DevOps / SRE interview process at a European product company usually look like, and what is each round assessing?
Asked at: Monzo, Spotify, Booking.com, Adyen, Zalando, Klarna, Revolut (process questions).

> **In simple words:** Expect fewer brain-teasers and more "show me how you really work": a timeboxed take-home or pairing session, a live troubleshooting or design round, and an hour on how you handled incidents and disagreements.

The common shape (3-5 rounds, three to five weeks):

1. **Recruiter call:** role, salary band, visa, language.
2. **Hiring-manager / "tell me about a project" call:** one hour, no coding; you walk through a project you owned. Monzo and Spotify start here.
3. **Practical exercise:** either a take-home with a timebox (often 3-4 hours, no deadline pressure, README expected) or a pairing session; typical tasks are a Terraform module, a Dockerfile plus pipeline, a small Kubernetes deployment, or a log-parsing script. Adyen and Monzo state that algorithmic coding is not the focus; Booking.com still runs a live coding round, sometimes graph-flavoured.
4. **System design or live troubleshooting:** a payment notification service, a config push system, a logging platform; or a slow Linux box to diagnose while talking.
5. **Behavioural / values:** two engineers or managers, one hour, incidents, ownership, cross-team conflict, what you would change.
6. **Hiring committee / decision.**

What they grade: clarity of explanation over tool name-dropping (teams are multinational), failure-mode thinking, idiomatic and documented work, honesty about trade-offs. Several companies now publish AI rules: fine for preparation, not live in the interview.

**Example:** how to budget a 4-hour take-home:

```
0:00  read spec twice, write README skeleton with assumptions
0:20  working happy path end to end (ugly is fine)
2:00  tests, idempotency, one failure case handled
3:00  clean up, Makefile/`just`, pin versions, document what you skipped
3:45  final run from a clean checkout; stop on time
```

> **What to say to the interviewer:** Most European product companies run a project conversation, a timeboxed practical exercise or pairing, a design or troubleshooting round and a behavioural round, and they grade for clear explanation and failure-mode thinking rather than puzzles. I prepare by having two projects I can narrate end to end and by doing take-homes from a clean checkout.

### Q11. "Walk me through a recent project you had real input on, and what you'd change if you built it again."
Asked at: Monzo (first call), Spotify, Klarna, Zalando hiring-manager rounds.

> **In simple words:** They want to hear that you understood the problem, made choices, saw the consequences and learned. A project where you just followed a ticket does not work here.

Structure (10 minutes max):

1. **Context:** the user or business problem in one sentence, scale numbers.
2. **Constraints:** budget, deadline, team size, compliance.
3. **Your decisions:** two or three real choices and the alternatives you rejected.
4. **Outcome:** measurable (deploy time, MTTR, cost, incidents).
5. **Hindsight:** one thing you'd change and why; one thing you'd keep.

Interviewers probe: "why that choice?", "what broke?", "who disagreed?", "how did you know it worked?". Be ready with the numbers and with one failure.

**Example:** a compact narrative:

```
Problem: deploys took 45 min and failed 1 in 5; two product teams blocked.
Constraints: 3 engineers, no new SaaS allowed (procurement), AWS eu-west-1.
Decisions: GitLab CI with Kubernetes runners instead of Jenkins; Argo CD for deploys; kept Helm, rejected Kustomize to limit retraining.
Outcome: 9-minute deploys, failure rate under 2%, rollback in one revert.
Change: I'd introduce SLOs before the migration so we could prove the reliability gain; keep: GitOps.
```

> **What to say to the interviewer:** I pick a project where I owned decisions, give the context and constraints, walk through two real choices and what I rejected, then the measured outcome. I end with the one thing I'd do differently, usually something about measuring earlier, and the one thing I'd keep.

### Q12. What are NIS2, DORA, the Cyber Resilience Act and the EU AI Act, and what do they mean for an infrastructure team?
Asked at: banks, fintechs, energy and telecom companies, public-sector suppliers; increasingly in security rounds.

> **In simple words:** These are EU laws that turn good practice into obligations: patch and monitor (NIS2), prove your systems and vendors can survive and recover (DORA), ship secure products with updates (CRA), and control high-risk AI systems (AI Act).

- **NIS2 (2024):** cybersecurity baseline for essential and important entities (energy, transport, health, digital infra, many manufacturers). Infra impact: risk management, incident reporting within 24h/72h, supply-chain security, patching, MFA, logging. Management is personally liable.
- **DORA (in force Jan 2025):** financial sector operational resilience. Impact: ICT risk framework, incident classification and reporting, resilience testing including threat-led pen tests, strict rules on third-party providers (cloud concentration risk, exit plans), register of all ICT contracts.
- **Cyber Resilience Act:** products with digital elements need secure-by-design, vulnerability handling and security updates through their lifecycle; SBOMs become practical requirements.
- **AI Act:** risk-tiered rules for AI systems; infra teams see it as logging, traceability and access control around models and data.

For an engineer this means: asset inventory, SBOMs, vulnerability SLAs, immutable audit logs, tested backups and DR, documented exit strategy from your cloud provider.

**Example:** evidence an auditor asks a platform team for:

```
- Vulnerability scan reports per image with fix SLA (Trivy, Grype)
- DR test record: date, RTO/RPO achieved, who ran it
- Access reviews: who had cluster-admin last quarter
- Third-party register: cloud, SaaS, DPAs, exit plan
```

> **What to say to the interviewer:** NIS2 sets the security baseline and incident reporting for critical sectors, DORA does the same with resilience testing and cloud-exit plans for finance, CRA pushes SBOMs and update obligations onto products, and the AI Act adds traceability around models. For my team that is inventory, scanning with SLAs, immutable audit logs and rehearsed DR.

## Advanced

### Q13. Design a GDPR-compliant logging pipeline. How do you handle PII, retention and the right to erasure?
Asked at: Doctolib, N26, Booking.com, Zalando, Trade Republic; any health or fintech company.

> **In simple words:** Treat logs like a hospital corridor: no patient names on the whiteboard, cameras that delete after 30 days, and a way to pull one person's records if they ask.

Design:

1. **Prevent at the source:** structured logging with an allow-list of fields; libraries that hash or drop email, IP, names; code review rule "no request bodies in logs".
2. **Scrub in transit:** OpenTelemetry Collector or Vector processors with regex and field-based redaction for emails, IBANs, card numbers; drop known-sensitive headers.
3. **Pseudonymise instead of identify:** log an internal user ID or a salted hash, keep the mapping in a protected store with its own retention.
4. **Retention by tier:** app logs 30 days, security/audit logs 1-2 years (legal basis), debug logs days. Enforce in Loki/Elastic lifecycle and in object storage.
5. **Access control and audit:** role-based access to logs, every query logged, production log access reviewed.
6. **Erasure:** if logs are pseudonymised and short-lived you argue erasure is satisfied by the retention period; where identifiers exist, delete-by-ID jobs (Elastic delete-by-query, Loki deletion API) and document backups as out of scope with a bounded window.

**Example:** Vector transform to redact:

```toml
[transforms.redact]
type = "remap"
inputs = ["app"]
source = '''
.message = replace(string!(.message), r'[\w.+-]+@[\w-]+\.[\w.]+', "<email>")
.message = replace(.message, r'\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b', "<iban>")
del(.headers.authorization)
'''
```

> **What to say to the interviewer:** I stop PII at the source with field allow-lists, scrub in the collector, pseudonymise identifiers, tier retention with short windows for app logs, lock down and audit log access, and keep a delete-by-ID path for whatever still identifies a person. Short retention plus pseudonymisation is what makes erasure requests tractable.

### Q14. How do you design backup and disaster recovery when data must stay in the EU, and who holds the keys?
Asked at: banks under DORA, insurers, public sector, SAP customers, Scaleway/OVH users.

> **In simple words:** Keep the spare copy in a second EU city, not another continent, lock it with a key the provider cannot read, and prove every quarter that you can actually restore it.

- **Topology:** primary in one EU region, backups and a warm standby in a second EU region (Frankfurt + Paris, Milan + Zurich if Switzerland is acceptable to legal). Cross-region replication must be checked for region pairs that leave the EU/EEA (watch for UK or US pairs).
- **Keys:** customer-managed keys in a KMS located in the EU; for sovereignty, external key management (HYOK) or an HSM you control; separate keys per environment; backups encrypted with their own key so a compromised app key cannot read them.
- **Immutability:** object lock / WORM on backup buckets, separate account or project for backups, no delete permission from the production role (ransomware is the real DR case).
- **RPO/RTO:** define per data class; database PITR for minutes-level RPO; test restores on a schedule and record evidence (DORA asks for it).
- **Exit plan:** backups in a portable format in a second provider or on-prem; regulators now ask how you'd leave your cloud.

**Example:** S3 backup bucket with object lock and an EU-only KMS key:

```hcl
resource "aws_s3_bucket" "bk" { bucket = "acme-backups-eu-west-3" object_lock_enabled = true }
resource "aws_s3_bucket_object_lock_configuration" "bk" {
  bucket = aws_s3_bucket.bk.id
  rule { default_retention { mode = "COMPLIANCE" days = 35 } }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "bk" {
  bucket = aws_s3_bucket.bk.id
  rule { apply_server_side_encryption_by_default { sse_algorithm = "aws:kms" kms_master_key_id = aws_kms_key.backup.arn } }
}
```

> **What to say to the interviewer:** Two EU regions, backups in a separate account with object lock, encrypted with customer-managed keys kept in an EU KMS or our own HSM, defined RPO/RTO per data class and scheduled restore tests with evidence. I'd also keep a portable copy outside the primary provider because regulators ask for an exit plan.

### Q15. How do you run secrets management that survives a security audit?
Asked at: Adyen, N26, Revolut, Klarna, Wise, any PCI or DORA scope.

> **In simple words:** Nobody should know a password, every secret should rotate on its own, and there must be a receipt for every time one was read.

- **Source of truth:** HashiCorp Vault / OpenBao, or the cloud secret manager (AWS Secrets Manager, Azure Key Vault), never Git. If GitOps needs them: External Secrets Operator pulling into Kubernetes, or SOPS with age/KMS for encrypted-at-rest in Git.
- **Identity over credentials:** workloads authenticate via Kubernetes service accounts, IAM roles, workload identity; CI uses OIDC federation to the cloud, no long-lived tokens in CI variables.
- **Dynamic and rotated:** Vault database roles issue short-lived DB credentials; cloud keys rotate automatically; static secrets have an owner and a rotation date.
- **Least privilege and separation:** per-environment paths, policies per app, break-glass accounts with alerts.
- **Auditability:** Vault audit device or CloudTrail, shipped to immutable storage; alerts on unusual reads; quarterly access review.
- **Scanning:** gitleaks/trufflehog in pre-commit and CI; registry scanning for baked-in secrets.

**Example:** External Secrets Operator pulling from Vault:

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata: { name: db, namespace: api }
spec:
  secretStoreRef: { name: vault, kind: ClusterSecretStore }
  refreshInterval: 1h
  target: { name: db-creds }
  data:
    - secretKey: password
      remoteRef: { key: apps/api/db, property: password }
```

> **What to say to the interviewer:** Vault or the cloud secret manager as the only source, workloads and CI authenticating by identity through OIDC rather than keys, short-lived dynamic credentials where possible, External Secrets into Kubernetes, and audit logs shipped somewhere immutable with reviews. That is the set an auditor can walk through end to end.

### Q16. How do you build a CI/CD pipeline for PCI-DSS or otherwise regulated services without killing delivery speed?
Asked at: Adyen (explicit theme), Monzo, Revolut, Klarna, Nexi, SumUp, Mollie.

> **In simple words:** Auditors want proof that no single person can silently change production. Automate the proof so engineers keep shipping daily.

Controls as code:

- **Separation of duties:** merge requires a reviewer who is not the author (branch protection, CODEOWNERS); the deploy is done by the GitOps controller, not a person.
- **Change record:** the PR plus pipeline run is the change ticket; link to Jira only for high-risk changes; production deploys gated by a manual approval in a protected environment.
- **Integrity:** signed commits (gitsign/GPG), signed images (cosign), SLSA provenance attestations, admission control that only runs signed images from your registry.
- **Scanning gates:** SAST, dependency and container scanning with severity thresholds, SBOM stored per release.
- **Segmentation:** separate CI runners and credentials for the cardholder-data environment, no shared runners.
- **Evidence retention:** pipeline logs, approvals and artifacts kept for a year; immutable.
- **Speed:** keep gates fast (cached scanners), use feature flags so deploys stay small, automate the evidence so audits don't need humans.

**Example:** Kyverno policy admitting only signed images:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: verify-images }
spec:
  validationFailureAction: Enforce
  rules:
    - name: cosign
      match: { any: [{ resources: { kinds: [Pod] } }] }
      verifyImages:
        - imageReferences: ["registry.example.eu/*"]
          attestors: [{ entries: [{ keyless: { issuer: https://gitlab.example.eu, subject: "https://gitlab.example.eu/platform/*" } }] }]
```

> **What to say to the interviewer:** I encode the controls: reviewer-not-author merges, signed commits and images, provenance attestations, scanning gates with thresholds, GitOps doing the deploy and a manual approval only for production, with evidence retained automatically. That satisfies separation of duties and change control while teams still deploy several times a day.

### Q17. How do you run a zero-downtime database schema migration on a live payments system?
Asked at: Adyen, Monzo, Klarna, Trade Republic, Booking.com.

> **In simple words:** Never swap the engine while the car is moving. Add the new part beside the old one, move traffic over gradually, then remove the old part.

Expand / contract pattern:

1. **Expand:** add new columns/tables as nullable with defaults; create indexes concurrently; never lock the table (Postgres `CREATE INDEX CONCURRENTLY`, avoid `ALTER TABLE` that rewrites).
2. **Dual write:** deploy app version that writes both old and new shape, reads old.
3. **Backfill:** batched, rate-limited job copying historical rows; monitor replication lag and locks.
4. **Switch reads:** feature flag flips reads to the new shape; verify with shadow comparisons.
5. **Contract:** stop writing the old shape, later drop the column in a separate release.

Tools: Flyway/Liquibase for versioned migrations, gh-ost or pt-online-schema-change for MySQL, pgroll or reshape for Postgres. Rules: every migration backwards compatible with the previous app version, migrations separate from deploys, tested against a production-sized copy, rollback plan for each step.

**Example:** safe Postgres steps:

```sql
ALTER TABLE payments ADD COLUMN merchant_ref text;          -- fast, no rewrite
CREATE INDEX CONCURRENTLY payments_merchant_ref_idx ON payments(merchant_ref);
-- backfill in batches of 5k with sleep; app dual-writes meanwhile
-- later release:
ALTER TABLE payments ALTER COLUMN merchant_ref SET NOT NULL; -- after backfill and validation
```

> **What to say to the interviewer:** Expand, dual-write, backfill in batches, switch reads behind a flag, then contract in a later release, with every step compatible with the previous app version and indexes built concurrently. The key rule is that no single deploy both changes the schema and depends on it.

### Q18. Design multi-region failover for a transaction service without losing or duplicating transactions.
Asked at: Adyen (explicit theme), Mollie, Nexi, Wise, SumUp.

> **In simple words:** Two cash registers in two cities share one ledger. If one city goes dark, customers are sent to the other, and the ledger makes sure no payment is counted twice or lost.

- **Choose the model:** active-passive with synchronous replication inside a region pair (simplest, correct), or active-active with partitioning by merchant/region so each transaction has one home. Avoid active-active writes to the same rows.
- **Idempotency:** every request carries an idempotency key stored with the result; retries after failover return the stored result instead of a second charge.
- **Durable intake:** accept into a replicated queue (Kafka with `acks=all`, min ISR across zones) before acknowledging; processing is at-least-once with idempotent consumers.
- **Failover mechanics:** health-based DNS or global load balancer (Route 53, Cloudflare), short TTLs, automated promotion of the standby database with fencing so the old primary cannot accept writes (split-brain).
- **Reconciliation:** a settlement job compares ledgers across regions and flags gaps; this is how real payment companies prove nothing was lost.
- **Testing:** game days that kill a region; measure RPO (acceptable 0 for the ledger) and RTO.

**Example:** idempotent charge handler sketch:

```python
def charge(req):
    key = req.headers["Idempotency-Key"]
    if (r := store.get(key)): return r          # same answer on retry
    with db.transaction():
        result = ledger.apply(req)              # writes to replicated primary
        store.put(key, result, ttl=24*3600)
    return result
```

> **What to say to the interviewer:** Durable, replicated intake before acknowledging, idempotency keys so retries never double-charge, a single write home per transaction, automated failover with fencing to avoid split-brain, and a reconciliation job that proves the ledgers match. I'd test it with region-kill game days and track RPO as zero for the ledger.

### Q19. We want to cut our cloud bill by 40%. Where do you look first, and how do you prove the saving?
Asked at: Zalando, Delivery Hero, Bending Spoons, Scalapay, Italian and German scale-ups post-2023.

> **In simple words:** Find the lights left on in empty rooms, then the rooms you are renting but not using, then negotiate the rent. Measure the bill per customer order so the saving is real, not an accident.

Order of attack:

1. **Visibility:** tag everything (team, service, environment); cost allocation in Kubernetes with OpenCost/Kubecost; unit metric such as cost per 1,000 requests or per order.
2. **Waste:** idle non-prod at night (scale to zero with KEDA or schedules), orphaned volumes, snapshots, old images, unattached IPs, over-provisioned requests (VPA recommendations).
3. **Right-size and pack:** requests tuned to p95 usage, Karpenter or cluster autoscaler with consolidation, bin-packing, ARM (Graviton) nodes.
4. **Buy smarter:** spot for stateless and batch, Savings Plans/Reserved for the stable base, S3 lifecycle to cheaper tiers, cut cross-AZ and egress traffic (often hidden), managed services only where they earn their price.
5. **Architecture:** move heavy stateless workloads to Hetzner/OVH if sovereignty and cost both point that way; replace expensive SaaS (logs!) with self-hosted Loki.
6. **Prove it:** monthly report of total spend and the unit metric, before and after, with the baseline frozen.

**Example:** KEDA cron scaler for non-prod:

```yaml
triggers:
  - type: cron
    metadata: { timezone: Europe/Rome, start: "0 8 * * 1-5", end: "0 20 * * 1-5", desiredReplicas: "2" }
```

> **What to say to the interviewer:** First tagging and a unit cost metric, then the free wins: idle environments, orphaned storage, oversized requests. Then autoscaling with consolidation and spot, commitments for the stable base, and a hard look at egress and logging spend. I report cost per order monthly so the 40% is measurable, not a one-off.

### Q20. How do you manage configuration drift across thousands of servers or dozens of clusters?
Asked at: Booking.com (explicit), OVHcloud, Deutsche Telekom, large German enterprises.

> **In simple words:** Stop editing servers by hand, rebuild them from a recipe, and run a checker that shouts when reality differs from the recipe.

- **Prefer immutability:** bake images (Packer, Talos for Kubernetes nodes), replace instead of patch; node pools roll on image change.
- **Declarative config with reconciliation:** Ansible in pull or scheduled mode (ansible-pull, AWX schedules), Puppet/Salt agents that enforce every 30 minutes, or Kubernetes with GitOps self-heal.
- **Detect drift:** `terraform plan` on a schedule (or Atlantis/Spacelift/env0 drift detection) with alerts on non-empty plans; Argo CD out-of-sync status; `ansible --check --diff` nightly.
- **Block the cause:** no SSH to production (or audited, time-bound via Teleport/Boundary), IAM denies console edits, OPA/Kyverno policies.
- **Inventory:** CMDB or tags as source of truth, compliance scans (OpenSCAP, CIS benchmarks) as evidence for NIS2/DORA.

**Example:** nightly drift check in GitLab CI:

```yaml
drift:
  stage: check
  script:
    - terraform init -input=false
    - terraform plan -detailed-exitcode -input=false -out=plan.bin || CODE=$?
    - 'if [ "${CODE:-0}" = "2" ]; then echo "DRIFT DETECTED"; exit 1; fi'
  rules: [{ if: $CI_PIPELINE_SOURCE == "schedule" }]
```

> **What to say to the interviewer:** Immutable images and replace-not-patch where I can, a reconciling config system where I can't, scheduled drift detection with Terraform plan exit codes and Argo CD sync status, and removing the ability to hand-edit production. Drift then becomes an alert with a diff instead of a mystery.

### Q21. What is platform engineering, what is an internal developer platform like Backstage, and how do you measure whether it helps?
Asked at: Spotify (Backstage originators), Zalando, SAP, Adidas, DAZN, Deutsche Bahn, Doctolib.

> **In simple words:** A platform team builds the paved road so product teams don't each build their own: one way to create a service, deploy it, get logs, alerts and a database, in minutes instead of weeks.

- **Platform as a product:** internal customers, a roadmap, docs, support; "golden paths" that are the easy default, not a mandate.
- **Typical IDP pieces:** Backstage portal with software catalog and templates, GitOps deploy, Crossplane or Terraform modules for self-service infra, standard observability and CI templates, policy guardrails.
- **Measuring:** DORA metrics (deploy frequency, lead time, change failure rate, MTTR), time to first deploy for a new service, number of tickets to the platform team, developer satisfaction surveys (DevEx/SPACE), adoption of golden paths.
- **Anti-patterns:** building for yourself, mandating tools without migration help, no on-call for the platform.

**Example:** Backstage software template that scaffolds a service with CI and Argo CD app:

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata: { name: go-service }
spec:
  parameters: [{ properties: { name: { type: string }, team: { type: string } } }]
  steps:
    - id: fetch
      action: fetch:template
      input: { url: ./skeleton, values: { name: "${{ parameters.name }}" } }
    - id: publish
      action: publish:gitlab
      input: { repoUrl: "gitlab.example.eu?owner=${{ parameters.team }}&repo=${{ parameters.name }}" }
    - id: register
      action: catalog:register
```

> **What to say to the interviewer:** Platform engineering treats the internal platform as a product: golden paths for creating, deploying and observing a service, self-service infra behind guardrails, a portal like Backstage for discovery. I'd judge it by time-to-first-deploy, DORA metrics and whether teams choose the paved road without being forced.

### Q22. How do you set SLOs and use error budgets to settle the reliability-versus-velocity argument with product teams?
Asked at: Booking.com (explicit), Spotify, Klarna, Zalando, Google SRE-style loops in Zurich and Dublin.

> **In simple words:** Agree with the business how much failure is acceptable, measure it, and let that number decide: budget left, ship features; budget gone, fix reliability. Nobody argues with a number they agreed on.

- **SLI:** a user-facing ratio: good requests / all requests (availability), requests under 300 ms / all (latency), freshness for pipelines.
- **SLO:** target over a window, for example 99.9% over 30 days; derived from user needs and cost, not from the current number.
- **Error budget:** 1 - SLO; 99.9% monthly is about 43 minutes of full outage. Burn-rate alerts (fast burn 14x over 1h, slow burn 6x over 6h) replace threshold alerts.
- **Policy:** written in advance: when budget is exhausted, feature releases pause, the team works on reliability, and postmortem actions get priority. That is the agreement that ends the argument.
- **Conversation:** show product the budget dashboard; when they want a risky launch, spend budget consciously.

**Example:** Prometheus burn-rate alert:

```yaml
- alert: ApiErrorBudgetFastBurn
  expr: |
    (sum(rate(http_requests_total{job="api",code=~"5.."}[1h])) / sum(rate(http_requests_total{job="api"}[1h]))) > (14 * 0.001)
    and
    (sum(rate(http_requests_total{job="api",code=~"5.."}[5m])) / sum(rate(http_requests_total{job="api"}[5m]))) > (14 * 0.001)
  for: 2m
  labels: { severity: page }
```

> **What to say to the interviewer:** Define user-facing SLIs, agree SLOs with product, and turn the remainder into an error budget with a written policy: budget available means ship, budget exhausted means reliability work first. Burn-rate alerts page on real user impact, and the budget dashboard replaces opinion in the velocity debate.

### Q23. How do you upgrade Kubernetes across many production clusters without downtime?
Asked at: Adyen (explicit), Zalando, Deutsche Telekom, Booking.com, SAP.

> **In simple words:** Replace the floor one tile at a time while people keep walking on it, and check first that no furniture was built for the old floor.

1. **Read release notes and API deprecations:** `kubectl deprecations` / Pluto, kube-no-trouble; fix manifests and Helm charts before touching the cluster. Check add-on compatibility (CNI, CSI, ingress, cert-manager, Argo CD).
2. **Order:** non-prod first, one prod cluster at a time, control plane before nodes, never skip minor versions.
3. **Nodes:** new node pool on the new version, cordon and drain old nodes respecting PodDisruptionBudgets, surge capacity so draining never reduces replicas; immutable node images (Talos, Bottlerocket) make this a replace.
4. **Protect workloads:** every service has >1 replica, PDBs, topology spread, readiness probes, graceful shutdown (preStop, terminationGracePeriodSeconds).
5. **Observe:** error budget and key SLOs during the roll; automated pause on burn.
6. **Rollback:** control plane cannot be downgraded on most managed platforms, so keep old node pool until verified, and have the cluster recreatable from code (Cluster API, Terraform) as the ultimate fallback.

**Example:** safe drain:

```
kubectl cordon ip-10-0-1-5
kubectl drain ip-10-0-1-5 --ignore-daemonsets --delete-emptydir-data --timeout=600s
# PDB that keeps at least 2 of 3 replicas up
apiVersion: policy/v1
kind: PodDisruptionBudget
spec: { minAvailable: 2, selector: { matchLabels: { app: api } } }
```

> **What to say to the interviewer:** Deprecation scan and add-on compatibility first, then control plane and a fresh node pool per cluster, draining behind PodDisruptionBudgets with surge capacity, watching SLOs and pausing on burn. One cluster at a time, old node pool kept until verified, and the cluster recreatable from code as the real rollback.

### Q24. How do you secure the software supply chain (SBOM, signing, admission) and what does the Cyber Resilience Act change?
Asked at: Siemens, Bosch, SAP, Philips, telecoms, any company shipping software products in the EU.

> **In simple words:** Know every ingredient in what you ship, seal the package so nobody tampers with it, and only run packages whose seal you recognise. The CRA makes the ingredient list and the security updates a legal duty.

- **SBOM:** generate per build (Syft, Trivy, CycloneDX/SPDX), store with the artifact, scan continuously for new CVEs (Grype, Dependency-Track).
- **Provenance:** SLSA attestations from CI describing how the artifact was built; reproducible builds where feasible.
- **Signing:** cosign keyless via OIDC in CI; verify in admission (Kyverno/Sigstore policy controller); signed Helm charts and Terraform modules.
- **Dependencies:** pin and hash-lock, private proxy registries (Artifactory, Nexus, GitLab registry), base images from a curated set with scheduled rebuilds, Renovate/Dependabot.
- **Runtime:** admission policies for non-root, read-only FS, no privileged; Falco for runtime anomalies.
- **CRA:** manufacturers of products with digital elements must handle vulnerabilities, provide security updates for the support period, report actively exploited vulnerabilities to ENISA within 24h, and keep an SBOM. For platform teams that means SBOMs as release artifacts and a vulnerability-handling process with SLAs.

**Example:** GitLab job producing SBOM and signing:

```yaml
sbom-sign:
  image: alpine:3.20
  id_tokens: { SIGSTORE_ID_TOKEN: { aud: sigstore } }
  script:
    - syft $IMAGE -o cyclonedx-json > sbom.json
    - cosign sign --yes $IMAGE
    - cosign attest --yes --predicate sbom.json --type cyclonedx $IMAGE
  artifacts: { paths: [sbom.json], reports: { cyclonedx: sbom.json } }
```

> **What to say to the interviewer:** SBOM and SLSA provenance per build, keyless signing in CI, admission that only runs verified images, locked and proxied dependencies, and runtime policy. The CRA turns SBOMs, security updates and 24-hour vulnerability reporting into obligations, so I treat the SBOM as a release artifact with an owner and a scanning SLA.

## Scenario-Based

### Q25. Take-home: "Deploy a small web app with Terraform, Kubernetes and a CI pipeline; timebox 4 hours." What do you deliver and what are graders looking for?
Asked at: Monzo, N26, Zalando, Klarna, Delivery Hero, Qonto, Satispay, most EU scale-ups.

> **In simple words:** They are not grading how much you built. They are grading whether a colleague could run it, understand it, and trust it on Monday morning.

Deliver:

- **README first:** what it does, how to run from a clean machine (`make up`), assumptions, what you skipped and why, how you would productionise.
- **Terraform:** a module with variables and outputs, remote state mentioned (even if local for the exercise), `terraform fmt`/`validate`, pinned providers, no secrets in code.
- **Kubernetes:** Deployment with resources, probes, non-root securityContext, Service, Ingress, HPA or at least 2 replicas, PDB; Helm or Kustomize, not raw copy-paste.
- **CI:** lint, test, build, scan (Trivy), push, deploy; pipeline runs green on the repo; pinned image tags by digest or commit SHA.
- **Proof:** a test (even a smoke `curl`), a short Makefile, `.gitignore`, conventional commits.

Graders look for: idiomatic structure, security defaults, idempotency (`make up` twice works), honesty in the README, and time discipline. Over-building past the timebox is a negative at Monzo-style companies.

**Example:** README skeleton:

```
## Run: make up (kind + helm + app), make test, make down
## Decisions: Helm over Kustomize (team familiarity); nginx ingress; HPA on CPU
## Not done (timebox): TLS via cert-manager, OPA policies, remote state backend
## Next: SLOs, Argo CD, Vault for the DB password
```

> **What to say to the interviewer:** I'd ship a working happy path within the timebox: a Terraform module, a Helm chart with probes, resources, non-root and a PDB, a pipeline that lints, tests, scans and deploys, and a README with run steps, decisions and an honest list of what I skipped. I stop at the timebox and say so.

### Q26. Live session: "This Linux server is slow. Find out why while talking us through it."
Asked at: Booking.com, Spotify, OVHcloud, Hetzner, Scaleway, Deutsche Telekom; classic EU SRE round.

> **In simple words:** Act like a doctor: pulse, breathing, temperature, then specific tests. Say what you expect before each command, and what you learned after.

Triage order (narrate it):

1. **Load and CPU:** `uptime`, `top`/`htop`: load vs cores, user vs system vs iowait vs steal. High iowait means disk; high steal means noisy neighbour (common on shared VMs).
2. **Memory:** `free -m`, `vmstat 1`: swapping? `dmesg -T | grep -i oom`.
3. **Disk:** `iostat -xz 1` (await, %util), `df -h` and `df -i` (inodes), `iotop`.
4. **Network:** `ss -s`, `ss -tan state established | wc -l`, `sar -n DEV 1`, retransmits, conntrack table full.
5. **Processes:** `ps -eo pid,ppid,stat,pcpu,pmem,cmd --sort=-pcpu | head`, zombies, `strace -c -p`, `perf top` if allowed.
6. **Recent change:** `journalctl -S -1h`, package or deploy logs, cron at the same minute.

Then a hypothesis, a targeted fix, and how you'd prevent it (alert, limit, runbook).

**Example:** first 60 seconds:

```
uptime; top -bn1 | head -20
free -m; vmstat 1 5
iostat -xz 1 3; df -h; df -i
ss -s; dmesg -T | tail -30
journalctl -S -30min -p warning
```

> **What to say to the interviewer:** I check load against cores and the CPU split first, then memory and OOMs, then disk latency and inodes, then sockets and conntrack, then the top processes and the last hour of logs for a change. I state the hypothesis before each step. Most slow boxes are iowait, a swap storm or a noisy neighbour, and I'd finish by adding the alert that would have caught it.

### Q27. Design a payment-processing pipeline that loses no transactions during a partial outage.
Asked at: Adyen (explicit), Mollie, SumUp, Wise, Nexi.

> **In simple words:** Write the order down in a book that is copied to three places before you say "thank you", then process it from the book; if a worker faints, another picks up the same page.

- **Edge:** accept the request, validate, assign an idempotency key, persist to a replicated log (Kafka with replication factor 3, `acks=all`, `min.insync.replicas=2`) across availability zones, only then acknowledge to the merchant.
- **Processing:** consumers with manual offset commit after the ledger write; exactly-once via idempotent writes plus transactional outbox for downstream events.
- **Ledger:** strongly consistent database with synchronous replication; the single source of truth; appends only.
- **Partial outage handling:** circuit breakers and bulkheads per acquirer/bank; retries with backoff and jitter; dead-letter topic with alerting and replay tooling; timeouts shorter than the merchant's.
- **Degraded modes:** store-and-forward when a downstream bank is down, with clear state (pending) exposed to the merchant.
- **Verification:** reconciliation jobs comparing intake log, ledger and acquirer reports; game days killing a zone or a consumer group.

**Example:** Kafka producer settings:

```properties
acks=all
enable.idempotence=true
retries=2147483647
max.in.flight.requests.per.connection=5
min.insync.replicas=2   # topic level, with replication.factor=3
```

> **What to say to the interviewer:** Durable replicated intake before acknowledgement, idempotent at-least-once processing into an append-only ledger with an outbox for downstream events, circuit breakers and store-and-forward per external partner, dead-letter with replay, and reconciliation that proves intake equals ledger. Partial outages then degrade to pending states, never to lost transactions.

### Q28. Design a service that sends a notification when a payment arrives. Where could it fail?
Asked at: Monzo (design round style), Revolut, N26, Qonto, Satispay.

> **In simple words:** A doorbell wired to the bank account. The exercise is really: list every way the doorbell can stay silent or ring twice, and decide which ones you accept.

Architecture: payment service emits `payment.received` via transactional outbox to a topic; notification service consumes, looks up preferences and device tokens, calls push (APNs/FCM), SMS and email providers, records delivery state; a retry/dead-letter path and a user-visible inbox as the fallback.

Failure modes to name:

- Event never published (write committed, publish failed) -> outbox pattern.
- Duplicate events -> idempotency key per payment and channel.
- Consumer lag -> SLO on notification latency, autoscale on lag (KEDA).
- Provider down or rate-limiting -> circuit breaker, queue per provider, fallback channel.
- Stale device tokens -> handle provider feedback, clean up.
- Wrong user preferences or quiet hours -> rules evaluated at send time.
- PII in logs/events -> minimal payload (payment ID, not amount or counterparty, fetched on open).
- Ordering (refund before payment) -> partition by account, sequence numbers.
- Thundering herd at salary day -> pre-scale, batching.

**Example:** outbox table and relay:

```sql
CREATE TABLE outbox (id uuid primary key, aggregate_id uuid, type text, payload jsonb, created_at timestamptz, published_at timestamptz);
-- same transaction as the payment insert; a relay publishes rows where published_at is null and marks them
```

> **What to say to the interviewer:** Outbox from the payment write, a topic partitioned by account, a notification consumer with idempotency per payment and channel, per-provider circuit breakers and queues, delivery state and an in-app inbox as the guaranteed fallback. Then I walk the failure list: lost publish, duplicates, lag, provider outages, stale tokens, ordering, PII and salary-day spikes.

### Q29. Design a config push system that distributes configuration to thousands of servers safely.
Asked at: Booking.com (listed as a hard design question), Spotify, Cloudflare EU, OVHcloud.

> **In simple words:** Like a newspaper: one editor approves an edition, it is printed with a version number, delivered to every doorstep, and if an edition has a misprint you can reprint yesterday's in minutes.

- **Source of truth:** config in Git with schema validation and review; versioned, immutable artifacts (content-addressed).
- **Distribution:** pull-based agents polling or long-polling a config service (or watching etcd/Consul); push via fan-out is fragile at scale. Agents verify signatures.
- **Rollout control:** staged canaries (1% -> 10% -> 50% -> 100%) keyed by server cohort, automatic halt on health signals, kill switch to pin a version.
- **Safety:** agents validate before applying, keep the last-known-good, apply atomically (write temp, rename), and report applied version to a central store for drift visibility.
- **Observability:** metrics on version spread, time to converge, failures; dashboard showing which fleet runs what.
- **Scale concerns:** caching layer/CDN for the artifact, jittered polling, backoff, regional replicas of the config service.

**Example:** agent loop sketch:

```python
while True:
    desired = client.get_desired(cohort, current_version)   # long-poll
    if desired.version != current_version:
        blob = fetch(desired.url); verify(blob, desired.sig); validate(blob)
        atomic_write("/etc/app/config.yaml", blob); reload_app()
        if not healthy(): atomic_write("/etc/app/config.yaml", last_good); reload_app(); report("rolled_back")
        else: last_good = blob; current_version = desired.version; report("applied")
    sleep(jitter(30))
```

> **What to say to the interviewer:** Git as source with validation, immutable signed versions, pull-based agents with jittered long-polling, cohort-based canary rollout that halts on health, atomic apply with last-known-good rollback, and a central view of which version each server reports. That gives safety at scale and a way to pin or revert in minutes.

### Q30. Black Friday is in three weeks and traffic will be 8x normal. How do you plan capacity and prove the platform will hold?
Asked at: Zalando, Zalando Payments, Booking.com, Vinted, Allegro, Italian e-commerce (Yoox, Subito).

> **In simple words:** Find the narrowest pipe, widen it or protect it, rehearse the flood with fake water, and have a plan for the moment it still overflows.

1. **Model:** peak RPS per service from last year times growth; identify the critical path (search, cart, checkout, payment).
2. **Find limits:** load test to failure in staging with production-like data (k6, Gatling); watch databases, connection pools, external partners' rate limits, DNS and TLS termination, not just pods.
3. **Scale the hard parts:** databases (read replicas, connection pooling with PgBouncer, caching), queues (partitions), external quotas raised in advance with the provider.
4. **Scale the easy parts:** HPA tuned for fast scale-up, cluster autoscaler headroom or pre-warmed nodes, raised cloud quotas, CDN for static and cacheable pages.
5. **Protect:** rate limiting, queue-based waiting room, graceful degradation flags (hide recommendations before breaking checkout), circuit breakers.
6. **Rehearse:** game day at 8x in a production-like environment, change freeze for the week, war room, runbooks, clear rollback.
7. **Observe:** SLO dashboards per step of the funnel, business metric (orders/min) on the same screen.

**Example:** k6 ramp to peak:

```javascript
export const options = { stages: [ { duration: "10m", target: 2000 }, { duration: "30m", target: 8000 }, { duration: "10m", target: 0 } ],
  thresholds: { http_req_failed: ["rate<0.01"], http_req_duration: ["p(95)<500"] } };
```

> **What to say to the interviewer:** Model peak per service, load test to breaking point to find the real bottleneck, which is usually the database or a partner quota, fix or protect it, pre-scale the cluster and raise quotas, add degradation flags and a waiting room, then rehearse at target load under a change freeze with the funnel and orders-per-minute on one dashboard.

### Q31. A customer invokes their right to erasure. Their data is in Postgres, Kafka, S3 backups and logs. What do you do?
Asked at: Doctolib, N26, Trade Republic, Vinted, Booking.com, any B2C company.

> **In simple words:** Delete what you can find, make the rest unreadable, and write down exactly what you did and why some copies expire on their own instead of being deleted today.

- **Primary stores:** delete or anonymise the rows (keep the order history as anonymous if accounting law requires retention; GDPR allows legal-obligation exceptions).
- **Kafka:** topics are append-only; use compacted topics with tombstones for keyed user data, short retention for event topics, or crypto-shredding: encrypt per-user with a key and delete the key.
- **Search and caches:** delete from Elasticsearch, Redis, CDN caches; verify.
- **Logs:** pseudonymised and short retention; delete-by-ID where identifiers exist.
- **Backups:** deleting inside backups is impractical; document that backups are retained for N days and the record will not be restored (restore procedure must re-apply erasures), or use crypto-shredding.
- **Third parties:** notify processors (CRM, email provider, analytics) via their APIs.
- **Evidence:** a ticket with timestamps, systems covered, exceptions and legal basis; 30-day deadline.

Automate it: an erasure service that fans out to each system's deletion endpoint and records results.

**Example:** crypto-shredding sketch:

```
user_key = KMS.generate_data_key(user_id)        # stored in a key table
event.payload = encrypt(user_key, payload)       # in Kafka, S3, logs
erasure: delete user_key -> all copies become unreadable without touching the data
```

> **What to say to the interviewer:** Delete or anonymise in the primary database, tombstones or crypto-shredding for Kafka, delete from search and caches, rely on short pseudonymised retention for logs, document the backup window with a rule that restores re-apply erasures, notify processors, and record everything with the legal basis for any exception. I'd build this as a fan-out erasure service so it is repeatable.

### Q32. A regulator or auditor asks you to prove where customer data lives and who accessed it in the last 90 days. How do you answer?
Asked at: banks under DORA, insurers, Adyen/Mollie compliance rounds, public-sector suppliers.

> **In simple words:** Hand over a map and a guest book: a list of every place the data is stored, and a tamper-proof log of every person and system that opened the door.

- **Data map:** inventory of data stores with classification and region, generated from code (Terraform state, Kubernetes manifests, cloud asset inventory such as AWS Config or Azure Resource Graph) rather than a spreadsheet; SCPs/Azure Policy proving regions are restricted.
- **Access logs:** cloud audit logs (CloudTrail, Azure Activity Log), database audit logs (pgAudit), Kubernetes audit logs, Vault audit, SSH/bastion session recordings (Teleport); all shipped to immutable, write-once storage with retention of at least one year.
- **Identity:** SSO with MFA so every access maps to a person; JIT elevated access with approvals; quarterly access reviews with sign-off.
- **Report:** query the logs for the data stores in scope, group by principal, attach the review evidence; be able to explain anomalies.
- **Controls as evidence:** policy-as-code checks in CI, drift detection reports, DR tests.

**Example:** CloudTrail Lake query for S3 object reads on the customer bucket:

```sql
SELECT userIdentity.arn, eventName, eventTime, requestParameters
FROM <event-data-store>
WHERE eventSource = 's3.amazonaws.com' AND requestParameters LIKE '%customer-data-eu%'
  AND eventTime > date_add('day', -90, now())
ORDER BY eventTime DESC
```

> **What to say to the interviewer:** A data map generated from infrastructure code and cloud asset inventory with region policies attached, and immutable audit logs from the cloud, databases, Kubernetes, Vault and bastions, all tied to named identities through SSO and JIT access. I can query 90 days by store and principal and attach the quarterly access reviews as evidence.

### Q33. The pager fires at 03:00 for the payments API. Walk us through from alert to postmortem.
Asked at: Adyen (explicit "own an incident end to end"), Monzo, Klarna, Spotify, Booking.com.

> **In simple words:** Stop the bleeding first, understand second, and fix the system third. Keep people informed the whole way, and afterwards fix the cause without hunting for someone to blame.

1. **Acknowledge and assess (2 min):** read the alert, open the SLO dashboard, decide severity from user impact; declare the incident in the channel, take the incident-commander role or hand it over.
2. **Mitigate (minutes):** rollback the last deploy, failover, scale, feature flag off, rate limit; prefer the reversible action. Communicate status every 15 minutes; the status page for customers if impact is external.
3. **Diagnose:** logs, traces, recent changes; involve the owning team; keep a timeline in the channel.
4. **Recover and verify:** SLO back within target, backlog drained, reconciliation run for payments.
5. **Postmortem within days:** blameless, timeline, contributing causes (not one root cause), what went well, action items with owners and dates, published to the organisation.
6. **Follow through:** action items tracked like features; alert tuned; runbook updated; game day if the failure mode was new.

Mention regulatory clocks for finance: major ICT incidents under DORA have reporting deadlines, so the incident process has a compliance hook.

**Example:** postmortem skeleton:

```
Title / Severity / Duration / Customer impact (numbers)
Timeline (UTC): detect, declare, mitigate, resolve
Contributing factors: change X, missing alert Y, assumption Z
What went well / what we were lucky about
Actions: owner, due date, type (prevent / detect / mitigate)
```

> **What to say to the interviewer:** Acknowledge, size the impact from the SLO view, declare and take command, mitigate with the most reversible action, communicate on a cadence, then diagnose and verify recovery including reconciliation. Afterwards a blameless postmortem with contributing factors and owned actions, and I'd flag the DORA reporting clock for a payments incident.

### Q34. Write a script that parses system or application logs and reports recurring error patterns.
Asked at: Booking.com (coding round), Spotify, Hetzner, Scaleway; typical pairing exercise.

> **In simple words:** Read every line, keep only the errors, replace the parts that change (numbers, IDs, timestamps) with placeholders, and count what is left.

Approach: stream the file (don't load it all), filter by level, normalise variable tokens, count with a dictionary, print top N with first and last occurrence. Talk about edge cases: gzip, rotation, multi-line stack traces, time windows.

**Example:**

```python
#!/usr/bin/env python3
import re, sys, gzip, collections
pat = re.compile(r'\b(ERROR|CRIT|FATAL)\b')
norm = [(re.compile(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\S*'), '<ts>'),
        (re.compile(r'\b[0-9a-f]{8}-[0-9a-f-]{27}\b'), '<uuid>'),
        (re.compile(r'\b\d+\.\d+\.\d+\.\d+\b'), '<ip>'),
        (re.compile(r'\b\d+\b'), '<n>')]
def normalise(line):
    for rx, rep in norm: line = rx.sub(rep, line)
    return line.strip()
counts, first, last = collections.Counter(), {}, {}
def opener(p): return gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')
for path in sys.argv[1:]:
    with opener(path) as f:
        for i, line in enumerate(f, 1):
            if not pat.search(line): continue
            key = normalise(line)
            counts[key] += 1; first.setdefault(key, (path, i)); last[key] = (path, i)
for key, n in counts.most_common(20):
    print(f"{n:6d}  first={first[key]}  last={last[key]}\n        {key[:160]}")
```

Run: `./errpatterns.py /var/log/app/*.log /var/log/app/*.gz`. For bash-only interviews: `grep -hE 'ERROR|FATAL' *.log | sed -E 's/[0-9]+/N/g' | sort | uniq -c | sort -rn | head`.

> **What to say to the interviewer:** Stream the files, filter error levels, normalise timestamps, IDs, IPs and numbers to placeholders so variants collapse into one pattern, count them and print the top entries with first and last occurrence. I'd mention rotation, gzip and multi-line traces as the next things to handle.

### Q35. Given CPU, memory and request metrics for a fleet, write a program that picks which nodes to decommission.
Asked at: Booking.com (coding round), OVHcloud, Hetzner, Deutsche Telekom.

> **In simple words:** Keep enough capacity for the busiest hour plus a safety margin, then retire the emptiest, oldest machines first, never two from the same rack or zone at once.

Approach:

1. Compute required capacity: p95 of total CPU and memory over the last 2 weeks times a headroom factor (1.3), plus N+1 per zone.
2. Score nodes: low utilisation, old hardware generation, high failure rate, lower cost efficiency.
3. Greedy removal: sort by score, remove while the remaining capacity per zone still satisfies the requirement and anti-affinity constraints (no two in the same rack in one batch).
4. Output a batch plan with reasons; dry-run by default.

**Example:**

```python
def plan(nodes, p95_cpu, p95_mem, headroom=1.3, per_zone_min=2):
    need_cpu, need_mem = p95_cpu * headroom, p95_mem * headroom
    keep = {n.id for n in nodes}
    cap = lambda: (sum(n.cpu for n in nodes if n.id in keep), sum(n.mem for n in nodes if n.id in keep))
    zone_count = lambda z: sum(1 for n in nodes if n.id in keep and n.zone == z)
    score = lambda n: (n.util_cpu + n.util_mem) / 2 - 0.1 * n.age_years + 0.2 * n.fail_rate
    removed = []
    for n in sorted(nodes, key=score):
        if zone_count(n.zone) <= per_zone_min: continue
        keep.discard(n.id)
        c, m = cap()
        if c < need_cpu or m < need_mem: keep.add(n.id); break
        removed.append((n.id, f"util={n.util_cpu:.0%}/{n.util_mem:.0%} age={n.age_years}y zone={n.zone}"))
    return removed
```

> **What to say to the interviewer:** Derive the capacity you must keep from p95 usage with headroom and per-zone minimums, score nodes on utilisation, age and reliability, then greedily remove the lowest-scored ones while the constraints still hold, printing a dry-run plan with reasons. I'd drain in small batches and re-check metrics between batches.

### Q36. Management wants to move from AWS to Hetzner or an on-prem data centre for cost and sovereignty. Make a plan and name the risks.
Asked at: German and French scale-ups, public-sector suppliers, Italian SMEs after 2023 price increases.

> **In simple words:** Moving house: pack the furniture that moves easily (stateless apps), hire specialists for the piano (databases), keep the old house until the new one is proven, and budget for things AWS did for you invisibly.

Plan:

1. **Inventory and classify:** services, data stores, managed dependencies (RDS, SQS, S3, IAM, KMS), egress volumes, compliance scope.
2. **Target platform:** Kubernetes on Hetzner (Talos/kubeadm/Cluster API or managed Kapsule on Scaleway), load balancers, Ceph/Longhorn or provider block storage, S3-compatible object storage (Hetzner Object Storage, MinIO), Postgres via operator (CloudNativePG) or a managed EU provider (Aiven), Kafka via Strimzi, Vault, Keycloak for identity.
3. **Replace managed services:** map each AWS service to a replacement and an owner; some stay on AWS temporarily (Route 53, SES).
4. **Migrate stateless first,** then data with replication and a cutover window; dual-run with traffic shifting at DNS/CDN level.
5. **Operations gap:** backups, patching, monitoring, DR and on-call now fully yours; cost that in people, not only servers.
6. **Risks:** underestimated ops load, data migration cutover, hidden AWS dependencies (IAM, KMS), capacity planning without autoscaling elasticity, hardware lead times, single-provider concentration again.
7. **Prove it:** run the new platform for a release cycle under production load before decommissioning.

**Example:** service mapping table:

```
RDS Postgres -> CloudNativePG on k8s with PITR to Hetzner Object Storage
SQS          -> NATS JetStream / RabbitMQ (Strimzi Kafka if volume justifies)
S3           -> Hetzner Object Storage (S3 API), MinIO for on-prem
IAM/Secrets  -> Keycloak + Vault
CloudWatch   -> Prometheus/Loki/Grafana
ALB          -> Hetzner LB + ingress-nginx; Cloudflare in front
```

> **What to say to the interviewer:** Inventory and map every managed dependency to a replacement with an owner, build the Kubernetes platform on the target with storage, Postgres operator, object storage and identity, move stateless services first and data with replication and a dual-run cutover, and keep AWS alive until a full release cycle has run on the new side. The biggest risk is the operational load that AWS absorbed, so I'd budget people before servers.

### Q37. Tell us about a time you disagreed with developers about reliability versus shipping features. What did you do?
Asked at: Booking.com (explicit), Spotify, Zalando, Klarna, Monzo behavioural round.

> **In simple words:** They want to see that you neither cave nor block: you turn an argument about opinions into a decision about data and shared risk.

STAR shape:

- **Situation:** a product team wanted to ship a release while the service was burning error budget / had no rollback / during a freeze.
- **Task:** keep the SLO and keep the relationship.
- **Action:** quantify the risk (budget left, blast radius), propose a smaller safe path (feature flag, canary, ship behind a flag, delay by a day), bring the trade-off to the product owner with numbers, and agree who decides. Document the decision.
- **Result:** what shipped, what the impact was, and what changed structurally (error-budget policy, canary by default) so the argument does not recur.

Avoid: "I escalated and won", "I just said no", blaming developers. European teams value consensus with clear ownership.

**Example:** two-line result that lands well:

```
We shipped two days later behind a flag with a canary; no incident. We then wrote an error-budget policy with product so the next time the budget, not the loudest person, decides.
```

> **What to say to the interviewer:** I turn it into a shared risk decision: show the error budget and blast radius, offer a safer way to still ship, let the product owner decide with the numbers, and then fix the process so it is a policy next time. In the case I'd describe, we shipped slightly later behind a flag and agreed an error-budget policy together.

### Q38. You work in a multinational team across three time zones and two languages. How do you communicate during an incident and in a postmortem?
Asked at: Adyen (explicit: explanation over tool name-dropping), Booking.com, Spotify, SAP, Zalando.

> **In simple words:** Say less, write more, and say it so a tired colleague in another country understands it on the first read.

- **During the incident:** one channel, one incident commander, written updates on a fixed cadence (what we know, what we are doing, next update time), plain language, no acronyms without expansion, UTC timestamps, a shared timeline doc.
- **Hand-offs across time zones:** written summary at the end of each shift with current hypothesis, actions in flight and what the next person should not redo.
- **Postmortem:** written first, meeting second; neutral language ("the deploy at 02:14 introduced", not "X broke it"); contributing factors; explicit decisions; translated glossary if needed; actions with owners.
- **Culture notes:** blameless means describing systems and decisions, not people; in European teams direct feedback is normal but personal blame is not; ask quiet participants explicitly.
- **Language:** English is the working language almost everywhere; mention the local language if you have it (German, Italian, French, Dutch) because stakeholders and auditors often prefer it.

**Example:** incident update template:

```
[14:30 UTC] Status: mitigating. Impact: ~8% of card payments failing since 14:05. 
Cause (suspected): new acquirer rate limit. Action: rerouting to backup acquirer, ETA 10 min.
Next update: 14:45 UTC. IC: Amin. Scribe: Lea.
```

> **What to say to the interviewer:** One channel, one commander, written updates every 15 minutes in plain English with UTC times, a shift hand-off note across time zones, and a postmortem written in neutral, system-focused language before anyone meets. I also keep a glossary so new or non-native colleagues can follow, and I'd add Italian for local stakeholders.
