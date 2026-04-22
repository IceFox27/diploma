from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/about')
def about():
    return render_template('main/about.html')

@main.route('/portfolio')
def portfolio():
    return render_template('main/portfolio.html')

@main.route('/services')
def services():
    return render_template('main/services.html')

@main.route('/jobs')
def jobs():
    return render_template('main/jobs.html')

@main.route('/contacts')
def contacts():
    return render_template('main/contacts.html')

@main.route('/blog')
def blog():
    return render_template('main/blog.html')