from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import db
from app.models.user import User
import os 
from werkzeug.utils import secure_filename 
from app.models.resume import Resume
from flask import send_file
from flask import current_app
from app.services.resume_parser import extract_text
from app.services.resume_data_extractor import extract_basic_info
from app.services.resume_data_extractor import (extract_basic_info, extract_skills)
from app.models.resume_analysis import ResumeAnalysis
from app.services.resume_scorer import (calculate_resume_score)
from app.models.job_application import JobApplication
from datetime import datetime

ALLOWED_EXTENSIONS = {
    "pdf", "docx"
}

def allowed_file(filename):
    return (
        "." in filename and 
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )

auth = Blueprint(
    "auth",
    __name__
)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if email already exists
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # Hash password
        hashed_password = generate_password_hash(
            password
        )

        # Create user
        new_user = User(
            name=name,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html"
    )


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            flash(
                f"Welcome back, {user.name}!",
                "success"
            )

            return redirect(
                url_for("auth.dashboard")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


@auth.route("/dashboard")
@login_required
def dashboard():
    
    resumes = Resume.query.filter_by(
        user_id = current_user.id
    ).order_by(
        Resume.uploaded_at.desc()
    ).all()

    latest_analysis = ResumeAnalysis.query\
    .join(Resume)\
    .filter(
        Resume.user_id == current_user.id
    )\
    .order_by(
        ResumeAnalysis.id.desc()
    )\
    .first()
    
    resume_score = 0
    skills_count = 0

    if latest_analysis:
        resume_score = latest_analysis.score
    skills_count = len(
        latest_analysis.skills.split(",")
    )
    
    resumes = Resume.query.filter_by(
    user_id=current_user.id
    ).all()

    applications_count = JobApplication.query.filter_by(
    user_id=current_user.id
    ).count()

    interviews_count = JobApplication.query.filter_by(
    user_id=current_user.id,
    status="Interview"
    ).count()

    rejected_count = JobApplication.query.filter_by(
    user_id=current_user.id,
    status="Rejected"
    ).count()

    offer_count = JobApplication.query.filter_by(
    user_id=current_user.id,
    status="Offer"
    ).count()

    interview_rate = 0
    success_rate = 0

    if applications_count > 0:

        interview_rate = round(
            (interviews_count / applications_count) * 100
        )

    success_rate = round(
        (offer_count / applications_count) * 100
    )

    latest_analysis = ResumeAnalysis.query\
    .join(Resume)\
    .filter(
        Resume.user_id == current_user.id
    )\
    .order_by(
        ResumeAnalysis.id.desc()
    )\
    .first()

    resume_score = 0
    skills_count = 0

    if latest_analysis:

        resume_score = latest_analysis.score

    if latest_analysis.skills:
        skills_count = len(
            latest_analysis.skills.split(",")
        )
        
    resume_activities = []

    for resume in resumes:

        resume_activities.append({
        "type": "resume",
        "message": f"Uploaded resume: {resume.file_name}",
        "date": resume.uploaded_at
    })
        
    applications = JobApplication.query.filter_by(
    user_id=current_user.id
    ).all()

    application_activities = []

    for app in applications:

        application_activities.append({
        "type": "application",
        "message": f"Applied to {app.company_name} - {app.job_title}",
        "date": app.created_at
    })
        
    activities = (
    resume_activities +
    application_activities
    )

    activities.sort(
    key=lambda x: x["date"],
    reverse=True
)

    activities = activities[:5]
    
    return render_template(
        "dashboard.html",
        user=current_user,
        resumes = resumes,
        resume_score = resume_score,
        skills_count = skills_count,
        applications_count = applications_count,
        interviews_count = interviews_count,
        rejected_count=rejected_count,
        offer_count=offer_count,
        interview_rate=interview_rate,
        success_rate=success_rate,
        activities = activities
    )
    
    


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )

