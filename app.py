import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, AdminUser, Project, Podcast, Blog, Initiative
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///econcore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload

# Upload folders
UPLOAD_FOLDER = os.path.join('static', 'uploads')
PROJECT_FOLDER = os.path.join(UPLOAD_FOLDER, 'projects')
PODCAST_FOLDER = os.path.join(UPLOAD_FOLDER, 'podcasts')
BLOG_FOLDER = os.path.join(UPLOAD_FOLDER, 'blogs')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'mov', 'mp3', 'wav', 'ogg', 'pdf', 'doc', 'docx', 'zip'}

os.makedirs(PROJECT_FOLDER, exist_ok=True)
os.makedirs(PODCAST_FOLDER, exist_ok=True)
os.makedirs(BLOG_FOLDER, exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, subfolder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid overwrites
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now(pytz.timezone('UTC')).strftime('%Y%m%d%H%M%S')}{ext}"
        folder = os.path.join(UPLOAD_FOLDER, subfolder)
        os.makedirs(folder, exist_ok=True)
        file.save(os.path.join(folder, filename))
        return os.path.join('static', 'uploads', subfolder, filename).replace('\\', '/')
    return None

# ─── Routes ───────────────────────────────────────────

@app.route('/')
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    podcasts = Podcast.query.order_by(Podcast.episode_number.desc()).all()
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    initiatives = Initiative.query.all()
    return render_template('index.html',
                         projects=projects,
                         podcasts=podcasts,
                         blogs=blogs,
                         initiatives=initiatives)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    podcasts = Podcast.query.order_by(Podcast.episode_number.desc()).all()
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    initiatives = Initiative.query.all()
    return render_template('admin_dashboard.html',
                         projects=projects,
                         podcasts=podcasts,
                         blogs=blogs,
                         initiatives=initiatives)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

# ─── PROJECT CRUD ──────────────────────────────────

@app.route('/admin/project/add', methods=['POST'])
@login_required
def add_project():
    title = request.form.get('title')
    category = request.form.get('category', 'Macroeconomics')
    description = request.form.get('description')
    lead_author = request.form.get('lead_author', 'Research Team')
    page_count = request.form.get('page_count', 'N/A')
    video_url = request.form.get('video_url', '')
    date_str = request.form.get('date', datetime.now(pytz.timezone('UTC')).strftime('%b %Y'))

    thumbnail = None
    if 'thumbnail' in request.files:
        thumbnail = save_file(request.files['thumbnail'], 'projects')

    file_url = None
    if 'file' in request.files:
        file_url = save_file(request.files['file'], 'projects')

    project = Project(
        title=title, category=category, description=description,
        thumbnail=thumbnail, video_url=video_url, file_url=file_url,
        lead_author=lead_author, page_count=page_count, date=date_str
    )
    db.session.add(project)
    db.session.commit()
    flash('Project added!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/project/delete/<int:id>')
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    # Clean up files
    if project.thumbnail and os.path.exists(project.thumbnail):
        os.remove(project.thumbnail)
    if project.file_url and os.path.exists(project.file_url):
        os.remove(project.file_url)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

# ─── PODCAST CRUD ──────────────────────────────────

@app.route('/admin/podcast/add', methods=['POST'])
@login_required
def add_podcast():
    title = request.form.get('title')
    description = request.form.get('description')
    episode_number = int(request.form.get('episode_number', 1))
    duration = request.form.get('duration', '30 min')
    date_str = request.form.get('date', datetime.now(pytz.timezone('UTC')).strftime('%b %d, %Y'))

    cover = None
    if 'cover_image' in request.files:
        cover = save_file(request.files['cover_image'], 'podcasts')

    audio = None
    if 'audio_file' in request.files:
        audio = save_file(request.files['audio_file'], 'podcasts')

    podcast = Podcast(
        title=title, description=description, episode_number=episode_number,
        audio_url=audio, cover_image=cover, duration=duration, date=date_str
    )
    db.session.add(podcast)
    db.session.commit()
    flash('Podcast added!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/podcast/delete/<int:id>')
@login_required
def delete_podcast(id):
    podcast = Podcast.query.get_or_404(id)
    if podcast.cover_image and os.path.exists(podcast.cover_image):
        os.remove(podcast.cover_image)
    if podcast.audio_url and os.path.exists(podcast.audio_url):
        os.remove(podcast.audio_url)
    db.session.delete(podcast)
    db.session.commit()
    flash('Podcast deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

# ─── BLOG CRUD ──────────────────────────────────

@app.route('/admin/blog/add', methods=['POST'])
@login_required
def add_blog():
    title = request.form.get('title')
    category = request.form.get('category', 'Economics')
    description = request.form.get('description')
    author_name = request.form.get('author_name', 'Staff Writer')
    author_initials = request.form.get('author_initials', 'SW')
    read_time = request.form.get('read_time', '5 min read')
    date_str = request.form.get('date', datetime.now(pytz.timezone('UTC')).strftime('%b %Y'))

    image = None
    if 'image' in request.files:
        image = save_file(request.files['image'], 'blogs')

    blog = Blog(
        title=title, category=category, description=description,
        author_name=author_name, author_initials=author_initials,
        read_time=read_time, image_url=image, date=date_str
    )
    db.session.add(blog)
    db.session.commit()
    flash('Blog added!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/blog/delete/<int:id>')
@login_required
def delete_blog(id):
    blog = Blog.query.get_or_404(id)
    if blog.image_url and os.path.exists(blog.image_url):
        os.remove(blog.image_url)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

# ─── INITIATIVE CRUD ──────────────────────────────────

@app.route('/admin/initiative/add', methods=['POST'])
@login_required
def add_initiative():
    title = request.form.get('title')
    description = request.form.get('description')
    icon = request.form.get('icon', 'fa-chart-bar')
    initiative = Initiative(title=title, description=description, icon=icon)
    db.session.add(initiative)
    db.session.commit()
    flash('Initiative added!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/initiative/delete/<int:id>')
@login_required
def delete_initiative(id):
    initiative = Initiative.query.get_or_404(id)
    db.session.delete(initiative)
    db.session.commit()
    flash('Initiative deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

# ─── Serve uploaded files ──────────────────────────

@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)

# ─── Create admin user on first run ────────────────

with app.app_context():
    db.create_all()
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(
            username='admin',
            password_hash=generate_password_hash('Adminthinking123')
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
