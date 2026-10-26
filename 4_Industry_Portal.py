
import streamlit as st
import pandas as pd
from database import get_existing_problems
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
from database import get_existing_problems, save_industry_interest
st.set_page_config(
    page_title="Industry Partner Portal | CivicConnect",
    page_icon="🤝",
    layout="wide"
)

# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
.stApp {
    background-color: #f7f5ff;
}
.hero {
    background: linear-gradient(120deg, #5b21b6, #8b5cf6);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    color: white;
    margin-bottom: 8px;
}
.hero p {
    color: #f3e8ff;
    font-size: 16px;
}
.section-title {
    color: #4c1d95;
    font-weight: 700;
}
.problem-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e9d5ff;
    margin-bottom: 12px;
}
.small-label {
    color: #6b21a8;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------- SUPABASE CONNECTION ----------




# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <h1>🤝 Industry Partner Portal</h1>
    <p>
        Connect industry expertise and resources with societal challenges.
        Explore opportunities to collaborate with universities and communities.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<h3 class='section-title'>Discover Collaboration Opportunities</h3>",
    unsafe_allow_html=True
)

# ---------- LOAD PROBLEMS ----------
@st.cache_data(ttl=30)
def load_problems():
    return get_existing_problems()


try:
    problems = load_problems()
except Exception as e:
    st.error(f"Unable to load problems: {e}")
    st.stop()

if not problems:
    st.info("No societal problems are available yet.")
    st.stop()

df = pd.DataFrame(problems)

# ---------- FILTERS ----------
col1, col2, col3 = st.columns(3)

with col1:
    categories = sorted(
        df["category"].dropna().astype(str).unique().tolist()
    ) if "category" in df.columns else []
    selected_category = st.selectbox(
        "Problem category",
        ["All Categories"] + categories
    )

with col2:
    priorities = sorted(
        df["priority"].dropna().astype(str).unique().tolist()
    ) if "priority" in df.columns else []
    selected_priority = st.selectbox(
        "Priority",
        ["All Priorities"] + priorities
    )

with col3:
    search = st.text_input(
        "Search opportunities",
        placeholder="Search by title, location, or keywords"
    )

filtered = df.copy()

if selected_category != "All Categories" and "category" in filtered.columns:
    filtered = filtered[
        filtered["category"].astype(str) == selected_category
    ]

if selected_priority != "All Priorities" and "priority" in filtered.columns:
    filtered = filtered[
        filtered["priority"].astype(str) == selected_priority
    ]

if search.strip():
    searchable_columns = [
        col for col in ["title", "description", "location", "keywords"]
        if col in filtered.columns
    ]

    if searchable_columns:
        mask = filtered[searchable_columns].fillna("").astype(str).apply(
            lambda column: column.str.contains(
                search.strip(), case=False, regex=False
            )
        ).any(axis=1)

        filtered = filtered[mask]

# ---------- SUMMARY METRICS ----------
m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Available Problems", len(df))

with m2:
    st.metric("Matching Opportunities", len(filtered))

with m3:
    st.metric(
        "High-Priority Problems",
        int(
            (
                filtered["priority"].astype(str).str.lower() == "high"
            ).sum()
        ) if "priority" in filtered.columns else 0
    )

st.divider()

# ---------- OPPORTUNITY CARDS ----------
st.markdown(
    "<h3 class='section-title'>Problems Seeking Support</h3>",
    unsafe_allow_html=True
)

for _, problem in filtered.iterrows():
    problem_id = str(problem.get("id", ""))
    title = str(problem.get("title") or "Untitled Problem")
    location = str(problem.get("location") or "Location not specified")
    category = str(problem.get("category") or "Uncategorized")
    priority = str(problem.get("priority") or "Not specified")
    status = str(problem.get("status") or "Unknown")
    description = str(problem.get("description") or "No description available.")
    summary = str(problem.get("summary") or "")

    with st.container(border=True):
        left, right = st.columns([4, 1])

        with left:
            st.subheader(title)
            st.caption(f"📍 {location}  •  {category}")
            st.write(description)

            if summary:
                st.info(f"AI Summary: {summary}")

        with right:
            st.markdown(f"**Priority:** {priority}")
            st.markdown(f"**Status:** {status}")

        with st.expander("View collaboration details"):
            st.write(f"**Problem ID:** {problem_id}")
            st.write(f"**Category:** {category}")
            st.write(f"**Location:** {location}")

            st.markdown("**Potential industry contributions**")
            st.write(
                "Funding, technical mentoring, equipment, "
                "implementation support, or domain expertise."
            )

            with st.form(key=f"interest_form_{problem_id}"):
                st.markdown("### Express Interest")

                company_name = st.text_input(
                    "Company / Organization Name",
                    key=f"company_{problem_id}"
                )

                industry_sector = st.selectbox(
                    "Industry Sector",
                    [
                        "Information Technology",
                        "Manufacturing",
                        "Healthcare",
                        "Agriculture",
                        "Energy and Environment",
                        "Education",
                        "Infrastructure",
                        "Other"
                    ],
                    key=f"sector_{problem_id}"
                )

                company_location = st.text_input(
                    "Company Location",
                    key=f"location_{problem_id}"
                )

                contact_email = st.text_input(
                    "Contact Email",
                    key=f"email_{problem_id}"
                )

                support_type = st.selectbox(
                    "Type of Support",
                    [
                        "Technical Mentoring",
                        "Funding",
                        "Equipment",
                        "Technical Development",
                        "Implementation Support",
                        "Research Collaboration",
                        "Other"
                    ],
                    key=f"support_{problem_id}"
                )

                support_details = st.text_area(
                    "Describe your proposed contribution",
                    placeholder=(
                        "Explain how your organization could help "
                        "address this problem."
                    ),
                    key=f"details_{problem_id}"
                )

                submitted = st.form_submit_button(
                    "Submit Collaboration Proposal",
                    use_container_width=True
                )

                if submitted:
                    if not company_name.strip():
                        st.error("Please enter your organization name.")
                    elif not contact_email.strip() or "@" not in contact_email:
                        st.error("Please enter a valid contact email.")
                    elif not support_details.strip():
                        st.error("Please describe your proposed contribution.")
                    else:
                        try:
                            data = {
                                
                                "problem_id": problem_id,
                                "company_name": company_name.strip(),
                                "industry_sector": industry_sector,
                                "location": company_location.strip(),
                                "contact_email": contact_email.strip(),
                                "support_type": support_type,
                                "support_details": support_details.strip(),
                                "status": "Interested"
                            }
                            save_industry_interest(data)

                            st.success(
                                "Proposal submitted successfully! "
                                "The platform can now review your interest."
                            )

                        except Exception as e:
                            st.error(f"Could not save your proposal:{e}")

if filtered.empty:
    st.info("No problems match your selected filters.")

# ---------- FOOTER ----------
st.divider()
st.caption(
    "CivicConnect | Connecting communities, universities, and industry."
)
