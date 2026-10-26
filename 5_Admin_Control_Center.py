
import streamlit as st
import pandas as pd
from database import (
    get_existing_problems,
    update_problem_status
)
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="Admin Control Center | CivicConnect",
    page_icon="🛡️",
    layout="wide"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: #f7f5ff;
}
.hero {
    background: linear-gradient(120deg, #4c1d95, #8b5cf6);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 24px;
}
.hero h1 {
    color: white;
}
.hero p {
    color: #f3e8ff;
}
.section-title {
    color: #4c1d95;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Supabase settings are missing from .env")

    return create_client(url, key)


# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <h1>🛡️ Admin Control Center</h1>
    <p>
        Manage societal challenges, review industry proposals,
        and monitor collaboration across CivicConnect.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------- LOAD DATA ----------
@st.cache_data(ttl=30)
def load_problems():
    return get_existing_problems()


@st.cache_data(ttl=30)
def load_industry_interests():
    client = get_supabase_client()
    response = (
        client.table("industry_interests")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


try:
    problems = load_problems()
except Exception as e:
    st.error(f"Unable to load problems: {e}")
    st.stop()

try:
    interests = load_industry_interests()
except Exception as e:
    st.error(f"Unable to load industry proposals: {e}")
    st.info(
        "Check that the industry_interests table exists "
        "and that the configured Supabase key has permission to read it."
    )
    interests = []


# ---------- METRICS ----------
problem_df = pd.DataFrame(problems)
interest_df = pd.DataFrame(interests)

total_problems = len(problem_df)

if not problem_df.empty and "status" in problem_df.columns:
    status_series = problem_df["status"].fillna("").astype(str).str.lower()
    open_count = int(status_series.isin(["open", "submitted", "pending"]).sum())
    progress_count = int(
        status_series.str.contains("progress", regex=False).sum()
    )
    completed_count = int(
        status_series.isin(["completed", "resolved", "closed"]).sum()
    )
else:
    open_count = 0
    progress_count = 0
    completed_count = 0

proposal_count = len(interest_df)

if not interest_df.empty and "status" in interest_df.columns:
    proposal_status = interest_df["status"].fillna("").astype(str).str.lower()
    pending_count = int(
        proposal_status.isin(["interested", "pending", "submitted"]).sum()
    )
else:
    pending_count = 0

st.markdown(
    "<h3 class='section-title'>Platform Overview</h3>",
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Problems", total_problems)
c2.metric("Open Problems", open_count)
c3.metric("In Progress", progress_count)
c4.metric("Completed", completed_count)

c5, c6 = st.columns(2)
c5.metric("Industry Proposals", proposal_count)
c6.metric("Awaiting Review", pending_count)

st.divider()


# ---------- TABS ----------
problem_tab, proposal_tab = st.tabs([
    "📋 Manage Problems",
    "🤝 Industry Proposals"
])


# ---------- PROBLEM MANAGEMENT ----------
with problem_tab:
    st.markdown(
        "<h3 class='section-title'>Societal Problems</h3>",
        unsafe_allow_html=True
    )

    if problem_df.empty:
        st.info("No problems have been submitted yet.")
    else:
        search = st.text_input(
            "Search problems",
            placeholder="Search by title or location"
        )

        filtered_df = problem_df.copy()

        if search.strip():
            searchable = [
                col for col in ["title", "location", "category"]
                if col in filtered_df.columns
            ]

            if searchable:
                mask = filtered_df[searchable].fillna("").astype(str).apply(
                    lambda col: col.str.contains(
                        search.strip(), case=False, regex=False
                    )
                ).any(axis=1)

                filtered_df = filtered_df[mask]

        for _, problem in filtered_df.iterrows():
            problem_id = problem.get("id")
            title = str(problem.get("title") or "Untitled Problem")
            category = str(problem.get("category") or "Uncategorized")
            location = str(problem.get("location") or "Not specified")
            status = str(problem.get("status") or "Open")
            priority = str(problem.get("priority") or "Not specified")

            with st.container(border=True):
                st.subheader(title)
                st.caption(f"{category} • {location}")
                st.write(f"**Priority:** {priority}")
                st.write(f"**Current status:** {status}")

                status_options = [
                    "Open",
                    "Under Review",
                    "In Progress",
                    "Completed",
                    "Rejected"
                ]

                current_status = (
                    status if status in status_options else "Open"
                )

                with st.form(key=f"status_form_{problem_id}"):
                    new_status = st.selectbox(
                        "Update problem status",
                        status_options,
                        index=status_options.index(current_status),
                        key=f"status_select_{problem_id}"
                    )

                    update_clicked = st.form_submit_button(
                        "Save Status",
                        use_container_width=True
                    )

                    if update_clicked:
                        try:
                            update_problem_status(
                                problem_id,
                                new_status
                            )
                            st.success("Problem status updated.")
                            load_problems.clear()
                            load_industry_interests.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Status update failed: {e}")


# ---------- INDUSTRY PROPOSALS ----------
with proposal_tab:
    st.markdown(
        "<h3 class='section-title'>Industry Collaboration Proposals</h3>",
        unsafe_allow_html=True
    )

    if interest_df.empty:
        st.info("No industry proposals have been submitted yet.")
    else:
        filter_options = ["All"] + sorted(
            interest_df["status"].fillna("Unknown").astype(str).unique().tolist()
        ) if "status" in interest_df.columns else ["All"]

        selected_status = st.selectbox(
            "Filter proposals by status",
            filter_options
        )

        visible_df = interest_df.copy()

        if selected_status != "All" and "status" in visible_df.columns:
            visible_df = visible_df[
                visible_df["status"].fillna("Unknown").astype(str)
                == selected_status
            ]

        for _, proposal in visible_df.iterrows():
            proposal_id = proposal.get("id")
            company = str(proposal.get("company_name") or "Unknown company")
            support = str(proposal.get("support_type") or "Not specified")
            details = str(proposal.get("support_details") or "")
            email = str(proposal.get("contact_email") or "Not provided")
            sector = str(proposal.get("industry_sector") or "Not specified")
            location = str(proposal.get("location") or "Not specified")
            current = str(proposal.get("status") or "Interested")

            with st.container(border=True):
                st.subheader(company)
                st.caption(f"{sector} • {location}")
                st.write(f"**Problem ID:** {proposal.get('problem_id', 'N/A')}")
                st.write(f"**Proposed support:** {support}")
                st.write(details)
                st.write(f"**Contact:** {email}")
                st.write(f"**Current review status:** {current}")

                proposal_status_options = [
                    "Interested",
                    "Under Review",
                    "Approved",
                    "Rejected"
                ]

                if current not in proposal_status_options:
                    proposal_status_options.insert(0, current)

                with st.form(key=f"proposal_form_{proposal_id}"):
                    new_proposal_status = st.selectbox(
                        "Review decision",
                        proposal_status_options,
                        index=proposal_status_options.index(current),
                        key=f"proposal_status_{proposal_id}"
                    )

                    review_clicked = st.form_submit_button(
                        "Save Review Decision",
                        use_container_width=True
                    )

                    if review_clicked:
                        try:
                            client = get_supabase_client()
                            (
                                client.table("industry_interests")
                                .update({"status": new_proposal_status})
                                .eq("id", proposal_id)
                                .execute()
                            )

                            st.success("Proposal review status updated.")
                            load_industry_interests.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Unable to update proposal: {e}")


# ---------- FOOTER ----------
st.divider()
st.caption(
    "CivicConnect Admin | Review decisions should be made "
    "by authorized administrators."
)
