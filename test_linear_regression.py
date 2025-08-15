#!/usr/bin/env python3
"""
Linear Regression Test Script for StockSage
This script tests the linear regression analysis with visualizations
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.linear_regression import LinearRegressionAnalyzer
    from core.data_fetcher import DataFetcher
    print("✅ Successfully imported modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure you're in the StockSage project directory")
    sys.exit(1)

def setup_plotting():
    """Setup matplotlib for better looking plots"""
    plt.style.use('seaborn-v0_8')
    plt.rcParams['figure.figsize'] = (15, 10)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3

def plot_trend_analysis(stock_data, trend_analysis, symbol):
    """Plot trend analysis for different periods"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Linear Regression Trend Analysis - {symbol}', fontsize=16, fontweight='bold')
    
    periods = ['20d', '50d', '100d']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for i, period in enumerate(periods):
        if period not in trend_analysis:
            continue
            
        data = trend_analysis[period]
        row = i // 2
        col = i % 2
        
        # Get the actual dates for this period
        recent_data = stock_data.tail(int(period[:-1]))
        dates = recent_data.index
        
        # Plot actual prices
        axes[row, col].plot(dates, data['actual'], label='Actual Price', 
                           color='#2E86AB', linewidth=2, alpha=0.8)
        
        # Plot regression line
        axes[row, col].plot(dates, data['predictions'], label='Regression Line', 
                           color=colors[i], linewidth=3, linestyle='--')
        
        # Add trend information
        trend_dir = data['trend_direction']
        strength = data['trend_strength']
        r_squared = data['r_squared']
        
        axes[row, col].set_title(f'{period} Trend Analysis\n'
                                f'Direction: {trend_dir} | Strength: {strength:.2f}% | R²: {r_squared:.3f}')
        axes[row, col].set_xlabel('Date')
        axes[row, col].set_ylabel('Price')
        axes[row, col].legend()
        axes[row, col].grid(True, alpha=0.3)
        
        # Format x-axis dates
        axes[row, col].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        axes[row, col].xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.setp(axes[row, col].xaxis.get_majorticklabels(), rotation=45)
    
    # Hide the 4th subplot if we only have 3 periods
    if len(periods) < 4:
        axes[1, 1].set_visible(False)
    
    plt.tight_layout()
    plt.show()

