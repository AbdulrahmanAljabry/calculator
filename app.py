"""
حاسبة المتداول الاحترافية
Professional Trader Calculator
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="حاسبة المتداول الاحترافية",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS (minimal, for RTL support) ───────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .result-box {
        background: #1e2a3a;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #00c9a7;
    }
    .result-box.danger { border-left-color: #ff4b4b; }
    .result-box.warning { border-left-color: #ffa500; }
    .metric-label { font-size: 0.85rem; color: #aab4c4; margin-bottom: 2px; }
    .metric-value { font-size: 1.4rem; font-weight: 700; color: #ffffff; }
    .metric-value.good { color: #00c9a7; }
    .metric-value.bad  { color: #ff4b4b; }
    .section-header { font-size: 1.1rem; font-weight: 600; color: #cdd9e5; margin: 1rem 0 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.title("📈 حاسبة المتداول الاحترافية")
st.caption("أداة متكاملة لإدارة المخاطر · حساب حجم اللوت · خطة الربح التراكمي")

tab1, tab2, tab3 = st.tabs([
    "⚖️  إدارة المخاطر",
    "📦  حجم اللوت",
    "📊  خطة الربح التراكمي",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Risk-Reward Calculator
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("⚖️ حاسبة نسبة العائد للمخاطرة (Risk/Reward)")
    st.markdown("احسب نقاط الدخول · جني الأرباح · وقف الخسارة ونسبة R:R")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<p class="section-header">معطيات الصفقة</p>', unsafe_allow_html=True)

        direction = st.radio(
            "اتجاه الصفقة",
            ["شراء (Buy / Long)", "بيع (Sell / Short)"],
            horizontal=True,
        )
        is_long = direction.startswith("شراء")

        instrument_rr = st.selectbox(
            "نوع الأداة المالية",
            [
                "فوركس — زوج رئيسي (EUR/USD, GBP/USD ...)",
                "فوركس — زوج الين الياباني (USD/JPY ...)",
                "ذهب (XAU/USD)",
                "فضة (XAG/USD)",
                "مؤشرات (Indices)",
                "عملات رقمية (Crypto)",
                "أسهم (Stocks)",
            ],
            key="instrument_rr",
        )

        # Pip multiplier per instrument type
        pip_multiplier_map = {
            "فوركس — زوج رئيسي (EUR/USD, GBP/USD ...)":  10000,
            "فوركس — زوج الين الياباني (USD/JPY ...)":    100,
            "ذهب (XAU/USD)":                               10,
            "فضة (XAG/USD)":                               100,
            "مؤشرات (Indices)":                            1,
            "عملات رقمية (Crypto)":                        1,
            "أسهم (Stocks)":                               1,
        }
        pip_multiplier = pip_multiplier_map[instrument_rr]

        # Default prices per instrument
        price_defaults = {
            "فوركس — زوج رئيسي (EUR/USD, GBP/USD ...)":  (1.1000, 0.00001),
            "فوركس — زوج الين الياباني (USD/JPY ...)":    (150.000, 0.001),
            "ذهب (XAU/USD)":                               (2300.0, 0.1),
            "فضة (XAG/USD)":                               (28.00, 0.01),
            "مؤشرات (Indices)":                            (5000.0, 1.0),
            "عملات رقمية (Crypto)":                        (65000.0, 1.0),
            "أسهم (Stocks)":                               (100.0, 0.01),
        }
        default_price, default_step = price_defaults[instrument_rr]

        entry_price = st.number_input(
            "سعر الدخول",
            min_value=0.0001,
            value=default_price,
            step=default_step,
            format="%.4f" if pip_multiplier >= 1000 else "%.2f" if pip_multiplier >= 10 else "%.2f",
            help="السعر الذي ستدخل عنده الصفقة",
        )
        stop_loss = st.number_input(
            "وقف الخسارة (Stop Loss)",
            min_value=0.0001,
            value=round(entry_price * (0.9955 if is_long else 1.0045), 4),
            step=default_step,
            format="%.4f" if pip_multiplier >= 1000 else "%.2f",
            help="السعر الذي ستغلق عنده الصفقة خسارةً",
        )
        take_profit = st.number_input(
            "جني الأرباح (Take Profit)",
            min_value=0.0001,
            value=round(entry_price * (1.009 if is_long else 0.991), 4),
            step=default_step,
            format="%.4f" if pip_multiplier >= 1000 else "%.2f",
            help="السعر الذي ستغلق عنده الصفقة ربحاً",
        )
        pip_value_input = st.number_input(
            "قيمة النقطة (Pip Value) بالدولار — اختياري",
            min_value=0.0,
            value=10.0,
            step=0.01,
            format="%.2f",
            help="قيمة كل نقطة واحدة بالدولار (اتركها صفراً للتجاهل)",
        )

    with col2:
        st.markdown('<p class="section-header">النتائج</p>', unsafe_allow_html=True)

        # ── Validations ──────────────────────────────────────────────────────
        errors = []

        if is_long:
            if stop_loss >= entry_price:
                errors.append("⚠️ وقف الخسارة يجب أن يكون **أقل** من سعر الدخول في صفقة الشراء.")
            if take_profit <= entry_price:
                errors.append("⚠️ جني الأرباح يجب أن يكون **أعلى** من سعر الدخول في صفقة الشراء.")
        else:
            if stop_loss <= entry_price:
                errors.append("⚠️ وقف الخسارة يجب أن يكون **أعلى** من سعر الدخول في صفقة البيع.")
            if take_profit >= entry_price:
                errors.append("⚠️ جني الأرباح يجب أن يكون **أقل** من سعر الدخول في صفقة البيع.")

        for err in errors:
            st.warning(err)

        if not errors:
            # ── Calculations ─────────────────────────────────────────────────
            risk_points   = abs(entry_price - stop_loss)
            reward_points = abs(take_profit - entry_price)
            rr_ratio      = reward_points / risk_points if risk_points > 0 else 0

            # Convert to pips using the correct multiplier per instrument
            risk_pips   = round(risk_points * pip_multiplier, 1)
            reward_pips = round(reward_points * pip_multiplier, 1)

            # Monetary value (if pip value provided)
            risk_money   = risk_pips * pip_value_input if pip_value_input > 0 else None
            reward_money = reward_pips * pip_value_input if pip_value_input > 0 else None

            # ── Display ──────────────────────────────────────────────────────
            c1, c2, c3 = st.columns(3)
            c1.metric("نقاط المخاطرة", f"{risk_pips:g} نقطة")
            c2.metric("نقاط الربح",    f"{reward_pips:g} نقطة")
            rr_color = "good" if rr_ratio >= 2 else ("warning" if rr_ratio >= 1 else "bad")
            c3.metric("نسبة R:R",      f"1 : {rr_ratio:.2f}")

            if risk_money is not None:
                m1, m2 = st.columns(2)
                m1.metric("قيمة المخاطرة $", f"${risk_money:,.2f}")
                m2.metric("قيمة الربح $",    f"${reward_money:,.2f}")

            # ── RR Rating ────────────────────────────────────────────────────
            st.markdown("---")
            if rr_ratio >= 3:
                st.success(f"✅ نسبة ممتازة 1:{rr_ratio:.2f} — الصفقة ذات جدوى عالية جداً")
            elif rr_ratio >= 2:
                st.success(f"✅ نسبة جيدة 1:{rr_ratio:.2f} — الصفقة مقبولة ومنطقية")
            elif rr_ratio >= 1:
                st.warning(f"⚠️ نسبة متوسطة 1:{rr_ratio:.2f} — تأكد من ارتفاع نسبة الفوز")
            else:
                st.error(f"❌ نسبة ضعيفة 1:{rr_ratio:.2f} — يُنصح بعدم الدخول في هذه الصفقة")

            # ── Visual Chart ─────────────────────────────────────────────────
            st.markdown("---")
            fig = go.Figure()

            levels = {
                "وقف الخسارة": (stop_loss, "#ff4b4b"),
                "سعر الدخول":  (entry_price, "#ffffff"),
                "جني الأرباح": (take_profit, "#00c9a7"),
            }

            y_min = min(stop_loss, take_profit) * 0.9995
            y_max = max(stop_loss, take_profit) * 1.0005

            for label, (price, color) in levels.items():
                fig.add_hline(
                    y=price,
                    line_color=color,
                    line_width=2,
                    line_dash="dash" if label == "سعر الدخول" else "solid",
                    annotation_text=f"  {label}: {price:.5f}",
                    annotation_position="left",
                    annotation_font_color=color,
                )

            # Shaded risk/reward zones
            fig.add_hrect(
                y0=min(entry_price, stop_loss),
                y1=max(entry_price, stop_loss),
                fillcolor="rgba(255,75,75,0.15)",
                line_width=0,
            )
            fig.add_hrect(
                y0=min(entry_price, take_profit),
                y1=max(entry_price, take_profit),
                fillcolor="rgba(0,201,167,0.15)",
                line_width=0,
            )

            fig.update_layout(
                title=f"مستويات الصفقة — نسبة R:R = 1:{rr_ratio:.2f}",
                yaxis_title="السعر",
                xaxis=dict(showticklabels=False),
                height=320,
                paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117",
                font_color="#cdd9e5",
                margin=dict(l=80, r=20, t=40, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Lot Size Calculator
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📦 حاسبة حجم اللوت الأمثل")
    st.markdown("احسب حجم الصفقة المناسب بناءً على رأس المال ونسبة المخاطرة المقبولة")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<p class="section-header">بيانات الحساب والصفقة</p>', unsafe_allow_html=True)

        account_balance = st.number_input(
            "رأس المال ($)",
            min_value=1.0,
            value=10000.0,
            step=100.0,
            format="%.2f",
        )
        risk_percent = st.slider(
            "نسبة المخاطرة من رأس المال (%)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="يُنصح المحترفون بـ 1-2% كحد أقصى",
        )

        instrument_type = st.selectbox(
            "نوع الأداة المالية",
            [
                "فوركس — زوج رئيسي (مثل EUR/USD)",
                "فوركس — زوج ثانوي / غير مباشر",
                "ذهب (XAU/USD)",
                "مؤشرات (Indices)",
                "عملات رقمية (Crypto)",
                "أسهم (Stocks)",
                "مخصص",
            ],
        )

        # Dynamic pip value defaults per instrument
        pip_defaults = {
            "فوركس — زوج رئيسي (مثل EUR/USD)": (10.0, 0.0001, "لوت فوركس (100K وحدة)"),
            "فوركس — زوج ثانوي / غير مباشر":  (10.0, 0.0001, "لوت فوركس"),
            "ذهب (XAU/USD)":                   (1.0,  0.1,    "لوت ذهب"),
            "مؤشرات (Indices)":                (1.0,  1.0,    "عقد"),
            "عملات رقمية (Crypto)":             (1.0,  1.0,    "وحدة"),
            "أسهم (Stocks)":                    (0.01, 0.01,   "سهم"),
            "مخصص":                             (10.0, 0.0001, "وحدة"),
        }
        default_pip_val, default_pip_size, unit_label = pip_defaults[instrument_type]

        pip_value_per_lot = st.number_input(
            f"قيمة النقطة (Pip) لكل لوت ($)",
            min_value=0.0001,
            value=default_pip_val,
            step=0.01,
            format="%.4f",
            help="قيمة النقطة الواحدة لكل لوت كامل بالدولار",
        )
        stop_loss_pips = st.number_input(
            "المسافة إلى وقف الخسارة (نقطة / Pip)",
            min_value=0.1,
            value=50.0,
            step=0.5,
            format="%.1f",
        )

    with col2:
        st.markdown('<p class="section-header">النتائج</p>', unsafe_allow_html=True)

        # ── Calculations ─────────────────────────────────────────────────────
        risk_amount      = account_balance * (risk_percent / 100)
        lot_size         = risk_amount / (stop_loss_pips * pip_value_per_lot) if stop_loss_pips > 0 else 0

        # Standard lot breakdown
        standard_lots  = int(lot_size)
        mini_lots      = int((lot_size - standard_lots) * 10)
        micro_lots     = round((lot_size - standard_lots - mini_lots / 10) * 100, 1)

        # ── Display ──────────────────────────────────────────────────────────
        st.metric("مبلغ المخاطرة ($)", f"${risk_amount:,.2f}")
        st.metric(f"حجم اللوت المناسب ({unit_label})", f"{lot_size:.4f}")

        st.markdown("---")
        st.markdown("**تفصيل اللوت:**")
        d1, d2, d3 = st.columns(3)
        d1.metric("لوت كامل",  f"{standard_lots}")
        d2.metric("ميني لوت",  f"{mini_lots}")
        d3.metric("ميكرو لوت", f"{micro_lots}")

        # ── Risk Table at different % levels ─────────────────────────────────
        st.markdown("---")
        st.markdown("**جدول المقارنة — نسب المخاطرة المختلفة**")
        rows = []
        for pct in [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
            r_amt   = account_balance * (pct / 100)
            ls      = r_amt / (stop_loss_pips * pip_value_per_lot) if stop_loss_pips > 0 else 0
            rows.append({
                "نسبة المخاطرة %": f"{pct}%",
                "مبلغ المخاطرة $": f"${r_amt:,.2f}",
                "حجم اللوت":       f"{ls:.4f}",
                "التوصية":         (
                    "✅ موصى به" if pct <= 2 else
                    "⚠️ محفوف بمخاطر" if pct <= 3 else
                    "❌ خطر جداً"
                ),
            })
        df = pd.DataFrame(rows)
        # Highlight current selection
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Risk meter visual
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_percent,
            number={"suffix": "%", "font": {"size": 32}},
            title={"text": "مستوى المخاطرة", "font": {"size": 14, "color": "#cdd9e5"}},
            gauge={
                "axis":  {"range": [0, 10], "tickcolor": "#cdd9e5"},
                "bar":   {"color": "#00c9a7" if risk_percent <= 2 else "#ffa500" if risk_percent <= 3 else "#ff4b4b"},
                "steps": [
                    {"range": [0, 2],  "color": "rgba(0,201,167,0.15)"},
                    {"range": [2, 3],  "color": "rgba(255,165,0,0.15)"},
                    {"range": [3, 10], "color": "rgba(255,75,75,0.15)"},
                ],
                "threshold": {
                    "line":  {"color": "#ff4b4b", "width": 3},
                    "thickness": 0.75,
                    "value": 3,
                },
            },
        ))
        fig2.update_layout(
            height=220,
            paper_bgcolor="#0e1117",
            font_color="#cdd9e5",
            margin=dict(l=20, r=20, t=30, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Cumulative Profit Plan
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📊 خطة الربح التراكمي")
    st.markdown("حدد هدفك المالي واكتشف المسار اليومي للوصول إليه")

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown('<p class="section-header">إعدادات الخطة</p>', unsafe_allow_html=True)

        initial_capital = st.number_input(
            "رأس المال الابتدائي ($)",
            min_value=100.0,
            value=5000.0,
            step=100.0,
            format="%.2f",
        )
        target_capital = st.number_input(
            "رأس المال المستهدف ($)",
            min_value=initial_capital + 1,
            value=10000.0,
            step=500.0,
            format="%.2f",
        )
        trading_days = st.slider(
            "عدد أيام التداول",
            min_value=5,
            max_value=365,
            value=30,
            step=1,
            help="عدد الأيام لتحقيق الهدف",
        )
        daily_trades = st.number_input(
            "متوسط عدد الصفقات يومياً",
            min_value=1,
            max_value=20,
            value=2,
            step=1,
        )
        rr_plan = st.selectbox(
            "نسبة العائد للمخاطرة المستهدفة",
            ["1:1", "1:1.5", "1:2", "1:2.5", "1:3"],
            index=2,
        )
        win_rate = st.slider(
            "معدل الفوز المتوقع (%)",
            min_value=30,
            max_value=80,
            value=55,
            step=1,
        )

    with col2:
        # ── Calculations ─────────────────────────────────────────────────────
        total_profit_needed = target_capital - initial_capital
        total_growth_pct    = (total_profit_needed / initial_capital) * 100

        # Daily compounded growth rate
        daily_growth_rate   = (target_capital / initial_capital) ** (1 / trading_days) - 1
        daily_profit_pct    = daily_growth_rate * 100

        # Required risk per trade (based on R:R and win rate)
        rr_value = float(rr_plan.split(":")[1])
        win_rate_dec = win_rate / 100

        # Expected value factor per trade
        ev_per_trade = (win_rate_dec * rr_value) - ((1 - win_rate_dec) * 1)
        # Daily gain from all trades
        if daily_trades > 0 and ev_per_trade > 0:
            risk_per_trade_pct = (daily_profit_pct / daily_trades) / ev_per_trade
        else:
            risk_per_trade_pct = 0

        # ── Key Metrics ───────────────────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("إجمالي الربح المطلوب",  f"${total_profit_needed:,.0f}")
        m2.metric("نمو رأس المال",          f"{total_growth_pct:.1f}%")
        m3.metric("الربح اليومي المطلوب %", f"{daily_profit_pct:.2f}%")
        m4.metric("نسبة مخاطرة / صفقة",    f"{risk_per_trade_pct:.2f}%")

        # EV feedback
        if ev_per_trade > 0:
            st.success(f"✅ القيمة المتوقعة لكل وحدة مخاطرة: **{ev_per_trade:.2f}R** — الخطة قابلة للتحقيق رياضياً")
        else:
            st.error("❌ القيمة المتوقعة سلبية — راجع نسبة الفوز أو نسبة R:R")

        # Recommended risk per trade feedback
        if risk_per_trade_pct <= 1:
            st.info(f"✅ المخاطرة الموصى بها لكل صفقة: **{risk_per_trade_pct:.2f}%** — آمنة جداً")
        elif risk_per_trade_pct <= 2:
            st.info(f"✅ المخاطرة الموصى بها لكل صفقة: **{risk_per_trade_pct:.2f}%** — مناسبة")
        elif risk_per_trade_pct <= 3:
            st.warning(f"⚠️ المخاطرة الموصى بها لكل صفقة: **{risk_per_trade_pct:.2f}%** — تحتاج انضباطاً عالياً")
        else:
            st.error(f"❌ المخاطرة الموصى بها لكل صفقة: **{risk_per_trade_pct:.2f}%** — مرتفعة جداً، مدد الأيام")

        st.markdown("---")

        # ── Build cumulative profit table ─────────────────────────────────────
        days_list    = list(range(0, trading_days + 1))
        capital_list = [initial_capital * ((1 + daily_growth_rate) ** d) for d in days_list]
        profit_list  = [c - initial_capital for c in capital_list]

        # ── Plotly chart ─────────────────────────────────────────────────────
        fig3 = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.65, 0.35],
            vertical_spacing=0.06,
            subplot_titles=["رأس المال التراكمي ($)", "الربح اليومي ($)"],
        )

        # Capital curve with gradient fill
        fig3.add_trace(go.Scatter(
            x=days_list,
            y=capital_list,
            mode="lines",
            name="رأس المال",
            line=dict(color="#00c9a7", width=2.5),
            fill="tonexty",
            fillcolor="rgba(0,201,167,0.08)",
        ), row=1, col=1)

        # Target line
        fig3.add_hline(
            y=target_capital,
            line_dash="dot",
            line_color="#ffa500",
            annotation_text=f"  الهدف: ${target_capital:,.0f}",
            annotation_font_color="#ffa500",
            row=1, col=1,
        )

        # Daily profit bars
        daily_profits = [capital_list[i] - capital_list[i - 1] if i > 0 else 0 for i in range(len(capital_list))]
        fig3.add_trace(go.Bar(
            x=days_list,
            y=daily_profits,
            name="الربح اليومي",
            marker_color=[
                f"rgba(0,201,167,{0.4 + 0.6 * (i / trading_days)})" for i in range(len(days_list))
            ],
        ), row=2, col=1)

        fig3.update_layout(
            height=460,
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            font_color="#cdd9e5",
            showlegend=False,
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis2_title="اليوم",
        )
        fig3.update_xaxes(gridcolor="#1e2a3a", zerolinecolor="#1e2a3a")
        fig3.update_yaxes(gridcolor="#1e2a3a", zerolinecolor="#1e2a3a")
        st.plotly_chart(fig3, use_container_width=True)

        # ── Full day-by-day table ─────────────────────────────────────────────
        st.markdown("### 📋 الخطة التفصيلية — يوماً بيوم")

        full_data = []
        for d in range(0, trading_days + 1):
            cap        = capital_list[d]
            cum_profit = cap - initial_capital
            daily_gain = daily_profits[d]
            prev_cap   = capital_list[d - 1] if d > 0 else cap
            max_loss   = daily_gain if d > 0 else 0.0
            per_trade  = daily_gain / daily_trades if daily_trades > 0 else 0.0

            full_data.append({
                "اليوم":                               d,
                "رأس المال ($)":                       round(cap, 2),
                "الربح اليومي ($)":                    round(daily_gain, 2),
                "الربح التراكمي ($)":                  round(cum_profit, 2),
                "الحد الأقصى للخسارة ($)":            round(max_loss, 2),
                "رأس المال بعد الستوب ($)":            round(prev_cap, 2),
                f"متوسط الربح / صفقة ({daily_trades} صفقات)": round(per_trade, 2),
            })

        df_full = pd.DataFrame(full_data)
        st.dataframe(
            df_full,
            use_container_width=True,
            hide_index=True,
            height=min(600, (trading_days + 2) * 35 + 38),
        )

        st.caption(
            "📌 القاعدة: الحد الأقصى للخسارة اليومية = ربح ذلك اليوم المستهدف. "
            "في أسوأ الأحوال يعود رأس مالك لنفس رقم اليوم السابق. "
            f"متوسط الربح / صفقة = الربح اليومي ÷ {daily_trades} صفقات."
        )

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "⚠️ تنبيه: هذه الحاسبة لأغراض تعليمية وتحليلية فقط. التداول ينطوي على مخاطر. "
    "لا تستثمر أكثر مما تتحمل خسارته."
)
st.markdown(
    """
    <div style="text-align: center; padding: 1.5rem 0 0.5rem; color: #7a8a9a; font-size: 0.88rem; line-height: 1.8;">
        تم برمجة هذه الصفحة من خلال <strong style="color: #00c9a7;">"عبد الرحمن الجابري"</strong> لأهداف تعليمية فقط
        <br>
        جميع الحقوق محفوظة WMC Group LLC © 2026 — لا يُسمح بإعادة النشر أو الاستخدام التجاري دون إذن مسبق
    </div>
    """,
    unsafe_allow_html=True,
)
