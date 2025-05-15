# Utility functions for the Streamlit application
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
class StockAPI:

    def __init__(self):
        self.api_key = st.secrets["API_KEY"]
        self.url = "https://alpha-vantage.p.rapidapi.com/query"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "alpha-vantage.p.rapidapi.com",
        }

    def symbol_search(self, company: str) -> pd.DataFrame:
        querystring = {
            "datatype": "json",
            "keywords": company,
            "function": "SYMBOL_SEARCH",
        }
        response = requests.get(url=self.url, headers=self.headers, params=querystring)
        data = response.json()["bestMatches"]
        return pd.DataFrame(data)

    def stock_data(self, symbol: str) -> pd.DataFrame:
        querystring = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact",
            "datatype": "json",
        }
        response = requests.get(url=self.url, headers=self.headers, params=querystring)

        try:
            data2 = response.json()["Time Series (Daily)"]
        except KeyError:
            st.error("Error: Could not retrieve data. Check your symbol or API limit.")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data2).T

        # Clean column names
        df.columns = df.columns.str.strip()

        # Convert data to float
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Drop rows with NaN values
        df = df.dropna()

        # Convert index to datetime
        df.index = pd.to_datetime(df.index)

        # Sort by date ascending
        df = df.sort_index()

        return df

    def plot_chart(self, df: pd.DataFrame) -> go.Figure:
        if df.empty:
            st.warning("No data available to plot.")
            return go.Figure()

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df.index,
                    open=df["1. open"],
                    high=df["2. high"],
                    low=df["3. low"],
                    close=df["4. close"],
                    
                )
            ]
        )

        fig.update_layout(
            title="Stock Price Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            width=1000,
            height=800,
        )

        return fig