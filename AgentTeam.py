class AgentTeam:
    """Manages multiple agents for financial analysis and web research."""
    
    def __init__(self):
        self.web_agent = WebAgent()
        self.finance_agent = FinanceAgent()
    
    def research_nvda(self):
        print("🔍 Researching NVDA...\n")

        # Fetch stock performance
        stock_performance = self.finance_agent.get_stock_performance("NVDA")
        print("📈 Stock Performance:")
        print(pd.DataFrame([stock_performance]))

        # Fetch analyst recommendations
        print("\n💡 Analyst Recommendations:")
        print(self.finance_agent.get_analyst_recommendations("NVDA"))

        # Fetch news results
        print("\n📰 Latest News:")
        news_results = self.web_agent.search_news("Nvidia stock increase last year")
        for title, link in news_results:
            print(f"- {title} ({link})")

# Instantiate and run
agent_team = AgentTeam()
agent_team.research_nvda()
