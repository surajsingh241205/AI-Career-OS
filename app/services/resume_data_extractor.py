import re 

def extract_basic_info(text):
    data = {} 
    
    lines = text.split("\n")
    
    for line in lines:
        line = line.strip() 
        
        if line:
            data["name"] = line 
            break 
    
    email_match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+', text
    )
    
    if email_match:
        data["email"] = email_match.group() 
        
        phone_match = re.search(
            r'(\+91\s?\d{5}\s?\d{5}|\d{10})',
            text
        )
    
    if phone_match:
        data["phone"] = phone_match.group()
    return data 

def extract_skills(text):
    
    common_skills = [
        # programming 
        "Python", "Java", "C", "C++", "JavaScript",
        # Web 
        "HTML", "CSS", "Bootstrap", "TailwindCSS", "Flask", 
        # Database 
        "MYSQL", "PostgreSQL", 
        # Data Science
        "Pandas", "NumPy", "Matplotlib", "Scikit-learn", 
        # Tools
        "Git", "GitHub", "WordPress", "Canva", "SEO"
    ]
    
    found_skills = [] 
    text_lower = text.lower() 
    
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return sorted(list(set(found_skills)))