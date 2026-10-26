
import streamlit as st
import html
import pandas as pd

from database import (
    get_universities,
    get_existing_problems,
    save_recommendation,
    update_problem_status,
)

st.set_page_config(
    page_title="University Portal | CivicConnect",
    page_icon="🎓",
    layout="wide",
)

# ---------------- PAGE DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: #F7F6FC;
}
.hero {
    background: linear-gradient(120deg, #5632A8, #8664D8);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    color: white;
    margin: 0;
    font-size: 32px;
}
.hero p {
    color: #EEE8FF;
    margin-bottom: 0;
}
.metric-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #E8E2F5;
    margin-bottom: 10px;
}
.metric-number {
    font-size: 28px;
    font-weight: 700;
    color: #633CB5;
}
.metric-label {
    color: #6D6878;
    font-size: 14px;
}
.problem-card {
    background: white;
    border: 1px solid #E7E1F2;
    border-radius: 14px;
    padding: 20px;
    margin: 10px 0;
}
.tag {
    display: inline-block;
    background: #EEE7FF;
    color: #6038B5;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 12px;
    margin: 3px 4px 3px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🎓 University Portal</h1>
    <p>Discover societal challenges, connect your expertise,
    and track your university's impact.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- LOAD DATABASE ----------------
@st.cache_data(ttl=30)
def load_portal_data():
    universities = get_universities()
    problems = get_existing_problems()
    return universities, problems


try:
    universities, problems = load_portal_data()
except Exception as error:
    st.error("Unable to load portal data from Supabase.")
    st.exception(error)
    st.stop()


if not universities:
    st.warning(
        "No universities were found. Add university records "
        "to your Supabase universities table first."
    )
    st.stop()

if not problems:
    st.info("No societal problems have been submitted yet.")
    st.stop()


university_df = pd.DataFrame(universities)
problem_df = pd.DataFrame(problems)

# Ensure optional fields exist for display
for column in [
    "title", "description", "location", "category",
    "subcategory", "priority", "status", "summary",
    "keywords", "is_duplicate"
]:
    if column not in problem_df.columns:
        problem_df[column] = ""

for column in ["name", "location", "departments", "expertise"]:
    if column not in university_df.columns:
        university_df[column] = ""


# ---------------- SELECT UNIVERSITY ----------------
st.subheader("🏫 Select University")

university_options = {
    f"{row['name']} — {row['location'] or 'Location not specified'}":
    row["id"]
    for _, row in university_df.iterrows()
}

selected_university_label = st.selectbox(
    "Choose the university using this portal",
    list(university_options.keys()),
)

university_id = university_options[selected_university_label]

selected_university = university_df[
    university_df["id"] == university_id
].iloc[0]

university_name = str(selected_university["name"])
university_location = str(selected_university["location"] or "Not specified")
departments = str(selected_university["departments"] or "Not specified")
expertise = str(selected_university["expertise"] or "Not specified")


# ---------------- UNIVERSITY PROFILE ----------------
st.subheader("🏛️ University Profile")

profile_col, expertise_col = st.columns(2)

with profile_col:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f"### {html.escape(university_name)}")
    st.write(f"📍 **Location:** {university_location}")
    st.write(f"🏢 **Departments:** {departments}")
    st.markdown("</div>", unsafe_allow_html=True)

