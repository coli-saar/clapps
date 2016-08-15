import datetime
from time import gmtime, strftime, localtime
import os
import traceback

import flask
from flask import render_template
from flask_login import login_required, login_user, logout_user
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename, redirect
from wtforms.fields.core import BooleanField, DateTimeField
from wtforms.fields.simple import HiddenField
from wtforms.validators import ValidationError
from flask import request, flash

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from init import *

from wtforms import Form, StringField, validators, SelectField, IntegerField, TextAreaField, BooleanField, FileField, \
    TextField, PasswordField
from tables import *

import mail


@app.route("/", methods=["GET",])
def index():
    return render_template("index.html", form = ApplicationForm(), conf=conf)

@app.route("/", methods=["POST",])
def post_application():
    code = conf.get("application", "code")
    form = ApplicationForm(request.form)

    if form.validate():
        remote_cv_file = request.files[form.cv_file.name]

        if remote_cv_file.filename == '':
            form.cv_file.errors.append("Please specify a PDF file which contains your CV.")
            return render_template("index.html", form=form, conf=conf)

        elif not allowed_file(remote_cv_file.filename):
            form.cv_file.errors.append("File must be of one of these types: " + " ".join(ALLOWED_EXTENSIONS))
            return render_template("index.html", form=form, conf=conf)

        # disability = 1 if form.disability.data else 0
        new_app = Application(firstname=form.firstname.data, lastname=form.lastname.data,
                              birthday=form.birthday.data, application_time=datetime.datetime.now(),
                              level=form.level.data, code=code,
                              nationality=form.nationality.data, email=form.email.data,
                              affiliation=form.affiliation.data, aff_city=form.aff_city.data,
                              aff_country=form.aff_country.data, status=0)

        try:
            # store all data from application form
            session.add(new_app)
            session.commit()

            id = new_app.id

            lor1 = Letter(app_id=id, name=form.lor1_name.data, email=form.lor1_email.data, affiliation=form.lor1_affiliation.data)
            session.add(lor1)

            lor2 = Letter(app_id=id, name=form.lor2_name.data, email=form.lor2_email.data, affiliation=form.lor2_affiliation.data)
            session.add(lor2)

            degree = Degree(app_id=id, university=form.deg_university.data, city=form.deg_city.data, degree=form.deg_degree.data, country=form.deg_country.data, subject=form.deg_subject.data, year=form.deg_year.data)
            session.add(degree)

            session.commit()

            # store uploaded CV
            file_path = cv_filename_from_data(id, form.lastname.data)
            remote_cv_file.save(file_path)

            # notify contact person
            mail.send(id, clapps_contact, "Apps@Coli Application %d: %s %s" % (id, form.firstname.data, form.lastname.data),
                      render_template("contact_notification.txt", form=form, id=id))

            # notify applicant
#            mail.send(id, "%s %s <%s>" % (form.firstname.data, form.lastname.data, form.email.data),
#                      "Job application submitted", render_template("applicant_notification.txt", form=form, id=id, conf=conf))

            timestamp = strftime("%d %b %Y at %H:%M:%S", localtime())
            return render_template("confirm.html", form=form, id=id, timestamp=timestamp, conf=conf)

        except Exception as e:
            print("exception: %s" % str(e))
            print(traceback.format_exc())
            flash("An error occurred while adding your application. If the problem persists, please get in touch with %s" % (clapps_contact))
            return render_template("index.html", form=form, conf=conf)

    else:
        print("validation")
        return render_template("index.html", form=form, conf=conf)




ALLOWED_EXTENSIONS = ["pdf"]

def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


