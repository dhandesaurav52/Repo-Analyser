from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.github_service import GitHubService
from utils.detection_logic import analyze_repository

app = FastAPI(title="RepoInsight API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = GitHubService()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/analyze")
async def analyze(repo_url: str):
    try:
        owner, repo = service.parse_github_url(repo_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        repo_data = await service.get_repo(owner, repo)
        languages = await service.get_languages(owner, repo)
        tree = await service.get_tree(owner, repo, repo_data["default_branch"])
        commits = await service.get_commits(owner, repo)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    return analyze_repository(repo_data, languages, tree, commits)
