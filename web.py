# import yfinance as yf
# import pandas as pd
# from app import get_stock_performance, search_news

# # Define portfolio details
# portfolio = {
#     "AAPL": 100,  # Apple Inc.
#     "MSFT": 50,   # Microsoft Corp.
#     "GOOGL": 30,  # Alphabet Inc.
#     "AMZN": 20    # Amazon.com Inc.
# }

# def analyze_portfolio(portfolio, risk_tolerance="moderate", exit_period=5):
#     """Analyze the given portfolio for performance, diversification, and recommendations."""
    
#     print("\n📊 **Portfolio Analysis** 📊\n")
    
#     # Step 1: Fetch stock performance
#     stock_data = []
#     for stock, shares in portfolio.items():
#         perf = get_stock_performance(stock)  # Calls your existing function
#         perf["Shares Held"] = shares
#         stock_data.append(perf)

#     print("🔹 **Recent Performance of Stocks**")
#     print(pd.DataFrame(stock_data))

#     # Step 2: Diversification Analysis
#     sectors = {  
#         "AAPL": "Technology",
#         "MSFT": "Technology",
#         "GOOGL": "Technology",
#         "AMZN": "Consumer Discretionary"
#     }
    
#     sector_counts = pd.Series([sectors[s] for s in portfolio.keys()]).value_counts()
    
#     print("\n🔹 **Diversification Analysis:**")
#     print(sector_counts)

#     if sector_counts["Technology"] > 2:
#         print("⚠️ High concentration in Technology. Consider diversifying.")

#     # Step 3: Recommendations
#     recommendations = []
#     if risk_tolerance == "moderate":
#         recommendations.append("📌 Reduce exposure to high-volatility tech stocks.")
#         recommendations.append("📌 Consider adding defensive sectors like healthcare or utilities.")
#     if exit_period <= 5:
#         recommendations.append("📌 Invest in stable dividend-paying stocks to preserve capital.")
    
#     print("\n🔹 **Portfolio Recommendations:**")
#     for rec in recommendations:
#         print(rec)

#     # Step 4: Market Trends
#     print("\n🔹 **Market Trends Impacting Portfolio:**")
#     news_results = search_news("Technology stocks market trends")
#     for title, link in news_results:
#         print(f"- {title} ({link})")

# # Run Portfolio Analysis
# analyze_portfolio(portfolio, risk_tolerance="moderate", exit_period=5)

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from app import get_stock_performance, search_news

st.title("📊 Stock Portfolio Dashboard")

# User input for portfolio
st.subheader("Enter Your Portfolio")
portfolio = {}
num_stocks = st.number_input("How many stocks do you want to add?", min_value=1, max_value=10, value=4)
for i in range(num_stocks):
    stock = st.text_input(f"Stock Symbol {i+1}", "AAPL", key=f"stock_{i}").upper()
    shares = st.number_input(f"Shares of {stock}", min_value=1, value=10, key=f"shares_{i}")
    portfolio[stock] = shares

# User inputs for risk tolerance and exit period
risk_tolerance = st.selectbox("Select Risk Tolerance", ["Low", "Moderate", "High"], index=1)
exit_period = st.slider("Select Exit Period (Years)", 1, 10, 5)

# Analyze Portfolio
def analyze_portfolio(portfolio, risk_tolerance, exit_period):
    stock_data = []
    for stock, shares in portfolio.items():
        perf = get_stock_performance(stock)
        perf["Shares Held"] = shares
        stock_data.append(perf)
    
    df = pd.DataFrame(stock_data)
    st.subheader("🔹 Recent Stock Performance")
    st.dataframe(df)

    # Diversification Analysis
    sectors = {"AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology", "AMZN": "Consumer Discretionary"}
    sector_counts = pd.Series([sectors.get(s, "Unknown") for s in portfolio.keys()]).value_counts()
    st.subheader("🔹 Diversification Analysis")
    fig = px.pie(sector_counts, names=sector_counts.index, values=sector_counts.values, title="Portfolio Sector Distribution")
    st.plotly_chart(fig)
    
    if sector_counts.get("Technology", 0) > 2:
        st.warning("⚠️ High concentration in Technology. Consider diversifying.")

    # Recommendations
    recommendations = []
    if risk_tolerance == "Moderate":
        recommendations.append("📌 Reduce exposure to high-volatility tech stocks.")
        recommendations.append("📌 Consider adding defensive sectors like healthcare or utilities.")
    if exit_period <= 5:
        recommendations.append("📌 Invest in stable dividend-paying stocks to preserve capital.")
    
    st.subheader("🔹 Portfolio Recommendations")
    for rec in recommendations:
        st.write(rec)
    
    # Market Trends
    st.subheader("🔹 Market Trends Impacting Portfolio")
    news_results = search_news("Technology stocks market trends")
    for title, link in news_results:
        st.markdown(f"- [{title}]({link})")

# Run Analysis
if st.button("Analyze Portfolio"):
    analyze_portfolio(portfolio, risk_tolerance, exit_period)