class ApplicationForm(Form):
    email = StringField("Email", validators=[validators.InputRequired(), validators.Email()], render_kw={"placeholder": "Enter your email address"})
    firstname = StringField("First name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter your first name"})
    lastname = StringField("Last name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter your last (family) name"})
    birthday = DateTimeField("Date of birth", format="%Y/%m/%d", render_kw={"placeholder": "Enter your birthday (YYYY/MM/DD)"})
    level = SelectField("Level", choices=[("Postdoc", "Postdoc"), ("PhD Student", "PhD Student")])
    nationality = SelectField("Nationality", choices=country_list)
    affiliation = StringField("Affiliation", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter your affiliation"})
    aff_city = StringField("City", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the city where your affiliation is located"})
    aff_country = SelectField("Country", choices=country_list)

    cv_file = FileField(u'Your CV', [])

    deg_degree = StringField("Degree", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the degree (PhD, MSc, etc.)"})
    deg_subject = StringField("Subject", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the subject of the degree (computational linguistics, computer science, etc.)"})
    deg_year = IntegerField("Year", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the year in which the degree was (or will be) awarded"})
    deg_university = StringField("University", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the university that awarded the degree"})
    deg_city = StringField("City", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the city where this university is located"})
    deg_country = SelectField("Country", choices=country_list)

    lor1_name = StringField("Name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the name of reference #1"})
    lor1_email = StringField("Email", validators=[validators.InputRequired(), validators.Email()], render_kw={"placeholder": "Enter the email address of reference #1"})
    lor1_affiliation = StringField("Affiliation", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the affiliation of reference #1"})

    lor2_name = StringField("Name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the name of reference #2"})
    lor2_email = StringField("Email", validators=[validators.InputRequired(), validators.Email()], render_kw={"placeholder": "Enter the email address of reference #2"})
    lor2_affiliation = StringField("Affiliation", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the affiliation of reference #2"})


#######################################################################################
## admin access
#######################################################################################

@app.route("/show-applications.html", methods=["GET",])
@login_required
def show_applications():
    code = conf.get("application", "code")
    applications = session.query(Application).filter(Application.code == code).all()
    return render_template("show-applications.html", conf=conf, applications=applications, baseurl=baseurl)


@app.route("/show-application.html", methods=["GET",])
@login_required
def show_application():
    # TODO - check that ID is defined and an int

    id = int(request.args.get('id'))
    application = session.query(Application).filter(Application.id == id).first()
    return render_template("show-application.html", application=application, form=ShowApplicationForm(status=application.status, comments=application.comments), baseurl=baseurl)

@app.route("/show-application.html", methods=["POST",])
@login_required
def update_notes():
    id = int(request.args.get('id'))
    application = session.query(Application).filter(Application.id == id).first()
    form = ShowApplicationForm(request.form)
    return_to_overview_page = "update_and_return" in request.form

    if form.validate():
        if form.delete.data == "Delete!":
            session.query(Application).filter(Application.id == id).delete()
            session.commit()

            flash("Deleted application %d: %s, %s" % (application.id, application.lastname, application.firstname))
            return_to_overview_page = True

        else:
            application.comments = form.comments.data
            application.status = int(form.status.data)
            session.commit()

    if return_to_overview_page:
        return redirect(baseurl + "show-applications.html", code=302)
    else:
        return render_template("show-application.html", application=application, form=form, baseurl=baseurl)

class ShowApplicationForm(Form):
    status = SelectField("Change Status", choices=status_choices)
    comments = TextAreaField('Notes')
    delete = StringField("Delete")



#######################################################################################
## authentication
#######################################################################################

baseurl = conf.get("server", "path")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = baseurl + "login"
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id):
    return users[user_id]


@app.route('/login', methods=['GET',])
def unauthorized():
    # flask-login gave us a "next" argument in GET /login;
    # after that, we hide it in a hidden field so the POST requests can see it too
    form = LoginForm(request.form, next=baseurl + request.args.get("next")[1:])
    return render_template('login.html', form=form, baseurl=baseurl)


@app.route('/login', methods=['POST',])
def do_unauthorized():
    form = LoginForm(request.form)

    if form.validate():
        user = None
        for key, value in users.items():
            if form.name.data == value.id and form.passwd.data == value.passwd:
                user = value
                break

        if user:
            login_user(user)
            return redirect(baseurl + form.next.data[1:]) # strip leading /
        
    return render_template('login.html', form=form, baseurl=baseurl)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(baseurl)

class LoginForm(Form):
    name = StringField("User name", validators=[validators.InputRequired()])
    passwd = PasswordField("Password", validators=[validators.InputRequired()])
    next = HiddenField("next")



#######################################################################################
## main
#######################################################################################

if __name__ == "__main__":
    port = int(conf.get("server", "port"))

    if conf.getboolean("server", "use_tornado"):
        # use Tornado web server to host Flask app

        print("Starting Tornado webserver on port %d." % port)

        all = logging.FileHandler('./tornado.log')
        access = logging.FileHandler("./tornado-access.log")

        logging.getLogger("tornado.access").addHandler(access)
        logging.getLogger("tornado.access").setLevel(logging.DEBUG)

        logging.getLogger("tornado.application").addHandler(all)
        logging.getLogger("tornado.general").addHandler(all)
        logging.getLogger("tornado.application").setLevel(logging.DEBUG)
        logging.getLogger("tornado.general").setLevel(logging.DEBUG)

        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(port)
        IOLoop.instance().start()

    else:
        print("Starting builtin Flask webserver on port %d." % port)
        app.run(debug=True, host="0.0.0.0", port=port)





