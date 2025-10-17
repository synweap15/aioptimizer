from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
from agents import Agent


class PageFetcherService:
    """Service for fetching web page content using an OpenAI Agent"""

    def __init__(self):
        self._setup_agent()

    def _setup_agent(self):
        """Initialize the page fetcher agent with web scraping tool"""

        def fetch_page_content(url: str) -> str:
            """
            Fetch and extract plain text content from a web page.

            Args:
                url: The URL to fetch

            Returns:
                Plain text content from the page
            """
            try:
                response = requests.get(
                    url,
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; AIOBot/1.0)"},
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()

                # Get text
                text = soup.get_text()

                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (
                    phrase.strip() for line in lines for phrase in line.split("  ")
                )
                clean_text = "\n".join(chunk for chunk in chunks if chunk)

                return clean_text

            except Exception as e:
                return f"Error fetching page: {str(e)}"

        # Create agent with page fetching tool
        self.agent = Agent(
            name="Page Fetcher",
            instructions="""
            You are a web page content fetcher. Your job is to retrieve the plain text
            content of web pages using the fetch_page_content tool.

            When given a URL:
            1. Use the fetch_page_content tool to retrieve the page content
            2. Return the plain text content cleanly formatted
            3. If there's an error, report it clearly

            Focus on extracting the main content without navigation, headers, or footers.
            """,
            model="gpt-4o",
            tools=[fetch_page_content],
        )

    async def fetch_page(self, url: str) -> Dict[str, Any]:
        """
        Fetch page content using the agent.

        Args:
            url: The URL to fetch

        Returns:
            Dictionary with url and content
        """
        from agents import Runner

        result = await Runner.run(
            agent=self.agent,
            input=f"Please fetch the content from this URL: {url}",
        )

        return {"url": url, "content": result.final_output, "status": "success"}
