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

    return render_template(
        "dashboard.html",
        user=current_user,
        resumes = resumes
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