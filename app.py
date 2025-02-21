import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

SERP_API_KEY=os.environ.get('SERP_API_KEY')
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY')

os.environ["SERP_API_KEY"] = SERP_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

import yfinance as yf
from langchain.agents import AgentType, Tool, initialize_agent
from langchain_openai import ChatOpenAI

# Initialize the language model
llm = ChatOpenAI(temperature=0)

# Define the function to get stock price
def get_stock_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return f"The current stock price of {symbol} is ${todays_data['Close'].iloc[-1]:.2f}"

# Create a tool for the agent to use
tools = [
    Tool(
        name="StockPrice",
        func=get_stock_price,
        description="Useful for getting the stock price of a company. The input should be the stock symbol of the company."
    )
]

# Initialize the agent
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# #Example usage
# query = "What's the current stock price of Microsoft?"
# response = agent.invoke(query)
# print(response)
from langchain_core.tools import tool, StructuredTool
from datetime import date

@tool
def get_stock_price(symbol):
    """Use this tool to get the stock price of a company. The input should be the stock symbol of the company."""
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return f"The current stock price of {symbol} is ${todays_data['Close'].iloc[-1]:.2f}"
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain import hub

tools = [get_stock_price]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Try to answer user query using available tools.",
        ),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm = ChatOpenAI(model = "gpt-4o-mini")

finance_agent = create_tool_calling_agent(llm, tools, prompt)

finance_agent_executor = AgentExecutor(agent=finance_agent, tools=tools, verbose=True)

from langchain_core.tools import tool, StructuredTool
from datetime import date

@tool
def company_information(ticker: str) -> dict:
    """Use this tool to retrieve company information like address, industry, sector, company officers, business summary, website,
       marketCap, current price, ebitda, total debt, total revenue, debt-to-equity, etc."""
    
    ticker_obj = yf.Ticker(ticker)
    ticker_info = ticker_obj.get_info()

    return ticker_info

@tool
def last_dividend_and_earnings_date(ticker: str) -> dict:
    """
    Use this tool to retrieve company's last dividend date and earnings release dates.
    It does not provide information about historical dividend yields.
    """
    ticker_obj = yf.Ticker(ticker)
    
    return ticker_obj.get_calendar()

@tool
def summary_of_mutual_fund_holders(ticker: str) -> dict:
    """
    Use this tool to retrieve company's top mutual fund holders. 
    It also returns their percentage of share, stock count and value of holdings.
    """
    ticker_obj = yf.Ticker(ticker)
    mf_holders = ticker_obj.get_mutualfund_holders()
    
    return mf_holders.to_dict(orient="records")

@tool
def summary_of_institutional_holders(ticker: str) -> dict:
    """
    Use this tool to retrieve company's top institutional holders. 
    It also returns their percentage of share, stock count and value of holdings.
    """
    ticker_obj = yf.Ticker(ticker)   
    inst_holders = ticker_obj.get_institutional_holders()
    
    return inst_holders.to_dict(orient="records")

@tool
def stock_grade_updrages_downgrades(ticker: str) -> dict:
    """
    Use this to retrieve grade ratings upgrades and downgrades details of particular stock.
    It'll provide name of firms along with 'To Grade' and 'From Grade' details. Grade date is also provided.
    """
    ticker_obj = yf.Ticker(ticker)
    
    curr_year = date.today().year
    
    upgrades_downgrades = ticker_obj.get_upgrades_downgrades()
    upgrades_downgrades = upgrades_downgrades.loc[upgrades_downgrades.index > f"{curr_year}-01-01"]
    upgrades_downgrades = upgrades_downgrades[upgrades_downgrades["Action"].isin(["up", "down"])]
    
    return upgrades_downgrades.to_dict(orient="records")

@tool
def stock_splits_history(ticker: str) -> dict:
    """
    Use this tool to retrieve company's historical stock splits data.
    """
    ticker_obj = yf.Ticker(ticker)
    hist_splits = ticker_obj.get_splits()
    
    return hist_splits.to_dict()

