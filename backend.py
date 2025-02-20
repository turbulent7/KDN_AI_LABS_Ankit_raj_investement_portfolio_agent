from flask import Flask, request, jsonify
import yfinance as yf
import requests
import os

app = Flask(__name__)

# SerpAPI credentials
SERPAPI_KEY = os.getenv("SERP_API_KEY")
SERPAPI_URL = "https://serpapi.com/search"


def get_stock_performance(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    if hist.empty:
        return {"error": f"No data found for {ticker}"}

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
        return [{"title": news["title"], "link": news["link"]} for news in results]
    
    return {"error": "Search failed."}


@app.route("/stock", methods=["GET"])
def stock():
    ticker = request.args.get("ticker")
    if not ticker:
        return jsonify({"error": "Ticker is required"}), 400
    return jsonify(get_stock_performance(ticker))


@app.route("/news", methods=["GET"])
def news():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query is required"}), 400
    return jsonify(search_news(query))


if __name__ == "__main__":
    app.run(debug=True)
