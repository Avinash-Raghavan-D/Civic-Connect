
import html

import pandas as pd
import streamlit as st

from database import get_existing_problems


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="CivicConnect | Home",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- DESIGN SYSTEM ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #f7f8fc;
}

[data-testid="stHeader"] {
    background: rgba(247,248,252,0.92);
}

.block-container {
    max-width: 1450px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #ececf4;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #52546b;
}

h1, h2, h3 {
    color: #20213a;
    letter-spacing: -0.6px;
}

h1 {
    font-weight: 800;
}

.small-muted {
    color: #777b91;
    font-size: 14px;
}

.hero {
    background: linear-gradient(115deg, #4f35c9 0%, #7454e8 60%, #9575ff 100%);
    border-radius: 24px;
    padding: 34px 36px;
    color: white;
    position: relative;
    overflow: hidden;
    margin: 8px 0 28px 0;
    box-shadow: 0 12px 30px rgba(92,65,200,0.18);
}

.hero h1 {
    color: white !important;
    font-size: 36px;
    line-height: 1.2;
    margin: 8px 0 12px 0;
}

.hero p {
    color: #f0edff;
    font-size: 15px;
    max-width: 580px;
    line-height: 1.7;
}

.hero-tag {
    display: inline-block;
    background: rgba(255,255,255,0.16);
    color: white;
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 100px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 700;
}

.hero-art {
    font-size: 90px;
    text-align: center;
    opacity: 0.96;
}

.section-heading {
    font-size: 23px;
    font-weight: 800;
    color: #252641;
    margin: 25px 0 4px 0;
}

.section-subtitle {
    color: #81849a;
    font-size: 14px;
    margin-bottom: 18px;
}

.stat-card {
    background: white;
    border: 1px solid #ececf5;
    border-radius: 18px;
    padding: 21px;
    min-height: 135px;
    box-shadow: 0 5px 18px rgba(34,35,75,0.035);
}

.stat-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stat-icon {
    font-size: 25px;
    background: #f1edff;
    border-radius: 12px;
    padding: 8px;
}

.stat-label {
    color: #777b91;
    font-size: 13px;
    font-weight: 600;
    margin-top: 13px;
}

.stat-value {
    color: #252641;
    font-size: 31px;
    font-weight: 800;
    margin-top: 2px;
}

.category-card {
    background: white;
    border: 1px solid #ececf5;
    border-radius: 17px;
    padding: 18px 10px;
    text-align: center;
    min-height: 115px;
    box-shadow: 0 4px 15px rgba(34,35,75,0.025);
}

.category-icon {
    font-size: 29px;
    margin-bottom: 8px;
}

.category-name {
    font-size: 13px;
    color: #353650;
    font-weight: 700;
}

.problem-card {
    background: white;
    border: 1px solid #ececf5;
    border-radius: 17px;
    padding: 18px;
    margin-bottom: 12px;
    box-shadow: 0 4px 15px rgba(34,35,75,0.025);
}

.problem-title {
    color: #262741;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 8px;
}

.problem-meta {
    color: #777b91;
    font-size: 12px;
    line-height: 1.9;
}

.priority-high {
    color: #c43b45;
    background: #fff0f0;
    border-radius: 20px;
    padding: 5px 9px;
    font-size: 11px;
    font-weight: 800;
}

.priority-medium {
    color: #a56400;
    background: #fff5df;
    border-radius: 20px;
    padding: 5px 9px;
    font-size: 11px;
    font-weight: 800;
}

.priority-normal {
    color: #26734d;
    background: #e9f8ef;
    border-radius: 20px;
    padding: 5px 9px;
    font-size: 11px;
    font-weight: 800;
}

.status-pill {
    color: #5942c3;
    background: #f0edff;
    border-radius: 20px;
    padding: 5px 9px;
    font-size: 11px;
    font-weight: 700;
}

div.stButton > button {
    border-radius: 11px;
    font-weight: 700;
    min-height: 42px;
    border: 1px solid #e6e2fa;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    border-color: #7052df;
    color: #5c43c9;
    transform: translateY(-1px);
}

hr {
    border-color: #e9eaf2;
}

@media (max-width: 768px) {
    .hero {
        padding: 24px 20px;
    }
    .hero h1 {
        font-size: 28px;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------------- HELPERS ----------------

def safe_text(value, fallback="Not provided"):
    if pd.isna(value) or str(value).strip() == "":
        return fallback
    return html.escape(str(value))


def normalize(value, fallback="Unknown"):
    if pd.isna(value) or str(value).strip() == "":
        return fallback
    return str(value).strip()


def show_stat(label, value, icon, accent):
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-top">
            <div class="stat-icon">{icon}</div>
            <div style="color:{accent};font-size:12px;font-weight:700;">
                LIVE DATA
            </div>
        </div>
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value:,}</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## 🌍 CivicConnect")
    st.caption("COMMUNITY • CONNECTION • CHANGE")
    st.divider()

    st.markdown("### 🏠 Home Dashboard")
    st.markdown("Discover problems and follow community progress.")

    if st.button("➕ Report a Problem", use_container_width=True):
        st.switch_page("app.py")

    st.divider()
    st.markdown("**Your community, your voice.**")
    st.caption("Every report can help start a solution.")


# ---------------- HERO ----------------

hero_left, hero_right = st.columns([3, 1])

with hero_left:
    st.markdown("""
    <div class="hero">
        <span class="hero-tag">🌱 YOUR COMMUNITY, BETTER</span>
        <h1>Small reports.<br>Big changes.</h1>
        <p>
            Discover local challenges, bring attention to important issues,
            and connect communities with people who can help solve them.
        </p>
    </div>
    """, unsafe_allow_html=True)

with hero_right:
    st.markdown("""
    <div class="hero" style="height: 230px; display:flex;
         flex-direction:column; justify-content:center;">
        <div class="hero-art">🌍</div>
        <div style="text-align:center;font-size:13px;color:#f0edff;">
            Together, we make a difference
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------- LOAD DATABASE ----------------

st.markdown('<div class="section-heading">Your community at a glance</div>',
            unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">A snapshot of reported problems and their progress.</div>',
            unsafe_allow_html=True)

try:
    problems = get_existing_problems()
    df = pd.DataFrame(problems)
except Exception as e:
    st.error("We couldn't load the latest community data.")
    st.caption("Check your Supabase connection and try refreshing.")
    with st.expander("Technical details"):
        st.exception(e)
    st.stop()


if df.empty:
    st.info("Your community dashboard is ready! Submit the first problem to start tracking progress.")

    cols = st.columns(4)
    with cols[0]:
        show_stat("Total reports", 0, "📋", "#7253df")
    with cols[1]:
        show_stat("Awaiting review", 0, "⏳", "#df9a24")
    with cols[2]:
        show_stat("In progress", 0, "🛠️", "#3786d8")
    with cols[3]:
        show_stat("Resolved", 0, "✅", "#279b6b")

    if st.button("➕ Submit the first report", type="primary"):
        st.switch_page("app.py")

    st.stop()


# Prepare missing values
for col in ["title", "description", "category", "location",
            "priority", "status"]:
    if col not in df.columns:
        df[col] = "Unknown"
    df[col] = df[col].apply(normalize)

total = len(df)

pending = df["status"].isin(
    ["Submitted", "Under Review"]
).sum()

in_progress = df["status"].isin(
    ["Assigned", "In Progress"]
).sum()

resolved = (df["status"] == "Resolved").sum()


# ---------------- STAT CARDS ----------------

c1, c2, c3, c4 = st.columns(4)

with c1:
    show_stat("Total reports", int(total), "📋", "#7253df")
with c2:
    show_stat("Awaiting review", int(pending), "⏳", "#df9a24")
with c3:
    show_stat("In progress", int(in_progress), "🛠️", "#3786d8")
with c4:
    show_stat("Resolved", int(resolved), "✅", "#279b6b")


# ---------------- CATEGORY DISCOVERY ----------------

st.markdown('<div class="section-heading">Explore by category</div>',
            unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Find the issues that matter to your neighbourhood.</div>',
            unsafe_allow_html=True)

category_icons = {
    "Water Management": "💧",
    "Drinking Water Supply": "🚰",
    "Roads & Transport": "🛣️",
    "Road Infrastructure": "🚧",
    "Waste Management": "♻️",
    "Electricity": "💡",
    "Healthcare": "🏥",
    "Education": "📚",
    "Environment": "🌳",
    "Sanitation": "🧹",
}

categories = df["category"].value_counts().head(5).index.tolist()

if categories:
    category_cols = st.columns(5)
    for i, category in enumerate(categories):
        icon = category_icons.get(category, "📍")
        count = int((df["category"] == category).sum())
        with category_cols[i]:
            st.markdown(f"""
            <div class="category-card">
                <div class="category-icon">{icon}</div>
                <div class="category-name">{html.escape(category)}</div>
                <div style="font-size:12px;color:#898ba0;margin-top:5px;">
                    {count} report(s)
                </div>
            </div>
            """, unsafe_allow_html=True)


# ---------------- SEARCH & FILTERS ----------------

st.markdown('<div class="section-heading">Explore community reports</div>',
            unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Search reports and filter by what you want to see.</div>',
            unsafe_allow_html=True)

search_col, category_col, status_col = st.columns([2, 1, 1])

with search_col:
    search_term = st.text_input(
        "🔎 Search",
        placeholder="Search by title, description or location..."
    )

with category_col:
    category_filter = st.selectbox(
        "Category",
        ["All categories"] + sorted(df["category"].unique().tolist())
    )

with status_col:
    status_filter = st.selectbox(
        "Status",
        ["All statuses"] + sorted(df["status"].unique().tolist())
    )


filtered = df.copy()

if search_term.strip():
    searchable = (
        filtered["title"] + " " +
        filtered["description"] + " " +
        filtered["location"]
    ).str.lower()
    filtered = filtered[
        searchable.str.contains(search_term.strip().lower(), na=False)
    ]

if category_filter != "All categories":
    filtered = filtered[filtered["category"] == category_filter]

if status_filter != "All statuses":
    filtered = filtered[filtered["status"] == status_filter]


# ---------------- REPORT CARDS ----------------

st.caption(f"Showing {len(filtered)} of {total} reports")

if filtered.empty:
    st.info("No reports match these filters. Try another search or category.")
else:
    for _, row in filtered.head(15).iterrows():
        title = safe_text(row["title"], "Untitled report")
        description = safe_text(row["description"], "No description available")
        category = safe_text(row["category"], "Unknown")
        location = safe_text(row["location"], "Unknown")
        priority = normalize(row["priority"], "Unknown")
        status = normalize(row["status"], "Submitted")

        priority_lower = priority.lower()

        if priority_lower in ["high", "critical", "urgent"]:
            priority_class = "priority-high"
        elif priority_lower in ["medium", "moderate"]:
            priority_class = "priority-medium"
        else:
            priority_class = "priority-normal"

        st.markdown(f"""
        <div class="problem-card">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;gap:12px;flex-wrap:wrap;">
                <div style="flex:1;min-width:200px;">
                    <div class="problem-title">{title}</div>
                    <div class="problem-meta">
                        📍 {location}<br>
                        🗂️ {category}
                    </div>
                </div>
                <div style="display:flex;gap:7px;flex-wrap:wrap;">
                    <span class="{priority_class}">
                        {html.escape(priority.upper())} PRIORITY
                    </span>
                    <span class="status-pill">
                        {html.escape(status)}
                    </span>
                </div>
            </div>
            <div style="color:#666a80;font-size:13px;line-height:1.6;
                        margin-top:12px;">
                {description[:240]}{"..." if len(description) > 240 else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if len(filtered) > 15:
        st.caption("Showing the first 15 matching reports. Use search and filters to narrow the results.")


# ---------------- ANALYTICS ----------------

st.markdown('<div class="section-heading">Community insights</div>',
            unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Understand where reports are coming from and what needs attention.</div>',
            unsafe_allow_html=True)

chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown("#### Reports by category")
    category_counts = (
        df["category"].value_counts().head(8)
        .rename_axis("Category")
        .reset_index(name="Reports")
    )
    st.bar_chart(category_counts, x="Category", y="Reports")

with chart_right:
    st.markdown("#### Reports by status")
    status_counts = (
        df["status"].value_counts()
        .rename_axis("Status")
        .reset_index(name="Reports")
    )
    st.bar_chart(status_counts, x="Status", y="Reports")


# ---------------- FOOTER ----------------

st.divider()
footer_left, footer_right = st.columns([3, 1])

with footer_left:
    st.caption("🌍 CivicConnect — Connecting community problems with people who can help.")

with footer_right:
    if st.button("🔄 Refresh dashboard", use_container_width=True):
        st.rerun()
