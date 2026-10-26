import html
import pandas as pd
import streamlit as st

from database import get_existing_problems


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Explore Problems | CivicConnect",
    page_icon="🔎",
    layout="wide",
)


# --------------------------------------------------
# 2. CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #f7f8fc;
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #252641;
    letter-spacing: -0.5px;
}

[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid #ececf4;
}

.explore-hero {
    background: linear-gradient(115deg, #4f35c9, #8063ed);
    padding: 34px;
    border-radius: 22px;
    margin: 10px 0 25px 0;
    box-shadow: 0 10px 28px rgba(79,53,201,0.15);
}

.explore-hero h1 {
    color: white !important;
    font-size: 34px;
    margin: 14px 0;
}

.explore-hero p {
    color: #f0edff;
    font-size: 15px;
    line-height: 1.8;
    max-width: 700px;
}

.page-tag {
    display: inline-block;
    background: rgba(255,255,255,0.17);
    color: white;
    padding: 7px 12px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 700;
}

.problem-card {
    background: white;
    border: 1px solid #e9eaf3;
    border-radius: 18px;
    padding: 22px;
    margin: 14px 0;
    box-shadow: 0 5px 18px rgba(35,35,70,0.035);
}

.problem-title {
    font-size: 19px;
    font-weight: 800;
    color: #292a45;
    margin: 14px 0 9px 0;
    overflow-wrap: anywhere;
}

.meta {
    color: #777b91;
    font-size: 13px;
    line-height: 1.9;
}

.problem-description {
    color: #656980;
    font-size: 14px;
    line-height: 1.8;
    margin-top: 12px;
    overflow-wrap: anywhere;
}

.pill {
    display: inline-block;
    background: #f0edff;
    color: #5942c3;
    padding: 6px 10px;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 800;
    margin: 0 5px 5px 0;
}

.high {
    background: #fff0f0;
    color: #bf3846;
}

.medium {
    background: #fff4dd;
    color: #976000;
}

.low {
    background: #e8f8ef;
    color: #26734d;
}

.section-caption {
    color: #777b91;
    font-size: 14px;
}

div.stButton > button {
    border-radius: 11px;
    font-weight: 700;
    min-height: 42px;
}

div[data-testid="stExpander"] {
    background: white;
    border-radius: 12px;
    border: 1px solid #e9eaf3;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. HELPER FUNCTIONS
# --------------------------------------------------

def clean(value, fallback="Not provided"):
    """Safely convert database values into readable text."""
    if value is None:
        return fallback

    try:
        if pd.isna(value):
            return fallback
    except (TypeError, ValueError):
        pass

    value = str(value).strip()

    if not value or value.lower() in {"nan", "none"}:
        return fallback

    return value


def safe(value, fallback="Not provided"):
    """Escape text before placing it inside custom HTML."""
    return html.escape(clean(value, fallback))


# --------------------------------------------------
# 4. SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## CivicConnect")
    st.caption("COMMUNITY • CONNECTION • CHANGE")
    st.divider()

    st.markdown("### Explore Problems")
    st.write("Discover and explore community challenges.")

    if st.button("➕ Report a Problem", use_container_width=True):
        st.switch_page("app.py")


# --------------------------------------------------
# 5. HERO SECTION
# --------------------------------------------------

st.markdown("""
<div class="explore-hero">
    <span class="page-tag"> DISCOVER PROBLEMS</span>
    <h1>Find problems here!!</h1>
    
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 6. LOAD DATABASE RECORDS
# --------------------------------------------------

st.subheader("Discover community problems")

try:
    records = get_existing_problems()
    df = pd.DataFrame(records)

except Exception:
    st.error("Unable to load community reports from Supabase.")
    st.info("Check your internet connection and make sure your Supabase project is active.")

    with st.expander("Show technical details"):
        st.exception(Exception("Database request failed. Check the terminal for the original error."))

    st.stop()


if df.empty:
    st.info(
        "No community reports are available yet. "
        "Submit the first report to get started!"
    )

    if st.button("➕ Report a Problem", type="primary"):
        st.switch_page("app.py")

    st.stop()


# --------------------------------------------------
# 7. PREPARE DATABASE DATA
# --------------------------------------------------

required_columns = [
    "title",
    "description",
    "location",
    "category",
    "priority",
    "status",
]

for column in required_columns:
    if column not in df.columns:
        df[column] = None

for column in required_columns:
    df[column] = df[column].apply(clean)

# Work with a copy so the original database results stay untouched.
df = df.copy()


# --------------------------------------------------
# 8. SEARCH AND FILTERS
# --------------------------------------------------

st.markdown("### Find the report")
st.markdown(
    '<div class="section-caption">'
    'Search by keyword or narrow the results using the filters below.'
    '</div>',
    unsafe_allow_html=True,
)

search = st.text_input(
    "Search community reports",
    placeholder="Type here",
)

f1, f2, f3, f4 = st.columns(4)

with f1:
    categories = sorted(df["category"].unique().tolist())

    selected_category = st.selectbox(
        "Category",
        ["All categories"] + categories,
    )

with f2:
    locations = sorted(df["location"].unique().tolist())

    selected_location = st.selectbox(
        "Location",
        ["All locations"] + locations,
    )

with f3:
    priorities = sorted(df["priority"].unique().tolist())

    selected_priority = st.selectbox(
        "Priority",
        ["All priorities"] + priorities,
    )

with f4:
    statuses = sorted(df["status"].unique().tolist())

    selected_status = st.selectbox(
        "Status",
        ["All statuses"] + statuses,
    )


sort_order = st.selectbox(
    "Sort reports",
    [
        "Newest first",
        "Title A–Z",
        "Priority: High to Low",
    ],
)


# --------------------------------------------------
# 9. APPLY FILTERS
# --------------------------------------------------

filtered = df.copy()

if search.strip():
    search_columns = [
        "title",
        "description",
        "location",
        "category",
        "priority",
        "status",
    ]

    searchable = (
        filtered[search_columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    )

    filtered = filtered[
        searchable.str.contains(
            search.strip(),
            case=False,
            na=False,
            regex=False,
        )
    ]

if selected_category != "All categories":
    filtered = filtered[
        filtered["category"] == selected_category
    ]

if selected_location != "All locations":
    filtered = filtered[
        filtered["location"] == selected_location
    ]

if selected_priority != "All priorities":
    filtered = filtered[
        filtered["priority"] == selected_priority
    ]

if selected_status != "All statuses":
    filtered = filtered[
        filtered["status"] == selected_status
    ]


# --------------------------------------------------
# 10. SORT RESULTS
# --------------------------------------------------

priority_rank = {
    "critical": 0,
    "urgent": 1,
    "high": 2,
    "medium": 3,
    "moderate": 3,
    "normal": 4,
    "low": 5,
}

if sort_order == "Title A–Z":
    filtered = filtered.sort_values(
        "title",
        key=lambda series: series.str.lower(),
    )

elif sort_order == "Priority: High to Low":
    filtered = filtered.copy()

    filtered["_priority_order"] = (
        filtered["priority"]
        .str.lower()
        .map(priority_rank)
        .fillna(6)
    )

    filtered = (
        filtered.sort_values("_priority_order")
        .drop(columns="_priority_order")
    )

elif sort_order == "Newest first":
    if "created_at" in filtered.columns:
        filtered = filtered.sort_values(
            "created_at",
            ascending=False,
            na_position="last",
        )
    elif "id" in filtered.columns:
        filtered = filtered.sort_values(
            "id",
            ascending=False,
        )


# --------------------------------------------------
# 11. RESULTS SUMMARY
# --------------------------------------------------

st.divider()

summary_col, metric_col = st.columns([3, 1])

with summary_col:
    st.markdown("### Community reports")
    st.caption("Browse reports submitted by community members.")

with metric_col:
    st.metric(
        "Matching reports",
        len(filtered),
    )


# --------------------------------------------------
# 12. DISPLAY STYLED PROBLEM CARDS
# --------------------------------------------------

if filtered.empty:
    st.warning(
        "No reports match your current search. "
        "Try changing your filters."
    )

else:
    for index, (_, row) in enumerate(filtered.iterrows()):

        title = safe(row["title"], "Untitled problem")
        description = safe(row["description"])
        category = safe(row["category"])
        location = safe(row["location"])

        priority = clean(row["priority"], "Unknown")
        status = clean(row["status"], "Submitted")

        priority_key = priority.lower()

        if priority_key in ["critical", "urgent", "high"]:
            priority_class = "high"

        elif priority_key in ["medium", "moderate"]:
            priority_class = "medium"

        else:
            priority_class = "low"

        # Render the HTML card.
        st.markdown(
            
            
            
            """
            <div class="problem-title">📍 Lack of clean drinking water</div>
            <div class="meta">Location: Kanchipuram, Tamil Nadu</div>
            <div class="problem-description">
                Residents in our village are facing a shortage of clean drinking water.
            </div>
            """,
            unsafe_allow_html=True

        )

        # Expandable report details.
        with st.expander(
            f"View details — {clean(row['title'], 'Problem')}"
        ):
            st.write("**Full description**")
            st.write(clean(row["description"]))

            st.write("**Category:**", clean(row["category"]))
            st.write("**Location:**", clean(row["location"]))
            st.write("**Priority:**", clean(row["priority"]))
            st.write("**Status:**", clean(row["status"]))

            if "summary" in df.columns:
                summary = clean(row.get("summary"), "")

                if summary:
                    st.write("**AI summary**")
                    st.write(summary)

            if "keywords" in df.columns:
                keywords = row.get("keywords")

                if isinstance(keywords, list):
                    st.write(
                        "**Keywords:**",
                        ", ".join(str(word) for word in keywords),
                    )

                else:
                    keywords_text = clean(keywords, "")

                    if keywords_text:
                        st.write("**Keywords:**", keywords_text)


# --------------------------------------------------
# 13. FOOTER AND REFRESH
# --------------------------------------------------

st.divider()

footer_col, refresh_col = st.columns([3, 1])

with footer_col:
    st.caption(
        "CivicConnect — Every community challenge deserves attention."
    )

with refresh_col:
    if st.button("🔄 Refresh reports", use_container_width=True):
        st.rerun()