import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from ta.trend import SMAIndicator

# Binance API endpoint for fetching klines
BASE_URL = 'https://api.binance.com/api/v3/klines'

# Function to fetch klines data
def get_klines(symbol, interval, limit=1000):
    url = f"{BASE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                                     'Close time', 'Quote asset volume', 'Number of trades', 
                                     'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    df['Close'] = pd.to_numeric(df['Close'])
    df['High'] = pd.to_numeric(df['High'])
    df['Low'] = pd.to_numeric(df['Low'])
    df['Volume'] = pd.to_numeric(df['Volume'])
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    return df[['Open time', 'Close', 'High', 'Low', 'Volume']]

# Plot data with SMAs
def plot_data(df, smas, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Open time'], y=df['Close'], mode='lines', name='Close Price'))

    # Add SMAs
    for period, sma in smas.items():
        fig.add_trace(go.Scatter(x=df['Open time'], y=sma, mode='lines', name=f'{period}-SMA'))

    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Price', template='plotly_dark')
    st.plotly_chart(fig)

# Main function
def main():
    st.title('Crypto Price Analysis with SMAs')

    # User input
    symbol = st.sidebar.text_input('Enter Symbol (e.g., BTCUSDT)', 'BTCUSDT')

    # Weekly data (1 year)
    st.header('Weekly Klines with SMA (1 Year)')
    weekly_df = get_klines(symbol, '1w', limit=100)
    weekly_smas = {period: SMAIndicator(weekly_df['Close'], window=period).sma_indicator() for period in [5, 10, 20]}
    plot_data(weekly_df[-52:], {k: v[-52:] for k, v in weekly_smas.items()}, 'Weekly Klines with SMA (1 Year)')

    # Daily data (3 months)
    st.header('Daily Klines with SMA (3 Months)')
    daily_df = get_klines(symbol, '1d', limit=365)
    daily_smas = {period: SMAIndicator(daily_df['Close'], window=period).sma_indicator() for period in [50, 200]}
    plot_data(daily_df[-90:], {k: v[-90:] for k, v in daily_smas.items()}, 'Daily Klines with SMA (3 Months)')

    # Hourly data (1 week)
    st.header('Hourly Klines with SMA (1 Week)')
    hourly_df = get_klines(symbol, '1h', limit=1000)
    hourly_smas = {period: SMAIndicator(hourly_df['Close'], window=period).sma_indicator() for period in [20, 50, 100]}
    plot_data(hourly_df[-168:], {k: v[-168:] for k, v in hourly_smas.items()}, 'Hourly Klines with SMA (1 Week)')

if __name__ == '__main__':
    main()
