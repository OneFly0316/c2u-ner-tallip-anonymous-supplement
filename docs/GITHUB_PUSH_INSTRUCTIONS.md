# GitHub Push Instructions

The current machine does not have GitHub CLI installed at the time this file was created. After installing `gh`, run:

```bash
gh auth login
```

Choose:

```text
GitHub.com
HTTPS
Login with a web browser
```

Then push the anonymous supplement:

```bash
cd /home/ubuntu/GYF/LLM_NER/submission/C2U_NER_TALLIP_anon_supplement
bash scripts/create_github_repo.sh
```

Suggested repository name:

```text
c2u-ner-tallip-anonymous-supplement
```

Use a private repository during drafting if author anonymity or source-data licensing is not fully settled. Use a public anonymous repository only when the package has been checked for author-identifying metadata and restricted text.

