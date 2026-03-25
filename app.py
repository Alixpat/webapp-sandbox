import os
import uuid
from datetime import datetime, timezone

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql://hello:hello@localhost:5432/hellodb"
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Veuillez vous connecter."

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # user | supervisor
    projects = db.relationship("Project", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_supervisor(self):
        return self.role == "supervisor"


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    budget_lines = db.relationship("BudgetLine", backref="project", lazy=True, cascade="all, delete-orphan")

    @property
    def total_amount(self):
        return sum(bl.amount for bl in self.budget_lines)


class BudgetLine(db.Model):
    __tablename__ = "budget_lines"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    justification = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    attachments = db.relationship("Attachment", backref="budget_line", lazy=True, cascade="all, delete-orphan")


class Attachment(db.Model):
    __tablename__ = "attachments"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    original_name = db.Column(db.String(256), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    budget_line_id = db.Column(db.Integer, db.ForeignKey("budget_lines.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

def seed_data():
    if User.query.first():
        return

    # Users
    alice = User(name="Alice Dupont", email="alice@example.com", role="user")
    alice.set_password("alice123")
    bob = User(name="Bob Martin", email="bob@example.com", role="user")
    bob.set_password("bob123")
    admin = User(name="Sophie Leroy", email="admin@example.com", role="supervisor")
    admin.set_password("admin123")
    db.session.add_all([alice, bob, admin])
    db.session.flush()

    # Projects for Alice
    p1 = Project(name="Refonte site web", description="Modernisation du site web corporate avec nouveau design et migration vers le cloud.", user_id=alice.id)
    p2 = Project(name="Formation Data Science", description="Programme de formation en data science pour l'équipe technique.", user_id=alice.id)
    db.session.add_all([p1, p2])
    db.session.flush()

    # Budget lines for project 1
    db.session.add_all([
        BudgetLine(label="Design UX/UI", amount=15000, justification="Prestation agence de design pour maquettes et prototypes interactifs.", project_id=p1.id),
        BudgetLine(label="Développement front-end", amount=25000, justification="Développement React.js par un prestataire externe sur 3 mois.", project_id=p1.id),
        BudgetLine(label="Hébergement cloud", amount=4800, justification="Abonnement AWS pour 12 mois (EC2 + RDS + S3).", project_id=p1.id),
    ])

    # Budget lines for project 2
    db.session.add_all([
        BudgetLine(label="Licence plateforme e-learning", amount=3000, justification="Abonnement annuel DataCamp Team pour 10 utilisateurs.", project_id=p2.id),
        BudgetLine(label="Intervenant externe", amount=8000, justification="2 jours de formation en présentiel par un expert Machine Learning.", project_id=p2.id),
    ])

    # Project for Bob
    p3 = Project(name="Migration ERP", description="Migration de l'ERP legacy vers une solution SaaS moderne.", user_id=bob.id)
    db.session.add(p3)
    db.session.flush()

    db.session.add_all([
        BudgetLine(label="Audit technique", amount=12000, justification="Audit complet de l'existant par un cabinet de conseil.", project_id=p3.id),
        BudgetLine(label="Licence ERP SaaS", amount=36000, justification="Abonnement annuel Odoo Enterprise pour 25 utilisateurs.", project_id=p3.id),
        BudgetLine(label="Conduite du changement", amount=5000, justification="Accompagnement des équipes et documentation utilisateur.", project_id=p3.id),
    ])

    db.session.commit()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.is_supervisor:
            return redirect(url_for("supervisor_dashboard"))
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        flash("Email ou mot de passe incorrect.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# --- User dashboard ---

@app.route("/dashboard")
@login_required
def dashboard():
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template("dashboard.html", projects=projects)


@app.route("/projects/new", methods=["GET", "POST"])
@login_required
def project_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash("Le nom du projet est obligatoire.", "danger")
        else:
            project = Project(name=name, description=description, user_id=current_user.id)
            db.session.add(project)
            db.session.commit()
            flash("Projet créé avec succès.", "success")
            return redirect(url_for("project_detail", project_id=project.id))
    return render_template("project_new.html")


@app.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash("Projet introuvable.", "danger")
        return redirect(url_for("dashboard"))
    if not current_user.is_supervisor and project.user_id != current_user.id:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("dashboard"))
    budget_lines = BudgetLine.query.filter_by(project_id=project.id).order_by(BudgetLine.created_at.desc()).all()
    return render_template("project_detail.html", project=project, budget_lines=budget_lines)


@app.route("/projects/<int:project_id>/budget-lines/new", methods=["GET", "POST"])
@login_required
def budget_line_new(project_id):
    project = db.session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        label = request.form.get("label", "").strip()
        amount_str = request.form.get("amount", "").strip()
        justification = request.form.get("justification", "").strip()
        if not label or not amount_str:
            flash("Le libellé et le montant sont obligatoires.", "danger")
        else:
            try:
                amount = float(amount_str)
            except ValueError:
                flash("Montant invalide.", "danger")
                return render_template("budget_line_new.html", project=project)
            bl = BudgetLine(label=label, amount=amount, justification=justification, project_id=project.id)
            db.session.add(bl)
            db.session.flush()

            files = request.files.getlist("attachments")
            for f in files:
                if f and f.filename:
                    original = secure_filename(f.filename)
                    ext = os.path.splitext(original)[1]
                    stored = f"{uuid.uuid4().hex}{ext}"
                    f.save(os.path.join(app.config["UPLOAD_FOLDER"], stored))
                    att = Attachment(filename=stored, original_name=original, budget_line_id=bl.id)
                    db.session.add(att)

            db.session.commit()
            flash("Ligne budgétaire ajoutée.", "success")
            return redirect(url_for("project_detail", project_id=project.id))
    return render_template("budget_line_new.html", project=project)


@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# --- Supervisor dashboard ---

@app.route("/supervisor")
@login_required
def supervisor_dashboard():
    if not current_user.is_supervisor:
        flash("Accès réservé aux superviseurs.", "danger")
        return redirect(url_for("dashboard"))
    projects = Project.query.order_by(Project.created_at.desc()).all()
    total = sum(p.total_amount for p in projects)
    return render_template("supervisor.html", projects=projects, total=total)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

with app.app_context():
    db.create_all()
    seed_data()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
