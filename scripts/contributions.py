"""Update the contributions section of README.md from the GitHub GraphQL API."""
import datetime as dt
import json
import os
import re
import urllib.request

USER = os.environ.get("GH_USER", "ctpnheee")
TOKEN = os.environ["GITHUB_TOKEN"]


def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}"},
    )
    with urllib.request.urlopen(req) as r:
        body = json.load(r)
    if "errors" in body:
        raise RuntimeError(body["errors"])
    return body["data"]


Q = """query($u:String!,$f:DateTime,$t:DateTime){user(login:$u){createdAt
contributionsCollection(from:$f,to:$t){
 totalCommitContributions totalPullRequestContributions totalIssueContributions
 totalPullRequestReviewContributions restrictedContributionsCount
 contributionCalendar{totalContributions}
 commitContributionsByRepository(maxRepositories:50){repository{nameWithOwner url isPrivate} contributions{totalCount}}
 pullRequestContributionsByRepository(maxRepositories:50){repository{nameWithOwner url isPrivate} contributions{totalCount}}
}}}"""

created = dt.datetime.fromisoformat(gql(Q, u=USER)["user"]["createdAt"].replace("Z", "+00:00"))
now = dt.datetime.now(dt.timezone.utc)

years, repos = [], {}
for y in range(created.year, now.year + 1):
    f = max(created, dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc))
    t = min(now, dt.datetime(y, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
    c = gql(Q, u=USER, f=f.isoformat(), t=t.isoformat())["user"]["contributionsCollection"]
    years.append((y, c))
    for kind, key in (("commits", "commitContributionsByRepository"), ("prs", "pullRequestContributionsByRepository")):
        for item in c[key]:
            r = item["repository"]
            if r["isPrivate"]:
                continue
            e = repos.setdefault(r["nameWithOwner"], {"url": r["url"], "commits": 0, "prs": 0})
            e[kind] += item["contributions"]["totalCount"]

tot = lambda k: sum(c[k] for _, c in years)
all_contrib = sum(c["contributionCalendar"]["totalContributions"] for _, c in years)
badge = lambda label, value, color: (
    f'<img src="https://img.shields.io/badge/{label.replace(" ", "%20")}-{value}-{color}?style=for-the-badge" />'
)

lines = ['<p align="center">',
         badge("Contributions", all_contrib, "a18cd1"),
         badge("Commits", tot("totalCommitContributions"), "fbc2eb"),
         badge("Pull requests", tot("totalPullRequestContributions"), "f78fb3"),
         badge("Issues", tot("totalIssueContributions"), "c39bd3"),
         "</p>"]

path = "README.md"
s = open(path, encoding="utf-8").read()
s = re.sub(r"(<!-- CONTRIBUTIONS:START -->).*?(<!-- CONTRIBUTIONS:END -->)",
           lambda m: m.group(1) + "\n" + "\n".join(lines) + "\n" + m.group(2), s, flags=re.S)
open(path, "w", encoding="utf-8").write(s)
