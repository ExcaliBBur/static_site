"""Статус последних запусков GitHub Actions (публичный API, без токена)."""
import json
import sys
import urllib.request

repo = sys.argv[1] if len(sys.argv) > 1 else "ExcaliBBur/static_site"
with urllib.request.urlopen(f"https://api.github.com/repos/{repo}/actions/runs?per_page=8") as r:
    data = json.load(r)
for run in data["workflow_runs"]:
    print(run["id"], run["name"], run["event"], run["head_sha"][:7], run["status"],
          run["conclusion"], run["run_started_at"], run["updated_at"])
