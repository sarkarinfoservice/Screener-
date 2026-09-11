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
                    
                    # RSI
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    df['RSI'] = 100 - (100 / (1 + rs))
                    
                    # MACD
                    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
                    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
                    df['MACD'] = exp1 - exp2
                    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

                    # Bollinger Bands & Volume
                    df['BB_Mid'] = df['Close'].rolling(window=20).mean()
                    df['BB_Std'] = df['Close'].rolling(window=20).std()
                    df['BB_Upper'] = df['BB_Mid'] + (2 * df['BB_Std'])
                    df['BB_Lower'] = df['BB_Mid'] - (2 * df['BB_Std'])
                    df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
                    
                    # Latest Values
                    close_series = df['Close'].dropna()
                    latest_close = float(close_series.iloc[-1]) if len(close_series) > 0 else 0.0
                    prev_close = float(close_series.iloc[-2]) if len(close_series) > 1 else latest_close
                    price_change = ((latest_close - prev_close) / prev_close) * 100 if prev_close else 0.0
                    
                    latest_rsi = float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else 50.0
                    latest_ema20 = float(df['EMA_20'].iloc[-1]) if not pd.isna(df['EMA_20'].iloc[-1]) else latest_close
                    latest_ema50 = float(df['EMA_50'].iloc[-1]) if not pd.isna(df['EMA_50'].iloc[-1]) else latest_close
                    latest_macd = float(df['MACD'].iloc[-1]) if not pd.isna(df['MACD'].iloc[-1]) else 0.0
                    latest_signal = float(df['Signal_Line'].iloc[-1]) if not pd.isna(df['Signal_Line'].iloc[-1]) else 0.0
                    
                    latest_vol = float(df['Volume'].iloc[-1])
                    vol_sma20 = float(df['Vol_SMA_20'].iloc[-1])
                    latest_bb_upper = float(df['BB_Upper'].iloc[-1])
                    latest_bb_lower = float(df['BB_Lower'].iloc[-1])
                    
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
                    
                    if 40 <= latest_rsi <= 65:
                        rsi_status = f"{latest_rsi:.2f} 🟢 (Balanced)"
                    elif latest_rsi < 35:
                        rsi_status = f"{latest_rsi:.2f} 🟢 (Oversold)"
                    else:
                        rsi_status = f"{latest_rsi:.2f} 🔴 (Overbought)"

                    macd_status = "Bullish 🟢" if latest_macd > latest_signal else "Bearish 🔴"

                    # --- TABS ---
                    tab1, tab2, tab3 = st.tabs(["🎯 Complete Saransh (Hindi)", "🚀 Powerful Swing Trading Guide", "💼 Expert Long-Term Analysis"])
                    
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
                        st.markdown("### 🚦 Overall Buying & Holding Verdict:")
                        if score >= 3:
                            st.markdown("🟢 **Naya Kharidein:** Haan, aap ismein naya nivesh karne ka soch sakte hain.")
                            st.markdown("🔒 **Existing Position:** **HOLD (Apne paas rakhein)**.")
                        elif score == 2:
                            st.markdown("🟡 **Naya Kharidein:** Thoda intezaar karein ya chote hisse mein entry lein.")
                            st.markdown("🔒 **Existing Position:** **HOLD (Bane rahein)**.")
                        else:
                            st.markdown("🔴 **Naya Kharidein:** Filhal naya stock kharidne se bachein.")
                            st.markdown("🚪 **Existing Position:** **SELL / EXIT (Nikal jayein)**.")

                        st.markdown("---")
                        st.table(pd.DataFrame({
                            "Parameter": ["Valuation (P/E)", "Profitability (ROE)", "Karza (Debt/Equity)", "Momentum (RSI)", "Trend (MACD)"],
                            "Value/Status": [pe_status, roe_status, de_status, rsi_status, macd_status],
                            "Ideal Target": ["< 30", "> 15%", "< 0.5", "40 - 65", "Positive Crossover"]
                        }))

                    # ==========================================
                    # TAB 2: SWING TRADING ANALYSIS + VERDICT
                    # ==========================================
                    with tab2:
                        st.subheader("🚀 Powerful Swing Trading Analysis (Short-Term Momentum)")
                        
                        # Top Metrics
                        s1, s2, s3, s4 = st.columns(4)
                        with s1:
                            st.metric("RSI (Momentum)", f"{latest_rsi:.2f}", "Overbought 🔴" if latest_rsi > 70 else "Oversold 🟢" if latest_rsi < 35 else "Balanced 🟢")
                        with s2:
                            st.metric("20-Day EMA (Trend)", f"₹{latest_ema20:.2f}")
                        with s3:
                            st.metric("MACD Crossover", "Bullish 🟢" if latest_macd > latest_signal else "Bearish 🔴")
                        with s4:
                            vol_status = "High Volume 🟢" if latest_vol > vol_sma20 else "Low Volume 🔴"
                            st.metric("Volume Activity", f"{latest_vol / 100000:.2f}L", vol_status)
                            st.caption(f"**Vol vs Avg:** {latest_vol / 100000:.2f}L / {vol_sma20 / 100000:.2f}L")
                        
                        st.markdown("---")
                        
                        # Detailed Checklist
                        st.markdown("### 📋 Swing Trading Action Checklist:")
                        
                        swing_score = 0
                        if latest_close > latest_ema20:
                            st.markdown("✅ **Trend (EMA):** Price 20-day EMA ke upar hai. (Trend **Bullish** hai)")
                            swing_score += 1
                        else:
                            st.markdown("❌ **Trend (EMA):** Price 20-day EMA ke niche chal raha hai. (Trend **Weak** hai)")
                            
                        if 40 <= latest_rsi <= 65:
                            st.markdown(f"✅ **RSI (Momentum):** RSI {latest_rsi:.2f} par hai (Perfect Zone 40-65).")
                            swing_score += 1
                        elif latest_rsi > 65:
                            st.markdown(f"⚠️ **RSI (Momentum):** RSI {latest_rsi:.2f} par hai. Stock overbought zone ke kareeb hai.")
                        else:
                            st.markdown(f"❌ **RSI (Momentum):** RSI {latest_rsi:.2f} par hai. Momentum weak hai.")

                        if latest_macd > latest_signal:
                            st.markdown("✅ **MACD:** MACD line Signal line ke upar hai. (Fresh **Buying interest**)")
                            swing_score += 1
                        else:
                            st.markdown("❌ **MACD:** MACD line Signal line ke niche hai. (**Selling pressure**)")

                        if latest_vol > vol_sma20:
                            st.markdown("✅ **Volume:** Aaj ka volume average volume se zyada hai. (**Strong Move**)")
                            swing_score += 1
                        else:
                            st.markdown("⚠️ **Volume:** Volume average se kam hai. (Move mein strength kam ho sakti hai)")

                        # SWING TRADING VERDICT
                        st.markdown("---")
                        st.markdown("### 🚦 Swing Trading Final Verdict (Kya Karein?):")
                        
                        if swing_score == 4:
                            st.success("**VERDICT: PERFECT SWING ENTRY (Mazboot Sthiti) 🚀**\nSaare parameters positive hain. Aap current price par ya halke dip par entry lene ka soch sakte hain.")
                        elif swing_score >= 2:
                            st.warning("**VERDICT: WAIT & WATCH (Ya Choti Quantity Lein) ⚖️**\nKuch indicators positive hain par sabhi nahi. Agar risk lena chahein toh sirf choti quantity mein trade lein ya perfect setup ka wait karein.")
                        else:
                            st.error("**VERDICT: AVOID / NO TRADE Zone 🚫**\nFilhal stock mein swing trading ke liye strength nahi hai. Reversal ya breakout ka wait karein, abhi entry na lein.")

                        st.markdown("---")
                        
                        # Trading Strategy Ideas
                        st.markdown("### 💡 Strategy Idea (Risk Management):")
                        st.markdown(f"> **🛡️ Stop-Loss:** Agar aap trade lete hain, toh apna Stop-Loss lagbhag **₹{latest_ema20:.2f}** (20-Day EMA) ya **₹{latest_bb_lower:.2f}** (Strong Support) ke thoda niche rakh sakte hain taaki risk kam rahe.")
                        if latest_close < latest_bb_upper:
                            st.markdown(f"> **🎯 Pehla Target:** **₹{latest_bb_upper:.2f}** (Bollinger Upper Band) ek accha short-term resistance/target ho sakta hai.")
                        else:
                            st.markdown(f"> **🎯 Target:** Stock pehle se hi resistance (₹{latest_bb_upper:.2f}) ke upar hai. Apne Stop-Loss ko trail karte rahein (Trail SL).")

                    # ==========================================
                    # TAB 3: EXPERT LONG-TERM ANALYSIS
                    # ==========================================
                    with tab3:
                        st.subheader("💼 Expert Long-Term Investment Analysis")
                        st.markdown("Lambe samay ke nivesh (5-10 saal) ke liye business ki asli taqat aur fundamentals yahan check karein:")
                        
                        # --- NEW FUNDAMENTAL METRICS ---
                        pb_ratio = info.get('priceToBook', None)
                        pb_val = float(pb_ratio) if pb_ratio and not pd.isna(pb_ratio) else None
                        pb_str = f"{pb_val:.2f}" if pb_val is not None else 'N/A'
                        
                        profit_margin = info.get('profitMargins', None)
                        pm_val = float(profit_margin) * 100 if profit_margin and not pd.isna(profit_margin) else None
                        pm_str = f"{pm_val:.2f}%" if pm_val is not None else 'N/A'
                        
                        eps = info.get('trailingEps', None)
                        eps_str = f"₹{float(eps):.2f}" if eps and not pd.isna(eps) else 'N/A'
                        
                        # --- INDICATOR SIGNALS ---
                        pe_ind = "🟢" if pe_val and pe_val < 25 else ("🟡" if pe_val and pe_val <= 40 else "🔴") if pe_val else "⚪"
                        roe_ind = "🟢" if roe_val and roe_val > 15 else ("🟡" if roe_val and roe_val >= 10 else "🔴") if roe_val else "⚪"
                        de_ind = "🟢" if de_val and de_val < 0.5 else ("🟡" if de_val and de_val <= 1.5 else "🔴") if de_val else "🟢"
                        div_ind = "🟢" if div_val and div_val > 1 else ("🟡" if div_val and div_val > 0 else "⚪") if div_val else "⚪"
                        pb_ind = "🟢" if pb_val and pb_val < 3 else ("🟡" if pb_val and pb_val <= 5 else "🔴") if pb_val else "⚪"
                        pm_ind = "🟢" if pm_val and pm_val > 10 else ("🟡" if pm_val and pm_val > 0 else "🔴") if pm_val else "⚪"

                        # --- MOBILE FRIENDLY 2x2 GRID ---
                        st.markdown("#### 📊 Core Fundamental Metrics")
                        m1, m2 = st.columns(2)
                        with m1:
                            st.metric("P/E Ratio (Valuation)", f"{pe_str}", pe_ind)
                            st.metric("Debt-to-Equity (Karza)", f"{de_str}", de_ind)
                            st.metric("Net Profit Margin", f"{pm_str}", pm_ind)
                        with m2:
                            st.metric("ROE (Return on Equity)", f"{roe_str}", roe_ind)
                            st.metric("P/B Ratio (Book Value)", f"{pb_str}", pb_ind)
                            st.metric("EPS (Earning Per Share)", f"{eps_str}", "🟢")
                            
                        st.markdown("---")
                        
                        # --- DETAILED CHECKLIST ---
                        st.markdown("### 📋 Long-Term Action Checklist:")
                        lt_score = 0
                        
                        if pe_val and pe_val < 25:
                            st.markdown(f"✅ **Valuation (P/E): {pe_str}** - Stock saste ya bilkul sahi daam par mil raha hai.")
                            lt_score += 1
                        elif pe_val:
                            st.markdown(f"⚠️ **Valuation (P/E): {pe_str}** - Stock thoda mehanga lag raha hai (Premium Valuation).")
                            
                        if roe_val and roe_val > 15:
                            st.markdown(f"✅ **Profitability (ROE): {roe_str}** - Company apne capital par behtareen munafa kama rahi hai (15%+).")
                            lt_score += 1
                        elif roe_val:
                            st.markdown(f"❌ **Profitability (ROE): {roe_str}** - Munafa kamane ki raftaar thodi dheemi hai.")
                            
                        if de_val and de_val < 0.5:
                            st.markdown(f"✅ **Financial Health (Debt): {de_str}** - Company par karza bahut kam ya na ke barabar hai. Safest zone!")
                            lt_score += 1
                        elif de_val:
                            st.markdown(f"⚠️ **Financial Health (Debt): {de_str}** - Company par karza zyada hai, jisse long-term risk badh sakta hai.")
                            
                        if pb_val and pb_val < 3:
                            st.markdown(f"✅ **Book Value (P/B): {pb_str}** - Price-to-Book ratio 3 se kam h