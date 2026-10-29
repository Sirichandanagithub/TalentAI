
"""
GitHub repository discovery for TalentAI.

Searches public GitHub repositories using project details and ranks
potential matches. Ranking does not prove repository ownership.
"""

import re
from typing import Any, Dict, List, Set
from urllib.parse import quote

import httpx


class GitHubRepositoryDiscoveryService:
    """Discover and rank possible public GitHub repositories for a project."""

    API_BASE = "https://api.github.com"
    TIMEOUT_SECONDS = 8.0
    MAX_RESULTS = 10
    MAX_README_CHARS = 12000

    def __init__(self, timeout: float = TIMEOUT_SECONDS) -> None:
        self.timeout = timeout

    @staticmethod
    def _normalize(value: Any) -> str:
        """Normalize text for consistent comparisons."""
        if not isinstance(value, str):
            return ""
        return re.sub(r"[^a-z0-9+#.]+", " ", value.lower()).strip()

    @staticmethod
    def _tokens(value: str) -> Set[str]:
        """Return meaningful tokens from normalized text."""
        return {
            token
            for token in value.split()
            if len(token) > 1
        }

    @staticmethod
    def _safe_list(value: Any) -> List[str]:
        """Return only non-empty strings from a list."""
        if not isinstance(value, list):
            return []

        return [
            item.strip()
            for item in value
            if isinstance(item, str) and item.strip()
        ]

    @staticmethod
    def _unavailable(reason: str) -> Dict[str, Any]:
        """Build a consistent response when discovery cannot run."""
        return {
            "discovery_status": "unavailable",
            "reason": reason,
            "candidate_count": 0,
            "relevance_assessment": "unavailable",
            "score_gap": None,
            "relevance_reason": (
                "Relevance could not be assessed because discovery "
                "did not complete."
            ),
            "search_query": "",
            "selection_policy": (
                "Candidates are ranked only. The highest-ranked result "
                "is not automatically accepted as the candidate's repository. "
                "Ownership is unverified."
            ),
            "candidates": [],
        }

    def _build_search_query(self, project: Dict[str, Any]) -> str:
        """Build a GitHub repository search query from project details."""
        name = project.get("name", "")
        description = project.get("description", "")
        technologies = self._safe_list(project.get("technologies", []))

        search_terms = []

        if isinstance(name, str) and name.strip():
            search_terms.append(name.strip())

        search_terms.extend(technologies[:3])

        if not search_terms and isinstance(description, str):
            description_words = description.split()[:8]
            search_terms.extend(description_words)

        # Remove duplicates while preserving order.
        unique_terms = []
        seen = set()

        for term in search_terms:
            normalized = self._normalize(term)
            if normalized and normalized not in seen:
                unique_terms.append(term)
                seen.add(normalized)

        return " ".join(unique_terms).strip()

    def _fetch_readme_excerpt(
        self,
        client: httpx.Client,
        repository_full_name: str,
        headers: Dict[str, str],
    ) -> str:
        """Fetch a README excerpt while the HTTP client is still open."""
        if not isinstance(repository_full_name, str):
            return ""

        # Prevent unexpected paths from being requested.
        if not re.fullmatch(
            r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+",
            repository_full_name,
        ):
            return ""

        url = (
            f"{self.API_BASE}/repos/"
            f"{repository_full_name}/readme"
        )

        readme_headers = {
            **headers,
            "Accept": "application/vnd.github.raw+json",
        }

        try:
            response = client.get(url, headers=readme_headers)

            if response.status_code != 200:
                return ""

            return response.text[: self.MAX_README_CHARS]

        except (httpx.HTTPError, RuntimeError):
            return ""

    def _rank_repository(
        self,
        project: Dict[str, Any],
        repository: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Rank a repository by project-name, description, technology,
        and README similarity. The score is not an ownership probability.
        """
        project_name = self._normalize(project.get("name", ""))
        project_description = self._normalize(
            project.get("description", "")
        )
        technologies = self._safe_list(
            project.get("technologies", [])
        )

        project_name_tokens = self._tokens(project_name)
        project_description_tokens = self._tokens(project_description)

        project_tech_tokens: Set[str] = set()
        for technology in technologies:
            project_tech_tokens.update(
                self._tokens(self._normalize(technology))
            )

        project_all_tokens = (
            project_name_tokens
            | project_description_tokens
            | project_tech_tokens
        )

        repo_name = self._normalize(repository.get("name", ""))
        repo_description = self._normalize(
            repository.get("description") or ""
        )
        repo_language = self._normalize(
            repository.get("language") or ""
        )

        repo_topics = repository.get("topics", [])
        if not isinstance(repo_topics, list):
            repo_topics = []

        repo_topic_text = " ".join(
            topic for topic in repo_topics if isinstance(topic, str)
        )
        readme_text = self._normalize(
            repository.get("readme_excerpt", "")
        )

        repo_name_tokens = self._tokens(repo_name)
        repo_description_tokens = self._tokens(repo_description)
        repo_tech_tokens = self._tokens(
            f"{repo_language} {repo_topic_text}"
        )
        readme_tokens = self._tokens(readme_text)

        score = 0.0
        reasons = []

        # Repository name: maximum 40 points.
        if project_name and repo_name == project_name:
            score += 40
            reasons.append("Exact project-name match")
        elif project_name_tokens and repo_name_tokens:
            union = project_name_tokens | repo_name_tokens
            overlap = project_name_tokens & repo_name_tokens
            similarity = len(overlap) / len(union) if union else 0.0
            points = 25 * similarity
            score += points

            if points > 0:
                reasons.append(
                    f"Project-name token similarity ({points:.1f}/25)"
                )

        # Repository description: maximum 25 points.
        if project_description_tokens and repo_description_tokens:
            union = (
                project_description_tokens | repo_description_tokens
            )
            overlap = (
                project_description_tokens & repo_description_tokens
            )
            similarity = len(overlap) / len(union) if union else 0.0
            points = 25 * similarity
            score += points

            if points > 0:
                reasons.append(
                    f"Description similarity ({points:.1f}/25)"
                )

        # Technologies compared with repository language and topics:
        # maximum 25 points.
        if project_tech_tokens:
            overlap = project_tech_tokens & repo_tech_tokens
            ratio = len(overlap) / len(project_tech_tokens)
            points = 25 * ratio
            score += points

            if overlap:
                reasons.append(
                    "Technology matches: "
                    + ", ".join(sorted(overlap))
                )

        # README overlap: maximum 10 points.
        if project_all_tokens and readme_tokens:
            overlap = project_all_tokens & readme_tokens
            ratio = len(overlap) / len(project_all_tokens)
            points = 10 * ratio
            score += points

            if overlap:
                reasons.append(
                    f"README text overlap ({points:.1f}/10)"
                )

        score = round(min(score, 100.0), 2)

        return {
            "repository_name": repository.get("full_name", ""),
            "github_url": repository.get("html_url", ""),
            "description": repository.get("description") or "",
            "language": repository.get("language"),
            "topics": repo_topics,
            "stars": repository.get("stargazers_count", 0),
            "ranking_score": score,
            "ranking_reasons": reasons,
            "ownership_verified": False,
        }

    @staticmethod
    def _assess_candidate_relevance(
        candidates: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Assess relevance separately from repository ownership.

        Scores are heuristic similarity scores, not probabilities.
        """
        if not candidates:
            return {
                "relevance_assessment": "no_candidates",
                "score_gap": None,
                "reason": "No repository candidates were found.",
            }

        top_score = float(candidates[0].get("ranking_score", 0.0))

        second_score = (
            float(candidates[1].get("ranking_score", 0.0))
            if len(candidates) > 1
            else None
        )

        score_gap = (
            round(top_score - second_score, 2)
            if second_score is not None
            else None
        )

        # Low scores remain weak even when the top candidate leads.
        if top_score < 45:
            assessment = "weak_relevance"
            reason = "The top repository has insufficient similarity."

        # Similar scores mean there is no clear leading candidate.
        elif score_gap is not None and score_gap < 10:
            assessment = "ambiguous"
            reason = (
                "Multiple repositories have similar ranking scores; "
                "the system cannot confidently distinguish them."
            )

        elif top_score >= 70 and (
            score_gap is None or score_gap >= 15
        ):
            assessment = "strong_relevance"
            reason = (
                "The top repository has strong textual similarity. "
                "This does not establish repository ownership."
            )

        elif top_score >= 45 and (
            score_gap is None or score_gap >= 10
        ):
            assessment = "moderate_relevance"
            reason = (
                "The top repository has moderate textual similarity. "
                "Repository ownership remains unverified."
            )

        else:
            assessment = "ambiguous"
            reason = (
                "The available ranking evidence is insufficient "
                "to distinguish the repository confidently."
            )

        return {
            "relevance_assessment": assessment,
            "score_gap": score_gap,
            "reason": reason,
        }

    def discover_repositories(
        self,
        project: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Search GitHub and return ranked candidates without selecting
        a repository or claiming that it belongs to the candidate.
        """
        if not isinstance(project, dict):
            return self._unavailable("invalid_project_data")

        search_terms = self._build_search_query(project)

        if not search_terms:
            return self._unavailable("insufficient_project_information")

        search_query = quote(search_terms, safe=" ")
        api_url = (
            f"{self.API_BASE}/search/repositories"
            f"?q={search_query}&per_page={self.MAX_RESULTS}"
        )

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "TalentAI-Repository-Discovery",
        }

        try:
            # Keep the client open during both search and README requests.
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=False,
            ) as client:
                response = client.get(api_url, headers=headers)

                if response.status_code in (403, 429):
                    return self._unavailable(
                        "github_rate_limit_or_access_restriction"
                    )

                response.raise_for_status()
                payload = response.json()

                if not isinstance(payload, dict):
                    return self._unavailable(
                        "invalid_github_search_response"
                    )

                items = payload.get("items", [])
                if not isinstance(items, list):
                    items = []

                candidates = []

                for item in items:
                    if not isinstance(item, dict):
                        continue

                    html_url = item.get("html_url")
                    full_name = item.get("full_name")

                    if not isinstance(html_url, str) or not html_url:
                        continue

                    # Only accept results whose URL is on github.com.
                    if not re.fullmatch(
                        r"https://github\.com/"
                        r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+/?",
                        html_url,
                    ):
                        continue

                    if not isinstance(full_name, str):
                        continue

                    # Copy the result so the original response is unchanged.
                    repository = dict(item)

                    repository["readme_excerpt"] = (
                        self._fetch_readme_excerpt(
                            client,
                            full_name,
                            headers,
                        )
                    )

                    candidates.append(
                        self._rank_repository(project, repository)
                    )

                # Sort after processing every search result.
                candidates.sort(
                    key=lambda candidate: candidate["ranking_score"],
                    reverse=True,
                )

                relevance = self._assess_candidate_relevance(
                    candidates
                )

                return {
                    "discovery_status": (
                        "candidates_found"
                        if candidates
                        else "no_candidates_found"
                    ),
                    "reason": (
                        None
                        if candidates
                        else "no_matching_repositories"
                    ),
                    "candidate_count": len(candidates),
                    "relevance_assessment": relevance[
                        "relevance_assessment"
                    ],
                    "score_gap": relevance["score_gap"],
                    "relevance_reason": relevance["reason"],
                    "search_query": search_terms,
                    "selection_policy": (
                        "Candidates are ranked only. The highest-ranked "
                        "result is not automatically accepted as the "
                        "candidate's repository. Ownership is unverified."
                    ),
                    "candidates": candidates,
                }

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (403, 429):
                return self._unavailable(
                    "github_rate_limit_or_access_restriction"
                )
            return self._unavailable("github_search_failed")

        except (httpx.HTTPError, ValueError):
            return self._unavailable("github_search_failed")
