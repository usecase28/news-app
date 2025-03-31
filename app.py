from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
from collections import defaultdict
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Initialize Flask
app = Flask(__name__)

# Setup VADER
nltk.download('vader_lexicon')
analyzer = SentimentIntensityAnalyzer()

# Scrape ONGC news from Moneycontrol
def fetch_ongc_news():
    url = "https://www.moneycontrol.com/news/tags/ongc.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    news_with_sentiment = []
    articles = soup.find_all('li', class_='clearfix')

    for article in articles:
        title_tag = article.find('h2') or article.find('h3')
        link_tag = article.find('a')
        time_tag = article.find('span', class_='content_subhead')
        
        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            link = link_tag['href']
            published = time_tag.get_text(strip=True) if time_tag else datetime.now().isoformat()

            sentiment_score = analyzer.polarity_scores(title)["compound"]
            if sentiment_score >= 0.05:
                sentiment = "Positive"
            elif sentiment_score <= -0.05:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            news_with_sentiment.append({
                "title": title,
                "description": "",
                "publishedAt": published,
                "url": link,
                "sentiment": sentiment
            })

    return news_with_sentiment

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-stock')
def get_stock():
    ticker = yf.Ticker("ONGC.NS")
    data = ticker.history(period="1d")
    if not data.empty:
        price = round(data["Close"].iloc[-1], 2)
        return jsonify({"price": price})
    return jsonify({"price": "N/A"})

@app.route('/get-news')
def get_news():
    return jsonify(fetch_ongc_news())

@app.route('/get-trend-data')
def get_trend_data():
    ticker = yf.Ticker("ONGC.NS")
    hist = ticker.history(period="1d", interval="60m")
    price_data = hist[['Close']].reset_index()
    price_data['time'] = price_data['Datetime'].dt.strftime('%H:%M')

    stock_prices = [
        {"time": row['time'], "price": round(row['Close'], 2)}
        for _, row in price_data.iterrows()
    ]

    news = fetch_ongc_news()
    sentiment_by_hour = defaultdict(lambda: {"Positive": 0, "Neutral": 0, "Negative": 0})
    for item in news:
        try:
            hour = pd.to_datetime(item['publishedAt']).strftime('%H:00')
            sentiment_by_hour[hour][item['sentiment']] += 1
        except:
            continue

    sentiment_trend = [
        {
            "time": hour,
            "Positive": counts["Positive"],
            "Neutral": counts["Neutral"],
            "Negative": counts["Negative"]
        }
        for hour, counts in sorted(sentiment_by_hour.items())
    ]

    return jsonify({
        "stock_prices": stock_prices,
        "sentiment_trend": sentiment_trend
    })

if __name__ == '__main__':
    app.run(debug=True)
