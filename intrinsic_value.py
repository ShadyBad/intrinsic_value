import pandas as pd
import yfinance as yf
from datetime import datetime
import os

file_path = "stocks_data.csv"

def initialize_csv_file(file_path: str) -> None:
    """Initialize a csv file with the required columns if it doesn't exist."""
    if not os.path.exists(file_path):
        columns = ["ticker", "intrinsic_value", "last_updated"]
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)

def load_data(file_path):
    """Load data from the specified csv file."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return None
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return None

def save_data(df, file_path):
    """Save the DataFrame to the specified csv file."""
    if df is None:
        print("Error: Dataframe is None.")
        return
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return
    try:
        df.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

def fetch_stock_data(ticker):
    """Fetch earnings per share (EPS) and growth rate for the given stock ticker."""
    if not ticker:
        print('Error: Ticker symbol is empty.')
        return None, None
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info:
            print(f'Error: No information found for {ticker}.')
            return None, None
        eps = info.get("trailingEps", None)
        growth_rate = info.get("earningsGrowth", None)
        return eps, growth_rate
    except Exception as e:
        print(f'Error fetching data for {ticker}: {e}')
        return None, None

def calculate_intrinsic_value(eps, growth_rate, aa_bond_yield=4.4):
    """Calculate the intrinsic value of a stock using EPS and growth rate."""
    try:
        if eps is None or growth_rate is None:
            raise ValueError("EPS or growth rate is None")
        return eps * (8.5 + 2 * growth_rate) * 4.4 / aa_bond_yield
    except Exception as e:
        print(f"Error calculating intrinsic value: {e}")
        return None

def needs_update(last_updated):
    """Determine if the stock data needs to be updated based on the last updated date."""
    if last_updated is None:
        raise ValueError("Last updated date is None")
    try:
        last_updated_date = pd.to_datetime(last_updated).date()
        return last_updated_date != datetime.now().date()
    except Exception as e:
        print(f"Error checking for update: {e}")
        return True

def update_stock_data(ticker, file_path):
    """Update the stock data for a given ticker in the specified csv file."""
    if not ticker:
        print("Error: Ticker symbol is empty")
        return None

    df = load_data(file_path)
    if df is None:
        print("Error: Unable to load data from file")
        return None

    # Check if the ticker already exists in the dataframe
    if ticker in df['ticker'].values:
        row = df.loc[df['ticker'] == ticker]
        if not needs_update(row['last_updated'].iloc[0]):
            return row['intrinsic_value'].iloc[0]

    # Fetch the stock data
    eps, growth_rate = fetch_stock_data(ticker)
    if eps is None or growth_rate is None:
        print(f"Error: Unable to fetch data for {ticker}")
        return None

    # Calculate the intrinsic value
    intrinsic_value = calculate_intrinsic_value(eps, growth_rate)
    if intrinsic_value is None:
        print(f"Error: Unable to calculate intrinsic value for {ticker}")
        return None

    # Update the dataframe
    if ticker in df['ticker'].values:
        df.loc[df['ticker'] == ticker, ['intrinsic_value', 'last_updated']] = [intrinsic_value, datetime.now().date()]
    else:
        new_row = {"ticker": ticker, "intrinsic_value": intrinsic_value, "last_updated": datetime.now().date()}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save the dataframe
    try:
        save_data(df, file_path)
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")
        return None

    return intrinsic_value

def main():
    """Main function to initialize the file and update stock data for a user-input ticker."""
    try:
        initialize_csv_file(file_path)
    except Exception as e:
        print(f"Error initializing csv file: {e}")
        return

    ticker = input('Enter a stock ticker: ').upper().strip()
    if not ticker:
        print("Error: Ticker symbol is empty.")
        return

    intrinsic_value = update_stock_data(ticker, file_path)
    if intrinsic_value is not None:
        print(f"The intrinsic value of {ticker} is ${intrinsic_value:.2f}")
    else:
        print(f"Failed to fetch intrinsic value for {ticker}. Ensure the ticker is valid and try again.")

if __name__ == "__main__":
    main()