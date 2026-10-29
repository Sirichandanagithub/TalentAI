
"""
GitHub repository verification service.

Fetches public repository metadata and README evidence.
Never executes repository code or awards ATS points by itself.
"""

import re
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import httpx


class GitHubVerificationService:
    """Read-only verification of public GitHub repositories."""

    API_BASE = "https://api.github.com"
    TIMEOUT_SECONDS = 5.0
    MAX_README_CHARS = 12000

    def __init__(self, timeout: float = TIMEOUT_SECONDS) -> None:
        self.timeout = timeout

    @staticmethod
    def _parse_repo_url(url: str) -> Optional[Tuple[str, str]]:
        if not isinstance(url, str):
            return None

        try:
            parsed = urlparse(url.strip())
            port = parsed.port
        except ValueError:
            return None

        if (
            parsed.scheme != "https"
            or parsed.hostname not in {"github.com", "www.github.com"}
            or port not in (None, 443)
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            return None

        parts = [part for part in parsed.path.strip("/").split("/") if part]

        if len(parts) != 2:
            return None

        owner, repo = parts

        if not re.fullmatch(r"[A-Za-z0-9-]+", owner):
            return None

        if not re.fullmatch(r"[A-Za-z0-9_.-]+", repo):
            return None

        if repo.lower().endswith(".git"):
            repo = repo[:-4]

        if not repo or repo in {".", ".."}:
            return None

        return owner, repo

    def verify_repository(self, github_url: str) -> Dict[str, Any]:
        """Return repository evidence without assigning an ATS score."""

        parsed_repo = self._parse_repo_url(github_url)

        if not parsed_repo:
            return {
                "verification_status": "invalid_url",
                "repository_verified": False,
                "github_url": github_url if isinstance(github_url, str) else "",
                "evidence": [],
            }

        owner, repo = parsed_repo
        api_url = f"{self.API_BASE}/repos/{owner}/{repo}"

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "TalentAI-Repository-Verifier",
        }

        try:
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=False,
            ) as client:
                response = client.get(api_url, headers=headers)

                if response.status_code == 404:
                    return {
                        "verification_status": "not_found_or_private",
                        "repository_verified": False,
                        "github_url": github_url,
                        "evidence": [],
                    }

                if response.status_code in (403, 429):
                    return {
                        "verification_status": "rate_limited_or_forbidden",
                        "repository_verified": False,
                        "github_url": github_url,
                        "evidence": [],
                    }

                response.raise_for_status()
                metadata = response.json()

                if not isinstance(metadata, dict):
                    raise ValueError("Unexpected GitHub API response")

                if metadata.get("private") is True:
                    return {
                        "verification_status": "private",
                        "repository_verified": False,
                        "github_url": github_url,
                        "evidence": [],
                    }

                result: Dict[str, Any] = {
                    "verification_status": "verified",
                    "repository_verified": True,
                    "github_url": metadata.get("html_url", github_url),
                    "repository_name": metadata.get("full_name", ""),
                    "description": metadata.get("description") or "",
                    "language": metadata.get("language"),
                    "topics": metadata.get("topics", []),
                    "stars": metadata.get("stargazers_count", 0),
                    "evidence": [],
                }

                result["evidence"].append({
                    "source": "github_repository_metadata",
                    "description": result["description"],
                    "language": result["language"],
                    "topics": result["topics"],
                })

                # README retrieval is best-effort.
                try:
                    readme_response = client.get(
                        f"{api_url}/readme",
                        headers={
                            **headers,
                            "Accept": "application/vnd.github.raw+json",
                        },
                    )

                    if readme_response.status_code == 200:
                        readme_text = readme_response.text[
                            :self.MAX_README_CHARS
                        ]

                        result["readme_available"] = True
                        result["readme_excerpt"] = readme_text
                        result["evidence"].append({
                            "source": "github_readme",
                            "text": readme_text,
                        })
                    else:
                        result["readme_available"] = False

                except (httpx.HTTPError, ValueError):
                    result["readme_available"] = False

                return result

        except httpx.TimeoutException:
            return {
                "verification_status": "timeout",
                "repository_verified": False,
                "github_url": github_url,
                "evidence": [],
            }

        except (httpx.HTTPError, ValueError):
            return {
                "verification_status": "unavailable",
                "repository_verified": False,
                "github_url": github_url,
                "evidence": [],
            }
    
    
    def compare_required_skills(
        self,
        verification: Dict[str, Any],
        required_skills: list[str],
    ) -> Dict[str, Any]:
        """Compare job skills with repository text evidence."""

        if verification.get("verification_status") != "verified":
            return {
                "comparison_status": "insufficient_evidence",
                "skills": [
                    {
                        "skill": skill,
                        "status": "insufficient_evidence",
                        "evidence_sources": [],
                    }
                    for skill in required_skills
                    if isinstance(skill, str) and skill.strip()
                ],
            }

        sources = {
            "repository_description": verification.get("description", ""),
            "repository_language": verification.get("language") or "",
            "repository_topics": " ".join(
                str(topic) for topic in verification.get("topics", [])
            ),
            "readme": verification.get("readme_excerpt", ""),
        }

        normalized_sources = {
            name: value.lower()
            for name, value in sources.items()
            if isinstance(value, str) and value.strip()
        }

        results = []

        negative_patterns = [
            r"\bnot\s+(?:used|using|implemented|supported|required|discussed)\b",
            r"\bdoes\s+not\s+(?:use|implement|support|require)\b",
            r"\bnever\s+(?:uses|used|implements|implemented)\b",
            r"\bwithout\s+(?:using|supporting|implementing)\b",
            r"\bnot\s+currently\s+(?:used|supported|implemented)\b",
        ]

        for skill in required_skills:
            if not isinstance(skill, str) or not skill.strip():
                continue

            skill = skill.strip()
            skill_pattern = (
                r"(?<![a-z0-9])"
                + re.escape(skill.lower())
                + r"(?![a-z0-9])"
            )

            positive_sources = []
            negative_sources = []

            for source_name, source_text in normalized_sources.items():
                for match in re.finditer(skill_pattern, source_text):
                    # Inspect a small context around each mention.
                    start = max(0, match.start() - 80)
                    end = min(len(source_text), match.end() + 100)
                    context = source_text[start:end]

                    if any(
                        re.search(pattern, context)
                        for pattern in negative_patterns
                    ):
                        negative_sources.append(source_name)
                    else:
                        positive_sources.append(source_name)

            if positive_sources:
                status = "mentioned"
                evidence_sources = sorted(set(positive_sources))
            elif negative_sources:
                status = "mentioned_in_negative_context"
                evidence_sources = sorted(set(negative_sources))
            else:
                status = "not_found_in_scanned_evidence"
                evidence_sources = []

            results.append({
                "skill": skill,
                "status": status,
                "evidence_sources": evidence_sources,
            })

        return {
            "comparison_status": (
                "completed" if normalized_sources
                else "insufficient_evidence"
            ),
            "skills": results,
        }
