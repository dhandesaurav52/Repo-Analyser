from datetime import datetime, timezone


def humanize_days(date_str: str):
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - dt).days
    if days == 0:
        return "today"
    if days == 1:
        return "1 day ago"
    return f"{days} days ago"


def build_tree(paths):
    root = {}
    for item in paths:
        parts = item["path"].split("/")
        node = root
        for idx, part in enumerate(parts):
            node.setdefault(part, {"type": "tree" if idx < len(parts) - 1 else item["type"], "children": {}})
            node = node[part]["children"]
    return root


def analyze_repository(repo, languages, tree, commits):
    total = sum(languages.values()) or 1
    language_percentages = {k: round(v * 100 / total, 2) for k, v in languages.items()}
    primary_language = max(language_percentages, key=language_percentages.get) if language_percentages else "Unknown"

    files = [i["path"] for i in tree]
    root_files = [f for f in files if "/" not in f]
    workflows = [f for f in files if f.startswith('.github/workflows/')]

    stack = []
    if 'package.json' in root_files:
        stack.append('Node.js')
    if 'requirements.txt' in root_files:
        stack.append('Python')
    if 'pom.xml' in root_files:
        stack.append('Java (Maven)')
    if 'build.gradle' in root_files:
        stack.append('Java (Gradle)')
    if 'Gemfile' in root_files:
        stack.append('Ruby')
    if 'go.mod' in root_files:
        stack.append('Go')

    cicd = []
    if workflows:
        cicd.append('GitHub Actions')
    if 'Jenkinsfile' in root_files:
        cicd.append('Jenkins')
    if '.gitlab-ci.yml' in root_files:
        cicd.append('GitLab CI/CD')
    if 'azure-pipelines.yml' in root_files:
        cicd.append('Azure DevOps')

    uses_k8s = any('k8s' in f.lower() or 'helm' in f.lower() for f in files)
    uses_tf = any(f.endswith('.tf') for f in files)

    last_commit = commits[0] if commits else {}
    last_date = last_commit.get('commit', {}).get('author', {}).get('date', repo['updated_at'])

    return {
        "metadata": {
            "repository_name": repo["name"],
            "owner_name": repo["owner"]["login"],
            "owner_profile": repo["owner"]["html_url"],
            "description": repo.get("description"),
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "open_issues": repo["open_issues_count"],
            "size_kb": repo["size"],
            "default_branch": repo["default_branch"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"],
            "updated_human": humanize_days(repo["updated_at"]),
            "last_updated_by": last_commit.get('author', {}).get('login', 'Unknown'),
        },
        "languages": {
            "primary": primary_language,
            "breakdown": language_percentages,
        },
        "repository_structure": {
            "tree": build_tree(tree),
            "important_files": [f for f in ["README.md", "package.json", "requirements.txt", "Dockerfile", ".gitignore"] if f in root_files],
        },
        "backend_detection": stack,
        "cicd": {
            "tools": cicd,
            "workflow_count": len(workflows),
            "workflow_names": [w.split('/')[-1] for w in workflows],
        },
        "devops": {
            "uses_docker": "Dockerfile" in root_files,
            "uses_docker_compose": any(f in root_files for f in ["docker-compose.yml", "docker-compose.yaml"]),
            "uses_kubernetes": uses_k8s,
            "uses_terraform": uses_tf,
        },
        "activity": {
            "last_commit_message": last_commit.get('commit', {}).get('message', 'N/A'),
            "last_commit_author": last_commit.get('commit', {}).get('author', {}).get('name', 'N/A'),
            "last_commit_date": last_date,
            "status": "Active" if (datetime.now(timezone.utc) - datetime.fromisoformat(last_date.replace("Z", "+00:00"))).days <= 30 else "Inactive",
        },
    }
