import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from flask import send_from_directory
from .helper import get_uploaded_images
from app.models import UserProfile
from .forms import LoginForm
from app.forms import UploadForm
from . import app
###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        file = form.image.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('upload'))
    return render_template('upload.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():
        user = UserProfile.query.filter_by(username=form.username.data).first()

        # Checks if user exists and password matches
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('You have been successfully logged in.', 'Success')
            return redirect(url_for('upload')) 

        flash('Invalid username or password. Please try again.', 'Danger')
    
    return render_template('login.html', form=form)

@app.route('/uploads/<filename>')
def get_image(filename):
    uploads_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads_dir, filename)

@app.route('/files')
@login_required
def files():
    image_files = get_uploaded_images(app)
    return render_template('files.html', image_files=image_files)
# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'Success')
    return redirect(url_for('home'))
###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
