import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Advanced Stock Screener Pro", page_icon="📈", layout="wide")

st.title("🚀 Advanced Stock Screener (Long-Term & Swing Trading)")
st.markdown("Yeh app **Swing Trading** (Short-term momentum) aur **Long-Term Investment** (Fundamental strength) dono ke liye complete aur aasan Hindi analysis deti hai.")

st.markdown("---")

# Main Page Inputs
col_in1, col_in2, col_in3 = st.columns([2, 2, 1])
with col_in1:
    symbol = st.text_input("Stock Ka Naam Daalein (jaise RELIANCE, TCS, INFY)", "RELIANCE").upper().strip()
with col_in2:
    exchange = st.selectbox("Exchange Chunein", ["NSE (.NS)", "BSE (.BO)"])
with col_in3:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Deep Analyze Karein", type="primary")

if run_btn:
    suffix = ".NS" if "NSE" in exchange else ".BO"
    ticker_symbol = symbol + suffix
    
    with st.spinner("Market data aur indicators calculate ho rahe hain..."):
        try:
            stock = yf.Ticker(ticker_symbol)
            df = stock.history(period="1y")
            info = stock.info
            
            if df.empty or len(df) < 50:
                st.error("Galat symbol ya data uplabdh nahi hai. Kripya sahi naam daalein.")
            else:
                # --- TECHNICALS & SWING INDICATORS ---
                df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
                
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
                latest_ema20 = df['EMA_20'].iloc[-1]
                latest_ema50 = df['EMA_50'].iloc[-1]
                latest_macd = df['MACD'].iloc[-1]
                latest_signal = df['Signal_Line'].iloc[-1]
                
                # --- FUNDAMENTALS ---
                market_cap = info.get('marketCap', 'N/A')
                market_cap_str = f"₹{market_cap / 10000000:.2f} Crore" if market_cap != 'N/A' else 'N/A'
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
                tab1, tab2, tab3 = st.tabs(["🎯 Complete Saransh & Verdict (Hindi)", "🚀 Powerful Swing Trading Guide", "💼 Expert Long-Term Investment Analysis"])
                
                with tab1:
                    st.subheader("🤖 Smart Combined Verdict (Hindi)")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Abhi ka Bhav (Current Price)", f"₹{latest_close:.2f}", f"{price_change:.2f}%")
                        st.info(f"**Sector:** {sector}\n\n**Industry:** {industry}")
                        st.metric("Market Capitalization", market_cap_str)
                    with col_b:
                        # Scoring logic for overall health
                        score = 0
                        if latest_close > latest_ema20: score += 1
                        if latest_macd > latest_signal: score += 1
                        if pe_ratio != 'N/A' and pe_ratio < 30: score += 1
                        if roe != 'N/A' and roe > 0.15: score += 1
                        
                        if score >= 3:
                            st.success("**Overall Nishkarsh: STRONG BULLISH / MAZBOOT STHITI** ✅\nTechnical aur Fundamental dono parameters kafi behtar dikh rahe hain.")
                        elif score == 2:
                            st.warning("**Overall Nishkarsh: MODERATE / MIXED STHITI** ⚖️\nKuch cheezein acchi hain par kuch par dhyan dena zaroori hai.")
                        else:
                            st.error("**Overall Nishkarsh: WEAK / SAWDHANI ZAROORI** ⚠️\nFilhal stock mein kamzori ya risk zyada lag raha hai.")
                            
                    st.markdown("---")
                    st.markdown("### 📌 Quick Summary Table:")
                    summary_data = {
                        "Parameter": ["Valuation (P/E)", "Profitability (ROE)", "Karza (Debt/Equity)", "Momentum (RSI)", "Trend (MACD)"],
                        "Value/Status": [str(pe_ratio), roe_str, str(debt_to_equity), f"{latest_rsi:.2f}", "Bullish" if latest_macd > latest_signal else "Bearish"],
                        "Ideal Target": ["< 30", "> 15%", "< 0.5", "40 - 60", "Positive Crossover"]
                    }
                    st.table(pd.DataFrame(summary_data))

                with tab2:
                    st.subheader("🚀 Powerful Swing Trading Analysis (Short-Term Momentum)")
                    st.markdown("Yeh section unke liye hai jo kuch hafton ke andarkaar tezi ya breakout ka fayda uthana chahte hain.")
                    
                    s1, s2, s3, s4 = st.columns(4)
                    s1.metric("RSI Power", f"{latest_rsi:.2f}")
                    s2.metric("20-Day EMA", f"₹{latest_ema20:.2f}")
                    s3.metric("50-Day EMA", f"₹{latest_ema50:.2f}")
                    s4.metric("MACD Crossover", "Positive 🟢" if latest_macd > latest_signal else "Negative 🔴")
                    
                    st.markdown("---")
                    st.markdown("### 📋 Swing Trading Action Checklist:")
                    
                    if latest_close > latest_ema20:
                        st.markdown("✅ **Trend:** Price 20-day EMA ke upar hai, matlab short-term trend upar ki taraf hai.")
                    else:
                        st.markdown("❌ **Trend:** Price 20-day EMA ke niche chal raha hai (Cautious rahein).")
                        
                    if latest_macd > latest_signal:
                        st.markdown("✅ **Momentum (MACD):** MACD signal line ke upar hai, jo buying momentum ko dikhata hai.")
                    else:
                        st.markdown("❌ **Momentum (MACD):** MACD signal line ke niche hai, selling pressure ho sakti hai.")
                        
                    if 40 <= latest_rsi <= 60:
                        st.markdown("✅ **RSI Zone:** RSI ekdam balanced zone mein hai, bada move aa sakta hai.")
                    elif latest_rsi > 70:
                        st.markdown("⚠️ **RSI Zone:** Stock 'Overbought' hai, yahan se profit booking aa sakti hai.")
                    elif latest_rsi < 35:
                        st.markdown("💡 **RSI Zone:** Stock 'Oversold' hai, yahan se sharp recovery ban sakti hai.")

                with tab3:
                    st.subheader("💼 Expert Long-Term Investment Analysis")
                    st.markdown("Lambe samay ke nivesh (5-10 saal) ke liye business ki asli taqat yahan check karein:")
                    
                    f1, f2, f3, f4 = st.columns(4)
                    f1.metric("P/E Ratio", str(pe_ratio))
                    f2.metric("ROE (Return)", roe_str)
                    f3.metric("Debt-to-Equity", str(debt_to_equity))
                    f4.metric("Dividend Yield", div_str)
                    
                    st.markdown("---")
                    st.markdown("### 🔍 Gehri Jaanch (Deep-Dive Analysis in Hindi):")
                    
                    st.markdown("#### 1. Company Kitni Sasti ya Mehngi Hai? (Valuation)")
                    st.markdown(f"P/E Ratio **{pe_ratio}** hai. Agar yeh apne industry average se kam aur 30 ke andar ho, toh ise achha daam mana jata hai. Mehngi companies mein growth expectations pehle se hi judi hoti hain.")
                    
                    st.markdown("#### 2. Management Ka Performance (ROE)")
                    st.markdown(f"Return on Equity (ROE) **{roe_str}** hai. 15% ya usse zyada ka ROE yeh sabit karta hai ki company apne business se zabardast munafa nikal kar de rahi hai, jo long-term wealth creation ki sabse badi shart hai.")
                    
                    st.markdown("#### 3. Suraksha aur Karza (Financial Stability)")
                    st.markdown(f"Debt-to-Equity ratio **{debt_to_equity}** hai. Kam karza ya debt-free hona kisi bhi company ko economic crisis mein bhi surakshit rakhta hai.")
                    
                    st.markdown("#### 4. 52-Week Range (Price Context)")
                    st.markdown(f"Pichle ek saal mein stock ka high **₹{high_52}** aur low **₹{low_52}** raha hai. Yeh dekh kar aap andaza laga sakte hain ki stock apne high se kitna discount par mil raha hai.")

        except Exception as e:
            st.error(f"Koyi error aa gaya: {e}")
else:
    st.info("Upar diye gaye box mein stock ka symbol daal kar **'Deep Analyze Karein'** button dabayein.")