@tool
def stock_news(ticker: str) -> dict:
    """
    Use this to retrieve latest news articles discussing particular stock ticker.
    """
    ticker_obj = yf.Ticker(ticker)
    
    return ticker_obj.get_news()

tools = [
    company_information,
    last_dividend_and_earnings_date,
    stock_splits_history,
    summary_of_mutual_fund_holders,
    summary_of_institutional_holders, 
    stock_grade_updrages_downgrades,
    stock_news,
    get_stock_price
]


finance_agent = create_tool_calling_agent(llm, tools, prompt)

finance_agent_executor = AgentExecutor(agent=finance_agent, tools=tools, verbose=True)

# #Create a dummy portfolio of 5 stocks
# portfolio = {
#     'AAPL': 50,  # Apple
#     'MSFT': 30,  # Microsoft
#     'GOOGL': 20, # Alphabet (Google)
#     'AMZN': 15,  # Amazon
#     'NVDA': 25   # NVIDIA
# }

# Function to analyze a single stock
def analyze_stock(ticker: str, shares: int):
    response = finance_agent_executor.invoke({
        "messages": [
            HumanMessage(content=f"Provide a brief analysis of {ticker} including current price, P/E ratio, and recent performance.")
        ]
    })
    return f"{ticker} ({shares} shares): {response['output']}"

# Function to analyze the entire portfolio
def analyze_portfolio(portfolio: dict):
    analysis = []
    total_value = 0

    for ticker, shares in portfolio.items():
        stock_analysis = analyze_stock(ticker, shares)
        analysis.append(stock_analysis)

        # Get current price to calculate portfolio value
        price_response = finance_agent_executor.invoke({
            "messages": [
                HumanMessage(content=f"What is the current stock price of {ticker}?")
            ]
        })
        try:
            price = float(price_response['output'].split('$')[1].split()[0])
            total_value += price * shares
        except:
            print(f"Could not parse price for {ticker}")

    return analysis, total_value

# Analyze the portfolio
# print("Analyzing portfolio...")
# stock_analyses, portfolio_value = analyze_portfolio(portfolio)

# # Print the results
# print("\nPortfolio Analysis:")
# for analysis in stock_analyses:
#     print(analysis)
#     print("-" * 50)

import yfinance as yf
import pandas as pd
import requests

# SerpAPI credentials
SERPAPI_KEY = os.getenv("SERP_API_KEY")
SERPAPI_URL = "https://serpapi.com/search"

def get_stock_performance(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    if hist.empty:
        return f"No data found for {ticker}"

    start_price = hist["Close"].iloc[0]
    end_price = hist["Close"].iloc[-1]
    percentage_increase = ((end_price - start_price) / start_price) * 100

    return {
        "Stock": ticker,
        "Start Price (1y ago)": round(start_price, 2),
        "End Price (Now)": round(end_price, 2),
        "Percentage Increase": round(percentage_increase, 2)
    }

def search_news(query):
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google_news",
        "num": 5
    }
    response = requests.get(SERPAPI_URL, params=params)

    if response.status_code == 200:
        results = response.json().get("news_results", [])
        return [(news["title"], news["link"]) for news in results]
    
    return "Search failed."

# Example Usage
# nvidia_performance = get_stock_performance("NVDA")
# news_results = search_news("Nvidia stock increase last year")

# # Display results
# print(pd.DataFrame([nvidia_performance]))
# print("\nRecent News:")
# for title, link in news_results:
#     print(f"- {title} ({link})")

import os
import yfinance as yf
import pandas as pd
import requests

# SerpAPI credentials
SERPAPI_KEY = os.getenv("SERP_API_KEY")
SERPAPI_URL = "https://serpapi.com/search"

class WebAgent:
    """Agent to search the web using SerpAPI."""
    
    def search_news(self, query):
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google_news",
            "num": 5
        }
        response = requests.get(SERPAPI_URL, params=params)

        if response.status_code == 200:
            results = response.json().get("news_results", [])
            return [(news["title"], news["link"]) for news in results]
        
        return "Search failed."

