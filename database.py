import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
print("Supabase URL configured:", bool(SUPABASE_URL))
print("Supabase key configured:", bool(SUPABASE_KEY))
print(
    "Key type:",
    "publishable" if SUPABASE_KEY and SUPABASE_KEY.startswith("sb_publishable_")
    else "legacy anon JWT" if SUPABASE_KEY and SUPABASE_KEY.startswith("eyJ")
    else "other or missing"
)
print("URL:", SUPABASE_URL)
print("KEY EXISTS:", bool(SUPABASE_KEY))

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def save_problem(data):
    response = (
        supabase
        .table("problems")
        .insert(data)
        .execute()
    )

    return response.data[0]["id"]
def get_existing_problems():

    response = (
        supabase
        .table("problems")
        .select(
            "id, title, description, location, "
            "category, subcategory, priority, summary, "
            "keywords, is_duplicate, duplicate_of, "
            "duplicate_reason, status"
        )
        .execute()
    )

    return response.data

def upload_image(file, file_name):

    file_bytes = file.getvalue()

    response = supabase.storage.from_("problem-images").upload(
        file_name,
        file_bytes
    )

    image_url = (
        f"{SUPABASE_URL}/storage/v1/object/public/"
        f"problem-images/{file_name}"
    )

    return image_url
def get_universities():
    response = (
        supabase
        .table("universities")
        .select("id, name, location, departments, expertise")
        .execute()
    )

    return response.data
def save_recommendation(problem_id, university_id, reason):

    data = {
        "problem_id": problem_id,
        "university_id": university_id,
        "reason": reason
    }

    response = (
        supabase
        .table("recommendations")
        .insert(data)
        .execute()
    )

    return response
def update_problem_status(problem_id, new_status):

    response = (
        supabase
        .table("problems")
        .update({
            "status": new_status
        })
        .eq("id", problem_id)
        .execute()
    )

    return response

def save_industry_interest(data):
    response = (
        supabase
        .table("industry_interests")
        .insert(data)
        .execute()
    )

    return response.data
