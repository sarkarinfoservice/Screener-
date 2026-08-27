import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Easy Stock Analyzer", page_icon="📈", layout="wide")

st.title("📈 Easy Stock Screener (Long-Term & Swing Trading)")
st.markdown("Yahan aap kisi bhi NSE/BSE stock ka **Fundamental** (Lambe samay ki invest ke liye) aur **Technical** (Swing trading ke liye) aasan Hindi analysis dekh sakte hain.")

st.markdown("---")

# Main Page Inputs
col_in1, col_in2, col_in3 = st.columns([2, 2, 1])
with col_in1:
    symbol = st.text_input("Stock Ka Naam Daalein (jaise RELIANCE, TCS, INFY)", "RELIANCE").upper().strip()
with col_in2:
    exchange = st.selectbox("Exchange Chunein", ["NSE (.NS)", "BSE (.BO)"])
with col_in3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Analyze Karein", type="primary")

if run_btn:
    suffix = ".NS" if "NSE" in exchange else ".BO"
    ticker_symbol = symbol + suffix
    
    with st.spinner("Data check ho raha hai, kripya intezaar karein..."):
        try:
            stock = yf.Ticker(ticker_symbol)
            df = stock.history(period="1y")
            info = stock.info
            
            if df.empty or len(df) < 50:
                st.error("Galat symbol ya data uplabdh nahi hai. Kripya sahi naam daalein.")
            else:
                # --- TECHNICALS (SWING) ---
                df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
                
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
                
                # --- FUNDAMENTALS ---
                market_cap = info.get('marketCap', 'N/A')
                market_cap_str = f"₹{market_cap / 10000000:.2f} Crore" if market_cap != 'N/A' else 'N/A'
                pe_ratio = info.get('trailingPB', info.get('trailingPE', 'N/A')) # Fallback safe
                pe_ratio = info.get('trailingPE', 'N/A')
                roe = info.get('returnOnEquity', 'N/A')
                roe_str = f"{roe * 100:.2f}%" if roe and roe != 'N/A' else 'N/A'
                
                debt_to_equity = info.get('debtToEquity', 'N/A')
                
                dividend_yield = info.get('dividendYield', 0)
                div_str = f"{dividend_yield * 100:.2f}%" if dividend_yield and dividend_yield != 'N/A' else '0%'
                
                sector = info.get('sector', 'N/A')
                industry = info.get('industry', 'N/A')
                high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
                low_52 = info.get('fiftyTwoWeekLow', 'N/A')
                
                # --- TABS ---
                tab1, tab2, tab3 = st.tabs(["🎯 Saransh & Final Verdict (Hindi)", "🚀 Swing Trading (Thoda Short-Term)", "💼 Advanced Long-Term Investment"])
                
                with tab1:
                    st.subheader("🤖 Simple Hindi Verdict")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Abhi ka Bhav (Current Price)", f"₹{latest_close:.2f}", f"{price_change:.2f}%")
                        st.info(f"**Sector:** {sector}\n\n**Industry:** {industry}")
                        st.metric("Market Capitalization", market_cap_str)
                    with col_b:
                        score = 0
                        if latest_close > latest_ema20: score += 1
                        if pe_ratio != 'N/A' and pe_ratio < 30: score += 1
                        if roe != 'N/A' and roe > 0.15: score += 1
                        
                        if score >= 2:
                            st.success("**Nishkarsh (Verdict): POSITIVE / ACHHA STHITI** ✅\nStock ke fundamentals aur momentum dono theek lag rahe hain.")
                        else:
                            st.warning("**Nishkarsh (Verdict): CAUTION / SAWDHANI** ⚠️\nKuch metrics kamzor hain, soch-samjh kar kadam uthayein.")
                            
                    st.markdown("---")
                    st.markdown("### 💡 Mukhya Baatein (Key Highlights):")
                    st.markdown(f"- **Company ka Valuation (P/E):** `{pe_ratio}` (30 se kam behtar mana jata hai).")
                    st.markdown(f"- **Company ka Return (ROE):** `{roe_str}` (15% se zyada hona shandar hai).")
                    st.markdown(f"- **Karza (Debt-to-Equity):** `{debt_to_equity}` (Kam karza matlab zyada suraksha).")

                with tab2:
                    st.subheader("🚀 Swing Trading Guide (Kuch Hafton/Mahino ke liye)")
                    s1, s2, s3 = st.columns(3)
                    s1.metric("RSI Power", f"{latest_rsi:.2f}", "Sahi zone: 40 se 60")
                    s2.metric("20-Day Trend Line", f"₹{latest_ema20:.2f}")
                    s3.metric("50-Day Trend Line", f"₹{latest_ema50:.2f}")
                    
                    st.markdown("### 📋 Kya Karna Chahiye?")
                    if latest_close > latest_ema20 and latest_rsi < 65:
                        st.markdown("🟢 **Tezi ke sanket:** Stock short-term trend ke upar hai.")
                    else:
                        st.markdown("🔴 **Sustha/Kamzor sthiti:** Filhal tezi ki kami hai.")

                with tab3:
                    st.subheader("💼 Advanced Long-Term Investment Analysis")
                    st.markdown("Lambe samay (5-10 saal) ke nivesh ke liye company ke yeh 4 sabse bade pillars check karein:")
                    
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("P/E Ratio (Valuation)", str(pe_ratio))
                    f2.metric("ROE (Profitability)", roe_str)
                    f3.metric("Debt-to-Equity (Karza)", str(debt_to_equity))
                    f4.metric("Dividend Yield", div_str)
                    
                    st.markdown("---")
                    st.markdown("### 🔍 Detail Analysis & Simple Rules:")
                    
                    # Detailed explanations in Hindi
                    st.markdown("#### 1. Valuation & Pricing (P/E Ratio)")
                    st.markdown(f"Aapka P/E ratio **{pe_ratio}** hai. Yeh batata hai ki aap company ko kitna mehanga kharid rahe hain. Agar yeh 25-30 ke andar ho toh stock 'Fair Value' par hai, lekin agar bahut high ho toh risk badh jata hai.")
                    
                    st.markdown("#### 2. Business Efficiency (ROE - Return on Equity)")
                    st.markdown(f"Iska ROE **{roe_str}** hai. Yeh long-term investing ka sabse bada hathyar hai. 15% ya usse upar ka ROE yeh sabit karta hai ki management aapke invest kiye gaye har rupaye par accha munafa kama kar de rahi hai.")
                    
                    st.markdown("#### 3. Financial Safety (Debt-to-Equity / Karza)")
                    st.markdown(f"Iska Debt-to-Equity ratio **{debt_to_equity}** hai. Aisi companies jinke paas kam ya na ke barabar karza hota hai (debt-free), wohi mandi ya buri sthiti mein sabse lambi race chalti hain.")
                    
                    st.markdown("#### 4. Extra Income (Dividend Yield)")
                    st.markdown(f"Dividend Yield **{div_str}** hai. Yeh batata hai ki company apne munafey ka kitna hissa seedha aapke bank account mein bonus ya laabh ke roop mein bhejti hai.")

        except Exception as e:
            st.error(f"Koyi error aa gaya: {e}")
else:
    st.info("Upar diye gaye box mein stock ka symbol daal kar **'Analyze Karein'** button dabayein.")