class FinanceAgent:
    """Agent to fetch stock performance and analyst recommendations."""
    
    def get_stock_performance(self, ticker):
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")

        if hist.empty:
            return f"No data found for {ticker}"

        start_price = hist["Close"].iloc[0]
        end_price = hist["Close"].iloc[-1]
        percentage_increase = ((end_price - start_price) / start_price) * 100

        return {
            "Stock": ticker,
            "Start Price (1y ago)": round(start_price, 2),
            "End Price (Now)": round(end_price, 2),
            "Percentage Increase": round(percentage_increase, 2)
        }

    def get_analyst_recommendations(self, ticker):
        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations

        if recommendations is None or recommendations.empty:
            return f"No analyst recommendations found for {ticker}"

        return recommendations.tail(5)  # Get the latest 5 recommendations
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


def compare_stocks(symbol1, symbol2, period='1y'):
    """Compare stock performance and P/E ratio for two stocks."""
    
    print(f"\n🔍 Comparing {symbol1} vs {symbol2} over {period}...\n")
    
    # Fetch stock performance for both symbols
    stock1_performance = agent_team.finance_agent.get_stock_performance(symbol1)
    stock2_performance = agent_team.finance_agent.get_stock_performance(symbol2)

    print("📊 Stock Performance Comparison:")
    print(pd.DataFrame([stock1_performance, stock2_performance]))

    # Fetch P/E ratios
    stock1_info = yf.Ticker(symbol1).info
    stock2_info = yf.Ticker(symbol2).info

    pe_ratio_1 = stock1_info.get("trailingPE", "N/A")
    pe_ratio_2 = stock2_info.get("trailingPE", "N/A")

    print("\n📈 P/E Ratio Analysis:")
    print(pd.DataFrame([
        {"Stock": symbol1, "P/E Ratio": pe_ratio_1},
        {"Stock": symbol2, "P/E Ratio": pe_ratio_2}
    ]))

# Compare NVDA vs TSLA over 1 year
compare_stocks("NVDA", "TSLA", "1y")


import yfinance as yf
import pandas as pd

# # Define portfolio details
# portfolio = {
#     "AAPL": 100,  # Apple Inc.
#     "MSFT": 50,   # Microsoft Corp.
#     "GOOGL": 30,  # Alphabet Inc.
#     "AMZN": 20    # Amazon.com Inc.
# }

def analyze_portfolio(portfolio, risk_tolerance="moderate", exit_period=5):
    """Analyze the given portfolio for performance, diversification, and recommendations."""
    
    print("\n📊 **Portfolio Analysis** 📊\n")
    
    # Step 1: Fetch stock performance
    stock_data = []
    for stock, shares in portfolio.items():
        perf = get_stock_performance(stock)  # Calls your existing function
        perf["Shares Held"] = shares
        stock_data.append(perf)

    print("🔹 **Recent Performance of Stocks**")
    print(pd.DataFrame(stock_data))

    # Step 2: Diversification Analysis
    sectors = {  
        "AAPL": "Technology",
        "MSFT": "Technology",
        "GOOGL": "Technology",
        "AMZN": "Consumer Discretionary"
    }
    
    sector_counts = pd.Series([sectors[s] for s in portfolio.keys()]).value_counts()
    
    print("\n🔹 **Diversification Analysis:**")
    print(sector_counts)

    if sector_counts["Technology"] > 2:
        print("⚠️ High concentration in Technology. Consider diversifying.")

    # Step 3: Recommendations
    recommendations = []
    if risk_tolerance == "moderate":
        recommendations.append("📌 Reduce exposure to high-volatility tech stocks.")
        recommendations.append("📌 Consider adding defensive sectors like healthcare or utilities.")
    if exit_period <= 5:
        recommendations.append("📌 Invest in stable dividend-paying stocks to preserve capital.")
    
    print("\n🔹 **Portfolio Recommendations:**")
    for rec in recommendations:
        print(rec)

    # Step 4: Market Trends
    print("\n🔹 **Market Trends Impacting Portfolio:**")
    news_results = search_news("Technology stocks market trends")
    for title, link in news_results:
        print(f"- {title} ({link})")

# # Run Portfolio Analysis
# analyze_portfolio(portfolio, risk_tolerance="moderate", exit_period=5)

