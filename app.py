import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="Advanced Stock Screener Pro", page_icon="📈", layout="wide")

st.title("🚀 Advanced Stock Screener (Long-Term & Swing Trading)")
st.markdown("Yeh app **Swing Trading** (Short-term momentum) aur **Long-Term Investment** (Fundamental strength) dono ke liye complete aur aasan Hindi analysis deti hai.")

st.markdown("---")

# Session state initialization for capital letters
if 'stock_input' not in st.session_state:
    st.session_state['stock_input'] = ""

def convert_to_caps():
    st.session_state['stock_input'] = st.session_state['stock_input'].upper().strip()

# Main Page Inputs
col_in1, col_in2, col_in3 = st.columns([2, 2, 1])
with col_in1:
    raw_symbol = st.text_input(
        "Stock Ka Naam Daalein (jaise BEL, RELIANCE, TCS)", 
        key='stock_input', 
        on_change=convert_to_caps
    )
with col_in2:
    exchange = st.selectbox("Exchange Chunein", ["NSE (.NS)", "BSE (.BO)"])
with col_in3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Deep Analyze Karein", type="primary")

symbol = st.session_state['stock_input']

if run_btn:
    if not symbol:
        st.warning("Kripya pehle stock ka naam daalein.")
    else:
        suffix = ".NS" if "NSE" in exchange else ".BO"
        ticker_symbol = symbol + suffix
        
        with st.spinner("Market data aur indicators calculate ho rahe hain..."):
            try:
                session = requests.Session()
                session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                
                stock = yf.Ticker(ticker_symbol, session=session)
                df = stock.history(period="1y")
                info = stock.info
                
                if df.empty or len(df) < 2:
                    st.error(f"'{symbol}' ke liye price data nahi mila. Kripya symbol check karein.")
                else:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                        
                    # --- TECHNICALS & SWING INDICATORS ---
                    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
                    
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    df['RSI'] = 100 - (100 / (1 + rs))
                    
                    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
                    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
                    df['MACD'] = exp1 - exp2
                    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
                    
                    close_series = df['Close'].dropna()
                    latest_close = float(close_series.iloc[-1]) if len(close_series) > 0 else 0.0
                    prev_close = float(close_series.iloc[-2]) if len(close_series) > 1 else latest_close
                    price_change = ((latest_close - prev_close) / prev_close) * 100 if prev_close else 0.0
                    
                    latest_rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
                    latest_ema20 = float(df['EMA_20'].iloc[-1]) if not pd.isna(df['EMA_20'].iloc[-1]) else latest_close
                    latest_ema50 = float(df['EMA_50'].iloc[-1]) if not pd.isna(df['EMA_50'].iloc[-1]) else latest_close
                    latest_macd = float(df['MACD'].iloc[-1]) if not pd.isna(df['MACD'].iloc[-1]) else 0.0
                    latest_signal = float(df['Signal_Line'].iloc[-1]) if not pd.isna(df['Signal_Line'].iloc[-1]) else 0.0
                    
                    # --- FUNDAMENTALS ---
                    market_cap = info.get('marketCap', None)
                    market_cap_str = f"₹{market_cap / 10000000:.2f} Crore" if market_cap and not pd.isna(market_cap) else 'N/A'
                        
                    pe_ratio = info.get('trailingPE', None)
                    pe_val = float(pe_ratio) if pe_ratio and not pd.isna(pe_ratio) else None
                    pe_str = f"{pe_val:.2f}" if pe_val is not None else 'N/A'
                    
                    roe = info.get('returnOnEquity', None)
                    roe_val = float(roe) * 100 if roe and not pd.isna(roe) else None
                    roe_str = f"{roe_val:.2f}%" if roe_val is not None else 'N/A'
                    
                    debt_to_equity = info.get('debtToEquity', None)
                    de_val = float(debt_to_equity) if debt_to_equity and not pd.isna(debt_to_equity) else None
                    de_str = f"{de_val:.2f}" if de_val is not None else 'N/A'
                    
                    dividend_yield = info.get('dividendYield', None)
                    div_val = float(dividend_yield) * 100 if dividend_yield and not pd.isna(dividend_yield) else None
                    div_str = f"{div_val:.2f}%" if div_val is not None else '0%'
                    
                    sector = info.get('sector', 'N/A')
                    industry = info.get('industry', 'N/A')
                    high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
                    low_52 = info.get('fiftyTwoWeekLow', 'N/A')
                    
                    # --- TABLE INDICATOR LOGIC ---
                    pe_status = f"{pe_str} 🟢" if pe_val and pe_val < 25 else (f"{pe_str} 🟡" if pe_val and pe_val <= 40 else f"{pe_str} 🔴") if pe_val else "N/A ⚪"
                    roe_status = f"{roe_str} 🟢" if roe_val and roe_val > 15 else (f"{roe_str} 🟡" if roe_val and roe_val >= 10 else f"{roe_str} 🔴") if roe_val else "N/A ⚪"
                    de_status = f"{de_str} 🟢" if de_val and de_val < 0.5 else (f"{de_str} 🟡" if de_val and de_val <= 1.5 else f"{de_str} 🔴") if de_val else "N/A 🟢"
                    
                    if 40 <= latest_rsi <= 60:
                        rsi_status = f"{latest_rsi:.2f} 🟢 (Balanced)"
                    elif latest_rsi < 35:
                        rsi_status = f"{latest_rsi:.2f} 🟢 (Oversold)"
                    else:
                        rsi_status = f"{latest_rsi:.2f} 🔴 (Overbought/High)"

                    macd_status = "Bullish 🟢" if latest_macd > latest_signal else "Bearish 🔴"

                    # --- TABS ---
                    tab1, tab2, tab3 = st.tabs(["🎯 Complete Saransh & Verdict (Hindi)", "🚀 Powerful Swing Trading Guide", "💼 Expert Long-Term Investment Analysis"])
                    
                    with tab1:
                        st.subheader("🤖 Smart Combined Verdict & Actionable Advice (Hindi)")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Abhi ka Bhav (Current Price)", f"₹{latest_close:.2f}", f"{price_change:.2f}%")
                            st.info(f"**Sector:** {sector}\n\n**Industry:** {industry}")
                            st.metric("Market Capitalization", market_cap_str)
                        with col_b:
                            score = 0
                            if latest_close > latest_ema20: score += 1
                            if latest_macd > latest_signal: score += 1
                            if pe_val and pe_val < 30: score += 1
                            if roe_val and roe_val > 15: score += 1
                            
                            if score >= 3:
                                st.success("**Overall Nishkarsh: STRONG BULLISH / MAZBOOT STHITI** ✅\nTechnical aur Fundamental dono parameters kafi behtar dikh rahe hain.")
                            elif score == 2:
                                st.warning("**Overall Nishkarsh: MODERATE / MIXED STHITI** ⚖️\nKuch cheezein acchi hain par kuch par dhyan dena zaroori hai.")
                            else:
                                st.error("**Overall Nishkarsh: WEAK / SAWDHANI ZAROORI** ⚠️\nFilhal stock mein kamzori ya risk zyada lag raha hai.")
                        
                        st.markdown("---")
                        st.markdown("### 🚦 Clear Buying & Holding Verdict (Kya Karein?):")
                        
                        if score >= 3:
                            st.markdown("🟢 **Naya Kharidein (Fresh Buy):** Haan, aap ismein naya nivesh karne ka soch sakte hain.")
                            st.markdown("🔒 **Pehle se hai toh? (Existing Position):** **HOLD (Apne paas rakhein)**.")
                        elif score == 2:
                            st.markdown("🟡 **Naya Kharidein (Fresh Buy):** Thoda intezaar karein ya chote hisse mein entry lein.")
                            st.markdown("🔒 **Pehle se hai toh? (Existing Position):** **HOLD (Bane rahein)**.")
                        else:
                            st.markdown("🔴 **Naya Kharidein (Fresh Buy):** Filhal naya stock kharidne se bachein.")
                            st.markdown("🚪 **Pehle se hai toh? (Existing Position):** **SELL / EXIT (Nikal jayein)**.")

                        st.markdown("---")
                        st.markdown("### 📌 Quick Summary Table (With Indicators):")
                        summary_data = {
                            "Parameter": ["Valuation (P/E)", "Profitability (ROE)", "Karza (Debt/Equity)", "Momentum (RSI)", "Trend (MACD)"],
                            "Value/Status": [pe_status, roe_status, de_status, rsi_status, macd_status],
                            "Ideal Target": ["< 30", "> 15%", "< 0.5", "40 - 60", "Positive Crossover"]
                        }
                        st.table(pd.DataFrame(summary_data))

                    with tab2:
                        st.subheader("🚀 Powerful Swing Trading Analysis (Short-Term Momentum)")
                        s1, s2, s3, s4 = st.columns(4)
                        s1.metric("RSI Power", f"{latest_rsi:.2f}")
                        s2.metric("20-Day EMA", f"₹{latest_ema20:.2f}")
                        s3.metric("50-Day EMA", f"₹{latest_ema50:.2f}")
                        s4.metric("MACD Crossover", "Positive 🟢" if latest_macd > latest_signal else "Negative 🔴")
                        
                        st.markdown("---")
                        st.markdown("### 📋 Swing Trading Action Checklist:")
                        if latest_close > latest_ema20:
                            st.markdown("✅ **Trend:** Price 20-day EMA ke upar hai.")
                        else:
                            st.markdown("❌ **Trend:** Price 20-day EMA ke niche chal raha hai.")

                    with tab3:
                        st.subheader("💼 Expert Long-Term Investment Analysis")
                        st.markdown("Lambe samay ke nivesh (5-10 saal) ke liye business ki asli taqat yahan check karein:")
                        
                        pe_ind = "🟢 (Sasta / Behtareen)" if pe_val and pe_val < 25 else ("🟡 (Moderate)" if pe_val and pe_val <= 40 else "🔴 (Mehanga)") if pe_val else "⚪ (N/A)"
                        roe_ind = "🟢 (Shandaar)" if roe_val and roe_val > 15 else ("🟡 (Average)" if roe_val and roe_val >= 10 else "🔴 (Kamzor)") if roe_val else "⚪ (N/A)"
                        de_ind = "🟢 (Low Debt)" if de_val and de_val < 0.5 else ("🟡 (Moderate)" if de_val and de_val <= 1.5 else "🔴 (High Risk)") if de_val else "🟢 (Low Debt / N/A)"
                        div_ind = "🟢 (Accha)" if div_val and div_val > 2 else ("🟡 (Kam)" if div_val and div_val > 0 else "⚪ (Nahi Deti)") if div_val else "⚪ (N/A)"

                        f1, f2, f3, f4 = st.columns(4)
                        f1.metric("P/E Ratio", pe_str, pe_ind)
                        f2.metric("ROE (Return)", roe_str, roe_ind)
                        f3.metric("Debt-to-Equity", de_str, de_ind)
                        f4.metric("Dividend Yield", div_str, div_ind)
                        
                        st.markdown("---")
                        st.markdown("### 🔍 Gehri Jaanch aur Detailing (Deep-Dive Analysis in Hindi):")
                        st.markdown(f"P/E Ratio **{pe_str}** hai, ROE **{roe_str}** hai, aur Debt-to-Equity **{de_str}** hai.")

            except Exception as e:
                st.error(f"Koyi error aa gaya: {e}")
else:
    st.info("Upar diye gaye box mein stock ka symbol daal kar **'Deep Analyze Karein'** button dabayein.")
