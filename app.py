import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Complete Stock Analyzer Pro", page_icon="📈", layout="wide")

st.title("🚀 Complete Stock Analyzer Pro (Investor + Trader Edition)")
st.markdown("Ek aisi advanced app jo **Fundamental Analysis** (Investors ke liye) aur **Technical Analysis** (Traders ke liye) dono ko combine karke complete verdict deti hai.")

# Sidebar inputs
st.sidebar.header("Configuration")
symbol = st.sidebar.text_input("Stock Symbol (e.g., RELIANCE, TCS, INFY)", "RELIANCE").upper().strip()
exchange = st.sidebar.selectbox("Exchange", ["NSE (.NS)", "BSE (.BO)"])

if st.sidebar.button("Run Full Analysis", type="primary"):
    suffix = ".NS" if "NSE" in exchange else ".BO"
    ticker_symbol = symbol + suffix
    
    with st.spinner("Fetching market data and processing metrics..."):
        try:
            stock = yf.Ticker(ticker_symbol)
            df = stock.history(period="1y")
            info = stock.info
            
            if df.empty or len(df) < 50:
                st.error("Invalid symbol ya data insufficient hai.")
            else:
                # --- TECHNICAL CALCULATIONS ---
                df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
                df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
                
                # RSI (14)
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                # MACD Calculation
                exp1 = df['Close'].ewm(span=12, adjust=False).mean()
                exp2 = df['Close'].ewm(span=26, adjust=False).mean()
                df['MACD'] = exp1 - exp2
                df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
                
                latest_close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                price_change = ((latest_close - prev_close) / prev_close) * 100
                latest_rsi = df['RSI'].iloc[-1]
                latest_ema50 = df['EMA_50'].iloc[-1]
                latest_ema200 = df['EMA_200'].iloc[-1]
                latest_macd = df['MACD'].iloc[-1]
                latest_signal = df['Signal_Line'].iloc[-1]
                
                # --- FUNDAMENTAL DATA ---
                market_cap = info.get('marketCap', 'N/A')
                if market_cap != 'N/A':
                    market_cap_cr = market_cap / 10000000 
                    market_cap_str = f"₹{market_cap_cr:.2f} Cr"
                else:
                    market_cap_str = 'N/A'
                    
                pe_ratio = info.get('trailingPE', 'N/A')
                pb_ratio = info.get('priceToBook', 'N/A')
                dividend_yield = info.get('dividendYield', 0)
                if dividend_yield and dividend_yield != 'N/A':
                    dividend_yield_str = f"{dividend_yield * 100:.2f}%"
                else:
                    dividend_yield_str = 'N/A'
                    
                roe = info.get('returnOnEquity', 'N/A')
                if roe and roe != 'N/A':
                    roe_str = f"{roe * 100:.2f}%"
                else:
                    roe_str = 'N/A'
                    
                sector = info.get('sector', 'N/A')
                industry = info.get('industry', 'N/A')
                
                # --- TABS LAYOUT ---
                tab1, tab2, tab3, tab4 = st.tabs(["🎯 Combined Verdict", "📊 Technical Analysis (Traders)", "💼 Fundamental Analysis (Investors)", "📈 Price Chart"])
                
                with tab1:
                    st.subheader("🤖 AI Automated Scoring & Verdict")
                    
                    tech_score = 0
                    fund_score = 0
                    
                    # Tech scoring
                    if latest_rsi < 40: tech_score += 1
                    elif latest_rsi > 70: tech_score -= 1
                    
                    if latest_close > latest_ema50: tech_score += 1
                    else: tech_score -= 1
                    
                    if latest_macd > latest_signal: tech_score += 1
                    else: tech_score -= 1
                    
                    # Fund scoring
                    if pe_ratio != 'N/A' and pe_ratio < 30: fund_score += 1
                    if roe != 'N/A' and roe > 0.15: fund_score += 1
                    if market_cap_str != 'N/A': fund_score += 1
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Current Price", f"₹{latest_close:.2f}", f"{price_change:.2f}%")
                        st.info(f"**Sector:** {sector} | **Industry:** {industry}")
                    with col_b:
                        total_score = tech_score + fund_score
                        if total_score >= 3:
                            st.success("**Overall Recommendation: STRONG BUY** ✅\nDono technical aur fundamental factors positive zone mein hain.")
                        elif total_score <= -1:
                            st.error("**Overall Recommendation: SELL / AVOID** ❌\nMarket sentiment aur metrics weak hain.")
                        else:
                            st.warning("**Overall Recommendation: HOLD / NEUTRAL** ⚖️\nMixed signals hain, market direction ka wait karein.")
                    
                    st.markdown("---")
                    st.markdown("### Key Strengths & Risks:")
                    col_c, col_d = st.columns(2)
                    with col_c:
                        st.markdown("**🟢 Positive Drivers:**")
                        if latest_rsi < 40: st.markdown("- RSI oversold zone ke kareeb hai (Value buy).")
                        if latest_close > latest_ema50: st.markdown("- Stock 50-day EMA ke upar trend kar raha hai.")
                        if roe != 'N/A' and roe > 0.15: st.markdown(f"- Strong Return on Equity ({roe_str}).")
                        if pe_ratio != 'N/A' and pe_ratio < 25: st.markdown(f"- Reasonable Valuation (P/E: {pe_ratio}).")
                    with col_d:
                        st.markdown("**🔴 Risk Factors:**")
                        if latest_rsi > 70: st.markdown("- RSI overbought hai (Profit booking ka khatra).")
                        if latest_close < latest_ema50: st.markdown("- Downtrend pressure: Price 50 EMA ke niche hai.")
                        if pe_ratio != 'N/A' and pe_ratio > 40: st.markdown(f"- High Valuation (P/E: {pe_ratio}).")
                        if roe != 'N/A' and roe < 0.10: st.markdown(f"- Low ROE ({roe_str}).")

                with tab2:
                    st.subheader("📈 Technical Indicators (Short-term Traders)")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("RSI (14)", f"{latest_rsi:.2f}", "Overbought > 70 | Oversold < 30")
                    m2.metric("50 EMA", f"₹{latest_ema50:.2f}")
                    m3.metric("200 EMA", f"₹{latest_ema200:.2f}")
                    m4.metric("MACD Status", "Bullish" if latest_macd > latest_signal else "Bearish")
                    
                    st.markdown("### Technical Breakdown:")
                    if latest_macd > latest_signal:
                        st.success("MACD Crossover Positive hai (Bullish momentum).")
                    else:
                        st.error("MACD Crossover Negative hai (Bearish momentum).")

                with tab3:
                    st.subheader("📊 Fundamental Metrics (Long-term Investors)")
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("Market Cap", market_cap_str)
                    f2.metric("P/E Ratio", str(pe_ratio))
                    f3.metric("P/B Ratio", str(pb_ratio))
                    f4.metric("Dividend Yield", dividend_yield_str)
                    
                    f5, f6 = st.columns(2)
                    f5.metric("Return on Equity (ROE)", roe_str)
                    f6.metric("Company Profile", f"{info.get('longBusinessSummary', 'Description not available.')[:300]}...")

                with tab4:
                    st.markdown("### Price Action & Moving Averages Chart")
                    st.line_chart(df[['Close', 'EMA_50', 'EMA_200']])
                    
        except Exception as e:
            st.error(f"Error process karne mein: {e}")
else:
    st.info("Sidebar mein stock ka symbol daal kar **'Run Full Analysis'** button par click karein.")