with expertise_col:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 🔬 Areas of Expertise")
    st.write(expertise)
    st.caption(
        "Keep the university's departments and expertise updated "
        "in the universities table to improve matching."
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------- FILTER PROBLEMS ----------------
st.divider()
st.subheader("🔎 Explore Societal Problems")

search_text = st.text_input(
    "Search problems",
    placeholder="Search by title, description, or location...",
)

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    categories = sorted([
        str(value) for value in problem_df["category"].dropna().unique()
        if str(value).strip()
    ])
    selected_category = st.selectbox(
        "Category",
        ["All categories"] + categories,
    )

with filter_col2:
    priorities = sorted([
        str(value) for value in problem_df["priority"].dropna().unique()
        if str(value).strip()
    ])
    selected_priority = st.selectbox(
        "Priority",
        ["All priorities"] + priorities,
    )

with filter_col3:
    statuses = sorted([
        str(value) for value in problem_df["status"].dropna().unique()
        if str(value).strip()
    ])
    selected_status = st.selectbox(
        "Status",
        ["All statuses"] + statuses,
    )


filtered = problem_df.copy()

if search_text.strip():
    searchable = (
        filtered["title"].fillna("").astype(str) + " " +
        filtered["description"].fillna("").astype(str) + " " +
        filtered["location"].fillna("").astype(str)
    )
    filtered = filtered[
        searchable.str.contains(search_text.strip(), case=False, regex=False)
    ]

if selected_category != "All categories":
    filtered = filtered[
        filtered["category"].astype(str) == selected_category
    ]

if selected_priority != "All priorities":
    filtered = filtered[
        filtered["priority"].astype(str) == selected_priority
    ]

if selected_status != "All statuses":
    filtered = filtered[
        filtered["status"].astype(str) == selected_status
    ]


# ---------------- PORTAL METRICS ----------------
total_problems = len(problem_df)
in_progress = int(
    problem_df["status"].astype(str).str.lower().eq("in progress").sum()
)
completed = int(
    problem_df["status"].astype(str).str.lower().eq("completed").sum()
)
open_problems = int(
    problem_df["status"].astype(str).str.lower().isin(
        ["open", "submitted", "pending"]
    ).sum()
)

metric_cols = st.columns(4)

metric_data = [
    ("📋", total_problems, "Total problems"),
    ("🟣", open_problems, "Open / pending"),
    ("🔵", in_progress, "In progress"),
    ("🟢", completed, "Completed"),
]

for col, (emoji, number, label) in zip(metric_cols, metric_data):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div>{emoji}</div>
            <div class="metric-number">{number}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)


# ---------------- PROBLEM LIST ----------------
st.divider()
st.subheader("🌍 Available Societal Problems")
st.caption(f"Showing {len(filtered)} problem(s)")

if filtered.empty:
    st.info("No problems match your filters.")
else:
    for _, problem in filtered.iterrows():
        problem_id = problem.get("id")
        title = str(problem.get("title") or "Untitled problem")
        description = str(problem.get("description") or "")
        location = str(problem.get("location") or "Not specified")
        category = str(problem.get("category") or "Uncategorized")
        priority = str(problem.get("priority") or "Not specified")
        status = str(problem.get("status") or "Submitted")
        summary = str(problem.get("summary") or "")

        st.markdown(f"""
        <div class="problem-card">
            <span class="tag">{html.escape(category)}</span>
            <span class="tag">{html.escape(priority)} priority</span>
            <span class="tag">{html.escape(status)}</span>
            <h3>{html.escape(title)}</h3>
            <p>📍 {html.escape(location)}</p>
            <p>{html.escape(description[:350])}</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"View details and actions: {title}"):
            if summary:
                st.write("**AI Summary**")
                st.write(summary)

            st.write("**Description**")
            st.write(description)

            st.write(f"**Category:** {category}")
            st.write(f"**Priority:** {priority}")
            st.write(f"**Current status:** {status}")

            # The existing recommendation table links a problem
            # to a university. Avoid duplicate recommendations.
            st.markdown("#### 🤝 University matching")

            reason = st.text_area(
                "Why is this university suitable for this problem?",
                key=f"reason_{problem_id}_{university_id}",
                placeholder=(
                    "Explain how your departments or expertise "
                    "could help address this challenge..."
                ),
            )

            if st.button(
                "Save University Recommendation",
                key=f"recommend_{problem_id}_{university_id}",
                use_container_width=True,
            ):
                if not reason.strip():
                    st.warning("Enter a reason for the recommendation.")
                else:
                    try:
                        save_recommendation(
                            problem_id,
                            university_id,
                            reason.strip(),
                        )
                        st.success("Recommendation saved successfully!")
                        st.cache_data.clear()
                    except Exception as error:
                        st.error(
                            "Could not save the recommendation. "
                            "It may already exist or the database "
                            "may require a different field."
                        )
                        st.exception(error)

            st.markdown("#### 📈 Update problem progress")

            new_status = st.selectbox(
                "Status",
                [
                    "Submitted",
                    "Under Review",
                    "In Progress",
                    "Completed",
                    "Rejected",
                ],
                index=(
                    [
                        "Submitted",
                        "Under Review",
                        "In Progress",
                        "Completed",
                        "Rejected",
                    ].index(status)
                    if status in [
                        "Submitted",
                        "Under Review",
                        "In Progress",
                        "Completed",
                        "Rejected",
                    ]
                    else 0
                ),
                key=f"status_{problem_id}",
            )

            if st.button(
                "Update Status",
                key=f"update_{problem_id}",
            ):
                try:
                    update_problem_status(problem_id, new_status)
                    st.success("Problem status updated!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as error:
                    st.error("Could not update the problem status.")
                    st.exception(error)


# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "CivicConnect • University Portal • Connecting expertise "
    "with societal challenges"
)
