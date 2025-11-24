
import yfinance as yf
import sys
import pandas as pd

def get_return(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if data.empty:
            return None
        start_price = float(data['Close'].iloc[0])
        end_price = float(data['Close'].iloc[-1])
        return (end_price / start_price) - 1
    except Exception as e:
        return None

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python compare_stocks.py <ticker1> <ticker2> <start_date> <end_date>")
        sys.exit(1)

    ticker1 = sys.argv[1]
    ticker2 = sys.argv[2]
    start_date = sys.argv[3]
    end_date = sys.argv[4]

    return1 = get_return(ticker1, start_date, end_date)
    return2 = get_return(ticker2, start_date, end_date)

    print(f"--- Monthly Return ({start_date} to {end_date}) ---")
    if return1 is not None:
        print(f"{ticker1}: {return1:.2%}")
    else:
        print(f"{ticker1}: N/A")

    if return2 is not None:
        print(f"{ticker2}: {return2:.2%}")
    else:
        print(f"{ticker2}: N/A")
