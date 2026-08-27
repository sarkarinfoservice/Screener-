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
                pe_ratio = info.get('trailingPE', 'N/A')
                roe = info.get('returnOnEquity', 'N/A')
                roe_str = f"{roe * 100:.2f}%" if roe and roe != 'N/A' else 'N/A'
                dividend_yield = info.get('dividendYield', 0)
                div_str = f"{dividend_yield * 100:.2f}%" if dividend_yield and dividend_yield != 'N/A' else 'N/A'
                sector = info.get('sector', 'N/A')
                industry = info.get('industry', 'N/A')
                high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
                low_52 = info.get('fiftyTwoWeekLow', 'N/A')
                
                # --- TABS ---
                tab1, tab2, tab3 = st.tabs(["🎯 Saransh & Final Verdict (Hindi)", "🚀 Swing Trading (Thoda Short-Term)", "💼 Long-Term Investment (Lambe Samay Ke Liye)"])
                
                with tab1:
                    st.subheader("🤖 Simple Hindi Verdict")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Abhi ka Bhav (Current Price)", f"₹{latest_close:.2f}", f"{price_change:.2f}%")
                        st.info(f"**Sector:** {sector}\n\n**Industry:** {industry}")
                        st.metric("Market Capitalization", market_cap_str)
                    with col_b:
                        # Simple logic for summary
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
                    st.markdown(f"- **Company ka Valuation (P/E):** `{pe_ratio}` (Agar yeh 30 se kam ho toh stock sasta ya theek daam par mana jata hai).")
                    st.markdown(f"- **Company ka Return (ROE):** `{roe_str}` (Agar yeh 15% se upar ho toh company paisa banane mein expert hai).")
                    st.markdown(f"- **Dividend (Laabh):** `{div_str}` (Company apne investors ko extra bonus/dividend kitna deti hai).")

                with tab2:
                    st.subheader("🚀 Swing Trading Guide (Kuch Hafton/Mahino ke liye)")
                    st.markdown("Yeh unke liye hai jo chote samay mein tezi ka fayda uthana chahte hain.")
                    
                    s1, s2, s3 = st.columns(3)
                    s1.metric("RSI Power", f"{latest_rsi:.2f}", "Sahi zone: 40 se 60")
                    s2.metric("20-Day Trend Line", f"₹{latest_ema20:.2f}")
                    s3.metric("50-Day Trend Line", f"₹{latest_ema50:.2f}")
                    
                    st.markdown("### 📋 Kya Karna Chahiye?")
                    if latest_close > latest_ema20 and latest_rsi < 65:
                        st.markdown("🟢 **Tezi ke sanket:** Stock apne short-term trend ke upar chal raha hai. Momentum accha hai.")
                    else:
                        st.markdown("🔴 **Sustha/Kamzor sthiti:** Filhal stock mein tezi ki kami hai ya price niche chal raha hai.")
                        
                    if latest_rsi < 35:
                        st.markdown("💡 **Tip:** RSI 35 se kam hone par stock 'Oversold' (bohot gira hua) mana jata hai, yahan se recovery aa sakti hai.")
                    elif latest_rsi > 70:
                        st.markdown("⚠️ **Tip:** RSI 70 se upar hone par stock 'Overbought' hota hai, yahan se girawat ka khatra hota hai.")

                with tab3:
                    st.subheader("💼 Long-Term Investment Guide (Saalon ke liye)")
                    st.markdown("Yeh unke liye hai jo company mein hissedari lekar lambe samay tak chhodna chahte hain.")
                    
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("P/E Ratio", str(pe_ratio))
                    f2.metric("ROE (Profitability)", roe_str)
                    f3.metric("52-Week High", f"₹{high_52}" if high_52 != 'N/A' else 'N/A')
                    f4.metric("52-Week Low", f"₹{low_52}" if low_52 != 'N/A' else 'N/A')
                    
                    st.markdown("### 📋 3 Golden Rules (Long-Term ke liye):")
                    st.markdown("1. **Strong Business:** Kya yeh aisi company hai jiska product aap ya log roz use karte hain?")
                    st.markdown(f"2. **Theek Daam (Valuation):** Iska P/E ratio `{pe_ratio}` hai. Bohot mehnge daam par kharidne se bachein.")
                    st.markdown(f"3. **Accha Return:** Iska ROE `{roe_str}` hai, jo yeh batata hai ki company apne business se kitna shandar munafa nikal rahi hai.")

        except Exception as e:
            st.error(f"Koyi error aa gaya: {e}")
else:
    st.info("Upar diye gaye box mein stock ka symbol daal kar **'Analyze Karein'** button dabayein.")