@auth.route("/upload-resume", methods=["GET", "POST"])
@login_required
def upload_resume():

    if request.method == "POST":

        file = request.files.get("resume")

        if not file:

            flash(
                "Please select a file.",
                "error"
            )

            return redirect(
                url_for("auth.upload_resume")
            )

        if not allowed_file(file.filename):

            flash(
                "Only PDF and DOCX files are allowed.",
                "error"
            )

            return redirect(
                url_for("auth.upload_resume")
            )

        filename = secure_filename(
            file.filename
        )

        upload_folder = os.path.join(
            current_app.root_path,
            "uploads"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        filepath = os.path.join(
            upload_folder,
            filename
        )

        file.save(filepath)
        
        resume_text = extract_text(filepath)
        resume_data = extract_basic_info(
            resume_text
        )
        skills = extract_skills(
            resume_text
        )
        
        score = calculate_resume_score(
                resume_data,
                skills,
                resume_text
            )

        print("\n===== RESUME SCORE =====\n")
        print(score)
        print("\n========================\n")
        
        print("\n===== SKILLS =====\n")
        print(skills)
        print("\n==================\n")
        
        print("\n===== EXTRACTED DATA =====\n")
        print(resume_data)
        print("\n=========================\n")
        
        print("\n========== RESUME TEXT ==========\n")
        print(resume_text[:1000])
        print("\n===============================\n")
        
        resume = Resume(
            file_name=filename,
            file_path=filepath,
            user_id=current_user.id
        )

        db.session.add(resume)
        db.session.commit()
        
        analysis = ResumeAnalysis(
            resume_id = resume.id, 
            
            name = resume_data.get("name"),
            email = resume_data.get("email"),
            phone = resume_data.get("phone"),
            skills = ",".join(skills),
            score = score
            )
        db.session.add(analysis)
        db.session.commit()

        flash(
            "Resume uploaded successfully.",
            "success"
        )

        return redirect(
            url_for("auth.dashboard")
        )

    return render_template(
        "upload_resume.html"
    )

@auth.route("/resume/<int:resume_id>/view")
@login_required
def view_resume(resume_id):

    resume = Resume.query.get_or_404(
        resume_id
    )

    if resume.user_id != current_user.id:

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("auth.dashboard")
        )

    return send_file(
        resume.file_path,
        as_attachment=False
    )

@auth.route("/resume/<int:resume_id>/delete")
@login_required
def delete_resume(resume_id):

    resume = Resume.query.get_or_404(
        resume_id
    )

    if resume.user_id != current_user.id:

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("auth.dashboard")
        )

    import os

    if os.path.exists(
        resume.file_path
    ):
        os.remove(
            resume.file_path
        )

    db.session.delete(
        resume
    )

    db.session.commit()

    flash(
        "Resume deleted successfully.",
        "success"
    )

    return redirect(
        url_for("auth.dashboard")
    )

@auth.route("/resume-analysis/<int:resume_id>")
@login_required
def resume_analysis(resume_id):

    resume = Resume.query.filter_by(
        id=resume_id,
        user_id=current_user.id
    ).first_or_404()

    analysis = ResumeAnalysis.query.filter_by(
        resume_id=resume.id
    ).first()

    print(analysis)
    print(analysis.name if analysis else "NO ANALYSIS")

    return render_template(
        "resume_analysis.html",
        resume=resume,
        analysis=analysis
    )
    
@auth.route("/add-application", methods=["GET", "POST"])
@login_required
def add_application():

    if request.method == "POST":

        company_name = request.form.get(
            "company_name"
        )

        job_title = request.form.get(
            "job_title"
        )

        status = request.form.get(
            "status"
        )

        applied_date = request.form.get(
            "applied_date"
        )

        application = JobApplication(

            company_name=company_name,

            job_title=job_title,

            status=status,

            applied_date=datetime.strptime(
                applied_date,
                "%Y-%m-%d"
            ).date(),

            user_id=current_user.id
        )

        db.session.add(application)
        db.session.commit()

        flash(
            "Application added successfully.",
            "success"
        )

        return redirect(
            url_for("auth.applications")
        )

    return render_template(
        "add_application.html"
    )

@auth.route("/applications")
@login_required
def applications():

    applications = JobApplication.query.filter_by(
        user_id=current_user.id
    ).order_by(
        JobApplication.id.desc()
    ).all()

    applied_count = JobApplication.query.filter_by(
    user_id=current_user.id,
    status="Applied"
    ).count()

    interview_count = JobApplication.query.filter_by(
    user_id=current_user.id,
    status="Interview"
    ).count()

    rejected_count = JobApplication.query.filter_by(
    user_id=current_user.id,
    status="Rejected"
    ).count()

    offer_count = JobApplication.query.filter_by(
    user_id=current_user.id,
    status="Offer"
    ).count()

    return render_template(
        "applications.html",
        applications=applications,
        applied_count=applied_count,
        interview_count=interview_count,
        rejected_count=rejected_count,
        offer_count=offer_count
    )
    
@auth.route(
    "/application/<int:application_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_application(application_id):

    application = JobApplication.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        application.status = request.form.get(
            "status"
        )

        db.session.commit()

        flash(
            "Application updated successfully.",
            "success"
        )

        return redirect(
            url_for("auth.applications")
        )

    return render_template(
        "edit_application.html",
        application=application
    )

@auth.route(
    "/application/<int:application_id>/delete"
)
@login_required
def delete_application(application_id):

    application = JobApplication.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(
        application
    )

    db.session.commit()

    flash(
        "Application deleted successfully.",
        "success"
    )

    return redirect(
        url_for("auth.applications")
    )