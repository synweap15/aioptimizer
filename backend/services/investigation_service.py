import asyncio
import json
from datetime import datetime
from typing import AsyncIterator, Dict, Any, List
from uuid import uuid4

from agents import Agent, Runner
from serpapi import GoogleSearch

from settings import OPENAI_API_KEY, SERPAPI_API_KEY


class InvestigationService:
    """Service for SEO optimization using OpenAI Agents and SerpAPI"""

    def __init__(self):
        self.openai_api_key = OPENAI_API_KEY
        self.serpapi_key = SERPAPI_API_KEY
        self._setup_agents()

    def _setup_agents(self):
        """Initialize OpenAI agents for SEO optimization"""

        # Define tool functions for agents
        def search_google(query: str, location: str = "United States") -> str:
            """
            Search Google for a query and return results.

            Args:
                query: The search query
                location: Geographic location for search

            Returns:
                JSON string with search results
            """
            params = {
                "q": query,
                "location": location,
                "api_key": self.serpapi_key,
            }
            search = GoogleSearch(params)
            results = search.get_dict()

            # Return top 5 organic results
            organic = results.get("organic_results", [])[:5]
            return json.dumps({
                "query": query,
                "results": [
                    {
                        "title": r.get("title"),
                        "link": r.get("link"),
                        "snippet": r.get("snippet"),
                        "position": r.get("position"),
                    }
                    for r in organic
                ]
            }, indent=2)

        def fetch_url_content(url: str) -> str:
            """
            Fetch and extract main content from a URL.

            Args:
                url: The URL to fetch

            Returns:
                Main text content from the page
            """
            import requests
            from bs4 import BeautifulSoup

            try:
                response = requests.get(url, timeout=10, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; SEOBot/1.0)"
                })
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Get text
                text = soup.get_text()

                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)

                # Extract meta data
                title = soup.find('title')
                meta_desc = soup.find('meta', attrs={'name': 'description'})

                return json.dumps({
                    "url": url,
                    "title": title.string if title else "No title",
                    "meta_description": meta_desc.get('content') if meta_desc else "No description",
                    "content": text[:2000],  # First 2000 chars
                    "content_length": len(text),
                }, indent=2)

            except Exception as e:
                return json.dumps({"error": str(e), "url": url})

        # Agent for web investigation
        self.investigator_agent = Agent(
            name="Web Investigator",
            instructions="""
            You are a web research specialist. Your job is to investigate URLs and gather data.

            Use the available tools to:
            1. Fetch and analyze the target URL's content
            2. Search Google for relevant keywords to understand the competitive landscape
            3. Examine top-ranking competitor pages
            4. Identify content gaps and opportunities

            Provide a comprehensive report of your findings.
            """,
            model="gpt-4o",
            tools=[search_google, fetch_url_content],
        )

        # Agent for analyzing search results
        self.analysis_agent = Agent(
            name="SEO Analyzer",
            instructions="""
            You are an expert SEO analyst. Analyze the investigation report and data
            to identify optimization opportunities. Focus on:
            - Keyword rankings and gaps
            - Competitor content strategies
            - Technical SEO factors (titles, meta descriptions, content quality)
            - Content quality indicators
            - On-page SEO elements

            Provide specific insights based on the data.
            """,
            model="gpt-4o",
        )

        # Agent for generating recommendations
        self.optimization_agent = Agent(
            name="SEO Optimizer",
            instructions="""
            You are an expert SEO strategist. Based on analysis data, provide
            specific, actionable optimization recommendations. Include:
            - On-page SEO improvements (titles, meta descriptions, headings)
            - Content optimization strategies
            - Technical SEO enhancements
            - Link building opportunities
            - Competitive advantages to leverage

            Provide clear, prioritized action items with specific examples.
            """,
            model="gpt-4o",
            handoffs=[self.analysis_agent],  # Can hand off to analyzer if needed
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

    async def investigate(
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

            # Step 3: Web investigation with agent tools
            yield self._format_sse({
                "status": "analyzing",
                "message": "Agent investigating target URL and competitors...",
                "progress": 50,
            })

            investigation_context = f"""
            Target URL: {url}
            Keywords: {', '.join(keywords)}
            Location: {location}

            Please investigate:
            1. Fetch and analyze the content from the target URL
            2. Search Google for each keyword: {', '.join(keywords)}
            3. Fetch content from the top 2-3 competitor URLs
            4. Compare content quality, structure, and SEO elements

            Provide a detailed investigation report.
            """

            investigation_result = await Runner.run(
                agent=self.investigator_agent,
                input=investigation_context,
            )

            # Step 4: Run analysis agent
            yield self._format_sse({
                "status": "analyzing",
                "message": "Running SEO analysis...",
                "progress": 70,
            })

            analysis_context = f"""
            Investigation Report:
            {investigation_result.final_output}

            Current Rankings: {json.dumps(analysis_data['rankings'], indent=2)}
            Top Competitors: {json.dumps(analysis_data['competitors'], indent=2)}

            Analyze this data and provide key SEO insights.
            """

            analysis_result = await Runner.run(
                agent=self.analysis_agent,
                input=analysis_context,
            )

            # Step 5: Generate recommendations
            yield self._format_sse({
                "status": "optimizing",
                "message": "Generating optimization recommendations...",
                "progress": 85,
            })

            optimization_context = f"""
            Investigation findings:
            {investigation_result.final_output}

            Analysis insights:
            {analysis_result.final_output}

            Provide 5-10 specific, actionable SEO recommendations prioritized by impact.
            Format as a numbered list.
            """

            optimization_result = await Runner.run(
                agent=self.optimization_agent,
                input=optimization_context,
            )

            # Step 6: Final results
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
