import asyncio
import json
from datetime import datetime
from typing import AsyncIterator, Dict, Any, List
from uuid import uuid4

from agents import Agent, Runner
from serpapi import GoogleSearch

from settings import OPENAI_API_KEY, SERPAPI_API_KEY


class OptimizationService:
    """Service for SEO optimization using OpenAI Agents and SerpAPI"""

    def __init__(self):
        self.openai_api_key = OPENAI_API_KEY
        self.serpapi_key = SERPAPI_API_KEY
        self._setup_agents()

    def _setup_agents(self):
        """Initialize OpenAI agents for SEO optimization"""

        # Agent for analyzing search results
        self.analysis_agent = Agent(
            name="SEO Analyzer",
            instructions="""
            You are an expert SEO analyst. Analyze search results and competitor data
            to identify optimization opportunities. Focus on:
            - Keyword rankings and gaps
            - Competitor content strategies
            - Technical SEO factors
            - Content quality indicators
            """,
            model="gpt-4o",
        )

        # Agent for generating recommendations
        self.optimization_agent = Agent(
            name="SEO Optimizer",
            instructions="""
            You are an expert SEO strategist. Based on analysis data, provide
            specific, actionable optimization recommendations. Include:
            - On-page SEO improvements
            - Content optimization strategies
            - Technical SEO enhancements
            - Link building opportunities
            Provide clear, prioritized action items.
            """,
            model="gpt-4o",
        )

    async def search_google(
        self, query: str, location: str, language: str = "en"
    ) -> Dict[str, Any]:
        """Perform Google search via SerpAPI"""
        params = {
            "q": query,
            "location": location,
            "hl": language,
            "gl": language[:2],
            "api_key": self.serpapi_key,
        }

        # Run synchronous SerpAPI call in thread pool
        loop = asyncio.get_event_loop()
        search = await loop.run_in_executor(None, lambda: GoogleSearch(params))
        results = await loop.run_in_executor(None, search.get_dict)

        return results

    async def analyze_rankings(
        self, url: str, keywords: List[str], location: str, language: str = "en"
    ) -> Dict[str, Any]:
        """Analyze current keyword rankings and competitor data"""
        rankings = {}
        all_competitors = set()

        for keyword in keywords:
            # Search for each keyword
            results = await self.search_google(keyword, location, language)

            # Find target URL ranking
            organic_results = results.get("organic_results", [])
            rank = None

            for idx, result in enumerate(organic_results[:20], start=1):
                result_url = result.get("link", "")
                if url.lower() in result_url.lower():
                    rank = idx
                    break

            rankings[keyword] = rank

            # Collect competitor URLs
            for result in organic_results[:5]:
                competitor_url = result.get("link", "")
                if competitor_url and url.lower() not in competitor_url.lower():
                    all_competitors.add(competitor_url)

        return {
            "rankings": rankings,
            "competitors": list(all_competitors)[:10],
            "search_results": results,
        }

    async def optimize(
        self, url: str, keywords: List[str], location: str, language: str = "en"
    ) -> AsyncIterator[str]:
        """
        Run SEO optimization process and stream results via SSE.

        Yields JSON strings formatted for Server-Sent Events.
        """
        task_id = str(uuid4())

        try:
            # Step 1: Initial status
            yield self._format_sse({
                "status": "pending",
                "message": "Starting SEO analysis...",
                "progress": 0,
            })

            await asyncio.sleep(0.5)  # Small delay for UX

            # Step 2: Analyze rankings
            yield self._format_sse({
                "status": "analyzing",
                "message": f"Analyzing rankings for {len(keywords)} keywords...",
                "progress": 20,
            })

            analysis_data = await self.analyze_rankings(url, keywords, location, language)

            yield self._format_sse({
                "status": "analyzing",
                "message": "Rankings analyzed. Processing competitor data...",
                "progress": 40,
                "data": {
                    "rankings": analysis_data["rankings"],
                    "competitors": analysis_data["competitors"],
                },
            })

            # Step 3: Run analysis agent
            yield self._format_sse({
                "status": "analyzing",
                "message": "Running AI analysis...",
                "progress": 60,
            })

            analysis_context = f"""
            Target URL: {url}
            Keywords: {', '.join(keywords)}
            Location: {location}

            Current Rankings: {json.dumps(analysis_data['rankings'], indent=2)}
            Top Competitors: {json.dumps(analysis_data['competitors'], indent=2)}

            Analyze this SEO data and provide key insights.
            """

            analysis_result = await Runner.run(
                agent=self.analysis_agent,
                input=analysis_context,
            )

            # Step 4: Generate recommendations
            yield self._format_sse({
                "status": "optimizing",
                "message": "Generating optimization recommendations...",
                "progress": 80,
            })

            optimization_context = f"""
            Based on this analysis:
            {analysis_result.final_output}

            Provide 5-10 specific, actionable SEO recommendations prioritized by impact.
            Format as a numbered list.
            """

            optimization_result = await Runner.run(
                agent=self.optimization_agent,
                input=optimization_context,
            )

            # Step 5: Final results
            recommendations = self._parse_recommendations(optimization_result.final_output)

            yield self._format_sse({
                "status": "completed",
                "message": "Optimization complete!",
                "progress": 100,
                "data": {
                    "id": task_id,
                    "url": url,
                    "keywords": keywords,
                    "location": location,
                    "current_rankings": analysis_data["rankings"],
                    "competitors": analysis_data["competitors"],
                    "recommendations": recommendations,
                    "analysis": analysis_result.final_output,
                    "created_at": datetime.utcnow().isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                },
            })

        except Exception as e:
            yield self._format_sse({
                "status": "failed",
                "message": f"Optimization failed: {str(e)}",
                "progress": 0,
            })

    def _parse_recommendations(self, text: str) -> List[str]:
        """Parse recommendations from agent output"""
        lines = text.strip().split('\n')
        recommendations = []

        for line in lines:
            line = line.strip()
            # Look for numbered items or bullet points
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove number/bullet and clean up
                cleaned = line.lstrip('0123456789.-•) ').strip()
                if cleaned:
                    recommendations.append(cleaned)

        return recommendations if recommendations else [text]

    def _format_sse(self, data: Dict[str, Any]) -> str:
        """Format data as Server-Sent Event"""
        return f"data: {json.dumps(data)}\n\n"
