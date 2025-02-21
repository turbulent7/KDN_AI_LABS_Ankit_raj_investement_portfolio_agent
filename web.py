import yfinance as yf
import pandas as pd
from app import get_stock_performance, search_news

# Define portfolio details
portfolio = {
    "AAPL": 100,  # Apple Inc.
    "MSFT": 50,   # Microsoft Corp.
    "GOOGL": 30,  # Alphabet Inc.
    "AMZN": 20    # Amazon.com Inc.
}

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

# Run Portfolio Analysis
analyze_portfolio(portfolio, risk_tolerance="moderate", exit_period=5)