def plot_price_predictions(stock_data, price_predictions, symbol):
    """Plot price predictions with confidence intervals"""
    if not price_predictions:
        print("❌ No price predictions available")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    fig.suptitle(f'Price Predictions - {symbol}', fontsize=16, fontweight='bold')
    
    # Plot 1: Historical data with predictions
    recent_data = stock_data.tail(100)
    dates = recent_data.index
    prices = recent_data['Close']
    
    # Plot historical prices
    ax1.plot(dates, prices, label='Historical Prices', color='#2E86AB', linewidth=2)
    
    # Plot predictions
    pred_dates = [datetime.strptime(pred['date'], '%Y-%m-%d') for pred in price_predictions['predictions']]
    pred_prices = [pred['predicted_price'] for pred in price_predictions['predictions']]
    upper_bounds = [pred['upper_bound'] for pred in price_predictions['predictions']]
    lower_bounds = [pred['lower_bound'] for pred in price_predictions['predictions']]
    
    # Add prediction line
    ax1.plot(pred_dates, pred_prices, label='Predicted Prices', 
             color='#E63946', linewidth=3, linestyle='--')
    
    # Add confidence intervals
    ax1.fill_between(pred_dates, lower_bounds, upper_bounds, 
                     alpha=0.3, color='#E63946', label='Confidence Interval')
    
    ax1.set_title(f'Price Predictions (Next 30 Days)\n'
                  f'Current: ₹{price_predictions["current_price"]:.2f} | '
                  f'Predicted: ₹{price_predictions["predicted_end_price"]:.2f} | '
                  f'Change: {price_predictions["price_change_percent"]:.1f}%')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price (₹)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Format x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Prediction details
    days = list(range(1, len(pred_prices) + 1))
    
    ax2.plot(days, pred_prices, label='Predicted Price', color='#E63946', linewidth=2)
    ax2.fill_between(days, lower_bounds, upper_bounds, 
                     alpha=0.3, color='#E63946', label='Confidence Interval')
    
    # Add current price line
    ax2.axhline(y=price_predictions['current_price'], color='#2E86AB', 
                linestyle='-', linewidth=2, label='Current Price')
    
    ax2.set_title('Prediction Timeline')
    ax2.set_xlabel('Days Ahead')
    ax2.set_ylabel('Price (₹)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_support_resistance(stock_data, support_resistance, symbol):
    """Plot support and resistance levels"""
    if not support_resistance:
        print("❌ No support/resistance data available")
        return
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    
    # Plot price data
    dates = stock_data.index
    prices = stock_data['Close']
    
    ax.plot(dates, prices, label='Stock Price', color='#2E86AB', linewidth=2)
    
    # Add support and resistance lines
    current_price = support_resistance['current_price']
    resistance_level = support_resistance['resistance_level']
    support_level = support_resistance['support_level']
    
    # Plot horizontal lines
    ax.axhline(y=resistance_level, color='#E63946', linestyle='--', 
               linewidth=2, label=f'Resistance: ₹{resistance_level:.2f}')
    ax.axhline(y=support_level, color='#2CA02C', linestyle='--', 
               linewidth=2, label=f'Support: ₹{support_level:.2f}')
    ax.axhline(y=current_price, color='#FF7F0E', linestyle='-', 
               linewidth=2, label=f'Current: ₹{current_price:.2f}')
    
    # Add distance information
    distance_to_resistance = support_resistance['distance_to_resistance']
    distance_to_support = support_resistance['distance_to_support']
    
    ax.set_title(f'Support and Resistance Levels - {symbol}\n'
                 f'Distance to Resistance: ₹{distance_to_resistance:.2f} | '
                 f'Distance to Support: ₹{distance_to_support:.2f}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (₹)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.show()

def plot_volume_price_trend(stock_data, volume_price_trend, symbol):
    """Plot volume-price trend analysis"""
    if not volume_price_trend:
        print("❌ No volume-price trend data available")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
    fig.suptitle(f'Volume-Price Trend Analysis - {symbol}', fontsize=16, fontweight='bold')
    
    # Plot 1: Price and Volume
    recent_data = stock_data.tail(50)
    dates = recent_data.index
    prices = recent_data['Close']
    volumes = recent_data['Volume']
    
    # Create twin axes for price and volume
    ax1_twin = ax1.twinx()
    
    # Plot price
    line1 = ax1.plot(dates, prices, color='#2E86AB', linewidth=2, label='Price')
    ax1.set_ylabel('Price (₹)', color='#2E86AB')
    ax1.tick_params(axis='y', labelcolor='#2E86AB')
    
    # Plot volume
    line2 = ax1_twin.plot(dates, volumes, color='#E63946', alpha=0.7, linewidth=1, label='Volume')
    ax1_twin.set_ylabel('Volume', color='#E63946')
    ax1_twin.tick_params(axis='y', labelcolor='#E63946')
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    ax1.set_title('Price and Volume Over Time')
    ax1.grid(True, alpha=0.3)
    
    # Format x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Volume-Price Correlation
    price_changes = recent_data['Close'].pct_change().dropna()
    volumes_aligned = recent_data['Volume'].iloc[1:]
    
    ax2.scatter(price_changes, volumes_aligned, alpha=0.6, color='#2E86AB')
    ax2.set_xlabel('Price Change (%)')
    ax2.set_ylabel('Volume')
    ax2.set_title(f'Volume-Price Correlation\n'
                  f'Correlation: {volume_price_trend["volume_price_correlation"]:.3f} | '
                  f'Volume Ratio: {volume_price_trend["volume_ratio"]:.2f}')
    ax2.grid(True, alpha=0.3)
    
    # Add trend line
    if len(price_changes) > 1:
        z = np.polyfit(price_changes, volumes_aligned, 1)
        p = np.poly1d(z)
        ax2.plot(price_changes, p(price_changes), "r--", alpha=0.8)
    
    plt.tight_layout()
    plt.show()

def print_analysis_summary(symbol, trend_analysis, price_predictions, support_resistance, volume_price_trend):
    """Print a summary of all analysis results"""
    print("\n" + "="*80)
    print(f"📊 LINEAR REGRESSION ANALYSIS SUMMARY - {symbol}")
    print("="*80)
    
    # Trend Analysis Summary
    print("\n🔍 TREND ANALYSIS:")
    print("-" * 40)
    for period, data in trend_analysis.items():
        print(f"{period:>6} | Direction: {data['trend_direction']:>8} | "
              f"Strength: {data['trend_strength']:>6.2f}% | R²: {data['r_squared']:>6.3f}")
    
    # Price Predictions Summary
    if price_predictions:
        print("\n🔮 PRICE PREDICTIONS:")
        print("-" * 40)
        print(f"Current Price:     ₹{price_predictions['current_price']:.2f}")
        print(f"Predicted Price:   ₹{price_predictions['predicted_end_price']:.2f}")
        print(f"Price Change:      ₹{price_predictions['price_change']:.2f}")
        print(f"Change %:          {price_predictions['price_change_percent']:.2f}%")
        print(f"Trend Direction:   {price_predictions['trend_direction']}")
        print(f"Model Accuracy:    {price_predictions['model_accuracy']:.3f}")
    
    # Support/Resistance Summary
    if support_resistance:
        print("\n🎯 SUPPORT & RESISTANCE:")
        print("-" * 40)
        print(f"Current Price:     ₹{support_resistance['current_price']:.2f}")
        print(f"Resistance Level:  ₹{support_resistance['resistance_level']:.2f}")
        print(f"Support Level:     ₹{support_resistance['support_level']:.2f}")
        print(f"Distance to Res:   ₹{support_resistance['distance_to_resistance']:.2f}")
        print(f"Distance to Sup:   ₹{support_resistance['distance_to_support']:.2f}")
        print(f"Nearest Level:     {support_resistance['nearest_level']}")
    
    # Volume-Price Trend Summary
    if volume_price_trend:
        print("\n📈 VOLUME-PRICE TREND:")
        print("-" * 40)
        print(f"Correlation:       {volume_price_trend['volume_price_correlation']:.3f}")
        print(f"Volume Ratio:      {volume_price_trend['volume_ratio']:.2f}")
        print(f"Confirms Trend:    {volume_price_trend['volume_confirms_trend']}")
        print(f"Model Accuracy:    {volume_price_trend['model_accuracy']:.3f}")
    
    print("\n" + "="*80)

def main():
    """Main function to run the linear regression test"""
    print("🚀 StockSage Linear Regression Test")
    print("=" * 50)
    
    # Setup plotting
    setup_plotting()
    
    # Initialize analyzers
    data_fetcher = DataFetcher()
    lr_analyzer = LinearRegressionAnalyzer()
    
    # Get stock symbol from user
    symbol = input("\nEnter stock symbol (e.g., RELIANCE.NS, TCS.BO, AAPL): ").strip().upper()
    
    if not symbol:
        symbol = "RELIANCE.NS"  # Default symbol
        print(f"Using default symbol: {symbol}")
    
    print(f"\n📊 Fetching data for {symbol}...")
    
    try:
        # Fetch stock data
        stock_data = data_fetcher.get_stock_data(symbol, period='6mo')
        
        if stock_data is None or stock_data.empty:
            print(f"❌ Unable to fetch data for {symbol}")
            return
        
        print(f"✅ Successfully fetched {len(stock_data)} data points")
        
        # Perform linear regression analysis
        print("\n🔍 Performing linear regression analysis...")
        
        # Trend analysis
        trend_analysis = lr_analyzer.calculate_trend_analysis(stock_data)
        print("✅ Trend analysis completed")
        
        # Price predictions
        price_predictions = lr_analyzer.predict_future_prices(stock_data)
        print("✅ Price predictions completed")
        
        # Support and resistance
        support_resistance = lr_analyzer.calculate_support_resistance(stock_data)
        print("✅ Support/resistance analysis completed")
        
        # Volume-price trend
        volume_price_trend = lr_analyzer.calculate_volume_price_trend(stock_data)
        print("✅ Volume-price trend analysis completed")
        
        # Print summary
        print_analysis_summary(symbol, trend_analysis, price_predictions, 
                              support_resistance, volume_price_trend)
        
        # Show plots
        print("\n📈 Generating visualizations...")
        
        # Plot trend analysis
        plot_trend_analysis(stock_data, trend_analysis, symbol)
        
        # Plot price predictions
        plot_price_predictions(stock_data, price_predictions, symbol)
        
        # Plot support and resistance
        plot_support_resistance(stock_data, support_resistance, symbol)
        
        # Plot volume-price trend
        plot_volume_price_trend(stock_data, volume_price_trend, symbol)
        
        print("\n✅ Analysis complete! Check the plots above.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
