def calculate_resume_score(
    resume_data,
    skills,
    resume_text
):

    score = 0

    # Name
    if resume_data.get("name"):
        score += 5

    # Email
    if resume_data.get("email"):
        score += 5

    # Phone
    if resume_data.get("phone"):
        score += 10

    # Skills
    skill_count = len(skills)

    if skill_count >= 10:
        score += 30

    elif skill_count >= 5:
        score += 20

    else:
        score += 10

    # Experience

    if "experience" in resume_text.lower():
        score += 30

    # Education

    education_keywords = [
        "b.tech",
        "bachelor",
        "degree",
        "university",
        "college"
    ]

    if any(
        keyword in resume_text.lower()
        for keyword in education_keywords
    ):
        score += 20

    return score