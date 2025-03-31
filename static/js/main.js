function sentimentColor(sentiment) {
    if (sentiment === "Positive") return "green";
    if (sentiment === "Negative") return "red";
    return "gray";
  }
  
  function fetchNews() {
    fetch('/get-news')
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('news-container');
        container.innerHTML = '';
        data.forEach(article => {
          const div = document.createElement('div');
          div.className = 'news-item';
          div.innerHTML = `
            <h3><a href="${article.url}" target="_blank">${article.title}</a></h3>
            <p>${article.description}</p>
            <p><strong>Sentiment:</strong> 
              <span style="color: ${sentimentColor(article.sentiment)};">
                ${article.sentiment}
              </span>
            </p>
          `;
          container.appendChild(div);
        });
      });
  }
  
  function fetchStock() {
    fetch('/get-stock')
      .then(res => res.json())
      .then(data => {
        document.getElementById('stock-price').innerText = data.price;
      });
  }
  
  function renderTrendChart(data) {
    const ctx = document.getElementById('priceSentimentChart').getContext('2d');
  
    const times = data.stock_prices.map(item => item.time);
    const prices = data.stock_prices.map(item => item.price);
  
    const sentimentTimeMap = {};
    data.sentiment_trend.forEach(item => {
      sentimentTimeMap[item.time] = item;
    });
  
    const alignedTimes = times.map(t => t.slice(0, 2) + ":00");
    const pos = alignedTimes.map(t => sentimentTimeMap[t]?.Positive || 0);
    const neu = alignedTimes.map(t => sentimentTimeMap[t]?.Neutral || 0);
    const neg = alignedTimes.map(t => sentimentTimeMap[t]?.Negative || 0);
  
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: times,
        datasets: [
          {
            type: 'line',
            label: 'Stock Price (INR)',
            data: prices,
            borderColor: 'blue',
            backgroundColor: 'transparent',
            yAxisID: 'y',
          },
          {
            label: 'Positive News',
            data: pos,
            backgroundColor: 'green',
            yAxisID: 'y1',
          },
          {
            label: 'Neutral News',
            data: neu,
            backgroundColor: 'gray',
            yAxisID: 'y1',
          },
          {
            label: 'Negative News',
            data: neg,
            backgroundColor: 'red',
            yAxisID: 'y1',
          }
        ]
      },
      options: {
        responsive: true,
        interaction: {
          mode: 'index',
          intersect: false
        },
        scales: {
          y: {
            type: 'linear',
            position: 'left',
            title: { display: true, text: 'Stock Price (INR)' }
          },
          y1: {
            type: 'linear',
            position: 'right',
            title: { display: true, text: 'News Count' },
            grid: { drawOnChartArea: false }
          }
        }
      }
    });
  }
  
  // Initial load
  setInterval(fetchNews, 5 * 60 * 1000);
  setInterval(fetchStock, 5 * 60 * 1000);
  window.onload = function () {
    fetchNews();
    fetchStock();
    fetch('/get-trend-data')
      .then(res => res.json())
      .then(data => renderTrendChart(data));
  };
  