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

# # Compare NVDA vs TSLA over 1 year
# compare_stocks("NVDA", "TSLA", "1y")
