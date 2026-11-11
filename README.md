# DevOps Interview Question Bank

![Questions](https://img.shields.io/badge/questions-567-blue)
![Topics](https://img.shields.io/badge/topics-11-green)
![Levels](https://img.shields.io/badge/levels-Basic%20%7C%20Advanced%20%7C%20Scenario-orange)
![License](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey)

**567 real DevOps / SRE / Cloud interview questions** gathered from interview experiences people shared publicly
(TCS, Accenture, PwC, product companies, Google SRE loops and more). They are de-duplicated,
grouped by topic and level, and answered in **plain language first**, then with real depth.

Every answer follows the same four steps:

| | |
| --- | --- |
| **In simple words** | An everyday analogy, so the idea makes sense even if you are new to it |
| **Detailed answer** | The real technical explanation, with a step-by-step triage order for scenario questions |
| **Example** | Working commands, YAML, HCL, Jenkinsfiles or scripts you can run or show |
| **What to say to the interviewer** | A crisp 2-3 line answer to practise out loud |

> Where the "model answers" circulating online were wrong, the corrected version is given
> (for example: removing a resource block in Terraform *destroys* it, KMS stores *keys* not secrets,
> Prometheus collects *metrics* not logs, and VPC endpoints reach AWS services, *not* the internet).

---

## Interactive playbook

The same questions as a filterable, flashcard-style study tool: filter by topic, difficulty and your own progress, full-text search, a drill mode, and progress saved in your browser.

- **Open it:** [`docs/index.html`](docs/index.html) (enable GitHub Pages on the `docs/` folder to get a hosted URL)
- Rebuild the data after editing questions: `python3 tools/build_playbook.py questions docs/bank.json`

## Download

- **Full PDF (all 10 topics):** [`pdf/DevOps_Interview_Question_Bank.pdf`](pdf/DevOps_Interview_Question_Bank.pdf) - 500+ pages with clickable contents and bookmarks
- **One PDF per topic:** [`pdf/by-topic/`](pdf/by-topic/) - handy for revising on your phone

## Topics

| # | Topic | Basic | Advanced | Scenario | Total | Read online | PDF |
| --- | --- | :-: | :-: | :-: | :-: | --- | --- |
| 01 | Linux, Shell Scripting & Networking | 22 | 21 | 43 | **86** | [Read](questions/01-linux-shell-networking.md) | [PDF](pdf/by-topic/01_Linux_Shell_Scripting_Networking.pdf) |
| 02 | Docker & Containers | 17 | 13 | 9 | **39** | [Read](questions/02-docker.md) | [PDF](pdf/by-topic/02_Docker_Containers.pdf) |
| 03 | Kubernetes (incl. EKS / AKS / GKE, Helm, KEDA) | 31 | 30 | 28 | **89** | [Read](questions/03-kubernetes.md) | [PDF](pdf/by-topic/03_Kubernetes.pdf) |
| 04 | CI/CD, Jenkins, Git, GitOps & Ansible | 38 | 23 | 18 | **79** | [Read](questions/04-cicd-jenkins-git-gitops-ansible.md) | [PDF](pdf/by-topic/04_CI_CD_Jenkins_GitOps_Ansible.pdf) |
| 05 | Terraform & Infrastructure as Code | 15 | 20 | 13 | **48** | [Read](questions/05-terraform-iac.md) | [PDF](pdf/by-topic/05_Terraform_Infrastructure_as_Code.pdf) |
| 06 | AWS | 18 | 36 | 27 | **81** | [Read](questions/06-aws.md) | [PDF](pdf/by-topic/06_AWS.pdf) |
| 07 | GCP, Azure & DevSecOps | 12 | 12 | 8 | **32** | [Read](questions/07-gcp-azure-devsecops.md) | [PDF](pdf/by-topic/07_GCP_Azure_DevSecOps.pdf) |
| 08 | Monitoring, Observability, SRE & Scale Design | 9 | 15 | 8 | **32** | [Read](questions/08-monitoring-observability-sre.md) | [PDF](pdf/by-topic/08_Monitoring_Observability_SRE_Scale_Design.pdf) |
| 09 | Behavioral & Project Experience (STAR samples) | 9 | - | 10 | **19** | [Read](questions/09-behavioral.md) | [PDF](pdf/by-topic/09_Behavioral_Project_Experience.pdf) |
| 10 | Shell Scripting: 24 real interview scripts | 7 | 8 | 9 | **24** | [Read](questions/10-shell-scripting.md) | [PDF](pdf/by-topic/10_Shell_Scripting_24_Real_Interview_Scripts.pdf) |
| 11 | Europe: companies, compliance & process (Adyen, Monzo, Booking.com, Zalando, N26, Spotify, Italian/German companies) | 12 | 12 | 14 | **38** | [Read](questions/11-europe.md) | - |
| | **Total** | **190** | **190** | **187** | **567** | | |

## What a question looks like

> **Q. Pods are Running, but users are getting 503 errors. Where do you debug?**
>
> **In simple words:** The shop is open and the staff are at their desks, but the front door
> sign says "closed". Check every step between the customer and the counter.
>
> **Detailed answer:** Follow the request path: DNS -> load balancer -> Ingress controller -> Service ->
> endpoints -> Pod. Empty endpoints (readiness failing or a selector mismatch), unhealthy LB targets,
> Ingress upstream errors, timeouts and HPA at max replicas are the usual culprits...
>
> **What to say to the interviewer:** "I walk the request path hop by hop and check `kubectl get endpoints`
> first. 503 with healthy pods usually means no ready endpoints behind the Service or unhealthy targets
> at the load balancer."

## How to use it

1. **Beginner?** Read only the *In simple words* boxes of the Basic sections first, then go back for the details.
2. **Interview in 1-2 weeks?** Do Basic -> Scenario-Based -> Advanced for your target stack. Most interviews are troubleshooting-heavy.
3. **Practise out loud.** Cover the answer, say yours, then compare with *What to say to the interviewer*.
4. **Run the examples** in a free-tier or local lab (kind/minikube, Docker, a sandbox AWS account). Hands-on answers sound different.

## Scope notes

- Topic 11 covers what European product companies add on top of the fundamentals: interview format (timeboxed take-homes, pairing, design and live-troubleshooting rounds), GDPR, data residency and sovereignty, NIS2/DORA/CRA, EU cloud providers, GitLab CI / GitOps defaults, and payments-grade reliability. Each question lists the companies known to probe it ("Asked at"), based on public interview reports and company guides.

- Only DevOps content: language-specific (Python/PHP) questions and pure network-hardware questions were left out.
- Questions asked in several different wordings are merged into one; the alternatives are listed as *"Also asked as"*.
- Account IDs, ARNs and hostnames in examples are placeholders (`123456789012`, `vpc-0abc...`).

## Contributing

Found a mistake, or have a question from your own interview? Open an issue or a pull request with the
question, the level (Basic / Advanced / Scenario) and, if possible, the company or round type.

## License

Content is licensed under [CC BY 4.0](LICENSE). You are free to share and adapt it with attribution.

---

Made by **Priyanka Gupta** - DevOps Engineer - [LinkedIn](https://www.linkedin.com/in/priyanka-gupta-3b0856153) - [GitHub](https://github.com/priyankagupta7679)

If this helped you prepare, a star on the repo helps others find it.
