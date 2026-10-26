import streamlit as st
import uuid
from database import (
    save_problem,
    upload_image,
    get_existing_problems,
    get_universities,
    save_recommendation
)
from ai import analyze_problem, validate_analysis, detect_duplicate, recommend_universities

st.set_page_config(
    page_title="Societal Problem Portal",
    page_icon="🌍"
)

st.title("🌍 Societal Problem Reporting Portal")

st.write(
    "Report a local societal problem and let AI analyze "
    "and prioritize it for further action."
)

st.divider()

st.header("Report a Problem")


title = st.text_input(
    "Problem Title *",
    placeholder="Example: Lack of drinking water"
)

description = st.text_area(
    "Describe the Problem *",
    placeholder="Explain the problem in detail...",
    height=150
)

location = st.text_input(
    "Location *",
    placeholder="Example: Village, District, State"
)

category = st.selectbox(
    "Problem Category",
    [
        "Not Sure",
        "Education",
        "Healthcare",
        "Agriculture",
        "Water Management",
        "Sanitation",
        "Environment",
        "Rural Livelihood",
        "Accessibility",
        "Urban Infrastructure",
        "Public Services",
        "Other"
    ]
)

image = st.file_uploader(
    "Upload a Photo (Optional)",
    type=["jpg", "jpeg", "png"]
)

name = st.text_input("Name (Optional)")

email = st.text_input("Email (Optional)")


if st.button("🚀 Submit Problem"):

    if not title.strip():
        st.error("Please enter the problem title.")

    elif not description.strip():
        st.error("Please describe the problem.")

    elif not location.strip():
        st.error("Please enter the location.")

    else:

        try:

            # Step 1: Analyze problem using Gemini
            with st.spinner("🤖 AI is analyzing the problem..."):

                ai_result = analyze_problem(
                    title,
                    description,
                    location
                )
                if not validate_analysis(ai_result):
                    st.error("AI returned an invalid analysis.")
                    st.stop()
                # Get existing problems from database
                existing_problems = get_existing_problems()

                # Check whether this problem is a duplicate
                duplicate_result = detect_duplicate(
                    title,
                    description,
                    location,
                    existing_problems
                )
                # Get universities from database
                universities = get_universities()
                # Recommend universities using AI
                university_recommendations = recommend_universities(
                    title,
                    description,
                    ai_result["category"],
                    ai_result["subcategory"],
                    universities
                )
                
            image_url = None

            if image is not None:

                file_name = f"{uuid.uuid4()}_{image.name}"

                image_url = upload_image(
                    image,
                    file_name
                )


            # Step 2: Prepare data for Supabase
            data = {
                "title": title,
                "description": description,
                "location": location,
                "citizen_category": category,

                "category": ai_result["category"],
                "subcategory": ai_result["subcategory"],
                "priority": ai_result["priority"],
                "summary": ai_result["summary"],
                "keywords": ", ".join(ai_result["keywords"]),
                "image_url": image_url,

                "name": name,
                "email": email,
                
                "is_duplicate": duplicate_result["is_duplicate"],
                "duplicate_of": duplicate_result["duplicate_of"],
                "duplicate_reason": duplicate_result["duplicate_reason"],
                "status": "Submitted"
            }


            # Step 3: Save everything to Supabase
            problem_id = save_problem(data)

            # Step 3.1: Save university recommendations
            for recommendation in university_recommendations:
                save_recommendation(
                    problem_id,
                    recommendation["university_id"],
                    recommendation["reason"]
                )


            # Step 4: Show result
            st.success("✅ Problem submitted successfully!")

            st.subheader("Recommended Universities")

            if university_recommendations:
                for recommendation in university_recommendations:

                    university_id = recommendation["university_id"]
                    reason = recommendation["reason"]

                    # Find university details
                    for university in universities:
                        if university["id"] == university_id:

                            st.write(f"### {university['name']}")
                            st.write(f"📍 {university['location']}")
                            st.write(f"🏛️ Departments: {university['departments']}")
                            st.write(f"💡 Reason: {reason}")
                            break

            else:
                st.write("No suitable university found.")

            st.subheader("🤖 AI Analysis")

            st.write(
                "**Category:**",
                ai_result["category"]
            )

            st.write(
                "**Subcategory:**",
                ai_result["subcategory"]
            )

            st.write(
                "**Priority:**",
                ai_result["priority"]
            )

            st.write(
                "**Summary:**",
                ai_result["summary"]
            )

            st.write(
                "**Keywords:**",
                ", ".join(ai_result["keywords"])
            )


        except Exception as e:

            st.error("❌ Something went wrong.")

            st.exception(e)