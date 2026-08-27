import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Investment & Swing Analyzer", page_icon="📈", layout="wide")

st.title("📈 Swing Trading & Long-Term Investment Screener")
st.markdown("Yeh app **Long-Term Investing** (Fundamentals) aur **Swing Trading** (Technical Momentum) ke liye stock analyze karti hai.")

st.markdown("---")

# Main Page Inputs
col_in1, col_in2, col_in3 = st.columns([2, 2, 1])
with col_in1:
    symbol = st.text_input("Stock Symbol (jaise RELIANCE, TCS, INFY)", "RELIANCE").upper().strip()
with col_in2:
    exchange = st.selectbox("Exchange", ["NSE (.NS)", "BSE (.BO)"])
with col_in3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Analyze Stock", type="primary")

if run_btn:
    suffix = ".NS" if "NSE" in exchange else ".BO"
    ticker_symbol = symbol + suffix
    
    with st.spinner("Data analyze ho raha hai..."):
        try:
            stock = yf.Ticker(ticker_symbol)
            df = stock.history(period="1y")
            info = stock.info
            
            if df.empty or len(df) < 50:
                st.error("Invalid symbol ya data insufficient hai.")
            else:
                # --- TECHNICALS (SWING TRADING) ---
                df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
                
                # RSI (14)
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                latest_close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                price_change = ((latest_close - prev_close) / prev_close) * 100
                latest_rsi = df['RSI'].iloc[-1]
                latest_ema20 = df['EMA_20'].iloc[-1]
                latest_ema50 = df['EMA_50'].iloc[-1]
                
                # --- FUNDAMENTALS (LONG-TERM) ---
                market_cap = info.get('marketCap', 'N/A')
                market_cap_str = f"₹{market_cap / 10000000:.2f} Cr" if market_cap != 'N/A' else 'N/A'
                pe_ratio = info.get('trailingPE', 'N/A')
                pb_ratio = info.get('priceToBook', 'N/A')
                roe = info.get('returnOnEquity', 'N/A')
                roe_str = f"{roe * 100:.2f}%" if roe and roe != 'N/A' else 'N/A'
                debt_to_equity = info.get('debtToEquity', 'N/A')
                sector = info.get('sector', 'N/A')
                industry = info.get('industry', 'N/A')
                
                # --- TABS LAYOUT (Price Chart Removed, Hindi Summary Added) ---
                tab1, tab2, tab3 = st.tabs(["🎯 Summary & Verdict (Hindi)", "🚀 Swing Trading Setup", "💼 Long-Term Investment Check"])
                
                with tab1:
                    st.subheader("🤖 Dual Strategy Summary & Verdict (Hindi mein)")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Current Price (Vartaman Mulya)", f"₹{latest_close:.2f}", f"{price_change:.2f}%")
                        st.info(f"**Sector:** {sector} | **Industry:** {industry}")
                        st.metric("Market Cap", market_cap_str)
                    with col_b:
                        # Swing check
                        if latest_close > latest_ema20 and latest_rsi < 65:
                            swing_hindi = "🚀 Tezi / Momentum mein hai (Bullish)"
                        else:
                            swing_hindi = "⚠️ Sideways ya Kamzor trend (Consolidating/Weak)"
                            
                        # Long-term check
                        if pe_ratio != 'N/A' and pe_ratio < 35 and roe != 'N/A' and roe > 0.12:
                            lt_hindi = "✅ Majboot Fundamentals (Strong Investment Potential)"
                        else:
                            lt_hindi = "⚠️ Sawdhani rakhein / Mixed metrics (Need Caution)"
                        
                        st.success(f"**Swing Trading Outlook:**\n{swing_hindi}")
                        st.info(f"**Long-Term Investment Outlook:**\n{lt_hindi}")
                    
                    st.markdown("---")
                    st.markdown("### 📌 Quick Insights:")
                    st.markdown(f"- **P/E Ratio:** {pe_ratio} (Company sasti ya mehngi hai yeh isse pata chalta hai)")
                    st.markdown(f"- **Return on Equity (ROE):** {roe_str} (Management paise ka kitna accha use kar rahi hai)")
                    st.markdown(f"- **RSI (14):** {latest_rsi:.2f} (Overbought ya Oversold sthiti ki jankari)")

                with tab2:
                    st.subheader("🚀 Swing Trading Analysis (Short to Medium-Term)")
                    st.markdown("Yeh section unke liye hai jo kuch hafton ya mahino ke momentum ke liye entry lena chahte hain.")
                    
                    s1, s2, s3 = st.columns(3)
                    s1.metric("RSI (14)", f"{latest_rsi:.2f}", "Ideal Buy zone: 40-55")
                    s2.metric("20 EMA", f"₹{latest_ema20:.2f}")
                    s3.metric("50 EMA", f"₹{latest_ema50:.2f}")
                    
                    st.markdown("### Swing Action Checklist:")
                    if latest_close > latest_ema20:
                        st.markdown("✅ **Trend Status:** Price 20 EMA ke upar hai (Short-term momentum positive).")
                    else:
                        st.markdown("❌ **Trend Status:** Price 20 EMA ke niche hai (Weak momentum).")
                        
                    if 40 <= latest_rsi <= 60:
                        st.markdown("✅ **RSI Status:** Healthy zone mein hai.")
                    elif latest_rsi < 40:
                        st.markdown("⚠️ **RSI Status:** Oversold zone ke paas hai, reversal ka wait karein.")
                    else:
                        st.markdown("⚠️ **RSI Status:** Overbought ho sakta hai, savdhan rahein.")

                with tab3:
                    st.subheader("💼 Long-Term Investment Analysis (Fundamental Health)")
                    st.markdown("Yeh section un investors ke liye hai jo lambe samay tak paisa invest karna chahte hain.")
                    
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("P/E Ratio", str(pe_ratio))
                    f2.metric("P/B Ratio", str(pb_ratio))
                    f3.metric("Return on Equity (ROE)", roe_str)
                    f4.metric("Debt to Equity", str(debt_to_equity))
                    
                    st.markdown("### Investment Quality Checks:")
                    if pe_ratio != 'N/A':
                        if pe_ratio < 30:
                            st.markdown(f"✅ **Valuation:** P/E ratio ({pe_ratio}) reasonable range mein hai.")
                        else:
                            st.markdown(f"⚠️ **Valuation:** P/E ratio ({pe_ratio}) high/expensive hai.")
                    
                    if roe != 'N/A':
                        if roe > 0.15:
                            st.markdown(f"✅ **Capital Efficiency:** Strong ROE ({roe_str}) hai.")
                        else:
                            st.markdown(f"⚠️ **Capital Efficiency:** ROE ({roe_str}) moderate ya low hai.")
                    
        except Exception as e:
            st.error(f"Error process karne mein: {e}")
else:
    st.info("Upar stock symbol daal kar aur exchange select karke **'Analyze Stock'** button par click karein.")
