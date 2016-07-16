import datetime
import os
import traceback

from flask import render_template
from werkzeug.utils import secure_filename
from wtforms.fields.core import BooleanField, DateTimeField
from wtforms.validators import ValidationError
from flask import request, flash

from init import *

from wtforms import Form, StringField, validators, SelectField, IntegerField, TextAreaField, BooleanField, FileField

from tables import *

import mail


@app.route("/", methods=["GET",])
def index():
    return render_template("index.html", form = ApplicationForm())

@app.route("/", methods=["POST",])
def post_application():
    form = ApplicationForm(request.form)

    if form.validate():
        remote_cv_file = request.files[form.cv_file.name]

        if remote_cv_file.filename == '':
            form.cv_file.errors.append("Please specify a PDF file which contains your CV.")
            return render_template("index.html", form=form)

        elif not allowed_file(remote_cv_file.filename):
            form.cv_file.errors.append("File must be of one of these types: " + " ".join(ALLOWED_EXTENSIONS))
            return render_template("index.html", form=form)

        disability = 1 if form.disability.data else 0
        new_app = Application(firstname=form.firstname.data, lastname=form.lastname.data,
                              birthday=form.birthday.data, application_time=datetime.datetime.now(),
                              level=form.level.data, disability=disability,
                              nationality=form.nationality.data, email=form.email.data)

        try:
            # store all data from application form
            session.add(new_app)
            session.commit()

            id = new_app.id

            lor1 = Letter(app_id=id, firstname=form.lor1_firstname.data, lastname=form.lor1_lastname.data, email=form.lor1_email.data, city=form.lor1_city.data, country=form.lor1_country.data)
            session.add(lor1)

            lor2 = Letter(app_id=id, firstname=form.lor2_firstname.data, lastname=form.lor2_lastname.data, email=form.lor2_email.data, city=form.lor2_city.data, country=form.lor2_country.data)
            session.add(lor2)

            degree = Degree(app_id=id, university=form.deg_university.data, city=form.deg_city.data, degree=form.deg_degree.data, country=form.deg_country.data, subject=form.deg_subject.data, year=form.deg_year.data)
            session.add(degree)

            session.commit()

            # store uploaded CV
            filename = secure_filename("%d-%s.pdf" % (id, form.lastname.data))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            remote_cv_file.save(file_path)

            # notify contact person
            mail.send(id, clapps_contact, "CLAPPS Application %d: %s %s" % (id, form.firstname.data, form.lastname.data),
                      render_template("contact_notification.txt", form=form, id=id))

            # notify applicant
            mail.send(id, "%s %s <%s>" % (form.firstname.data, form.lastname.data, form.email.data),
                      "Job application submitted", render_template("applicant_notification.txt", form=form, id=id, conf=conf))

            return render_template("confirm.html", form=form)

        except Exception as e:
            print("exception: %s" % str(e))
            print(traceback.format_exc())
            flash("An error occurred while adding your application. If the problem persists, please get in touch with %s" % (clapps_contact))
            return render_template("index.html", form=form)

    else:
        print("validation")
        return render_template("index.html", form=form)




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
    disability = BooleanField("Disability")
    nationality = SelectField("Nationality", choices=country_list)

    cv_file = FileField(u'Your CV', [])

    deg_degree = StringField("Degree", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the degree (PhD, MSc, etc.)"})
    deg_subject = StringField("Subject", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the subject of the degree (computational linguistics, computer science, etc.)"})
    deg_year = IntegerField("Year", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the year in which the degree was (or will be) awarded"})
    deg_university = StringField("University", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the university that awarded the degree"})
    deg_city = StringField("City", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the city where this university is located"})
    deg_country = SelectField("Country", choices=country_list)

    lor1_firstname = StringField("First name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the first name of reference #1"})
    lor1_lastname = StringField("Last name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the last name of reference #1"})
    lor1_email = StringField("Email", validators=[validators.InputRequired(), validators.Email()], render_kw={"placeholder": "Enter the email address of reference #1"})
    lor1_affiliation = StringField("Affiliation", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the affiliation of reference #1"})
    lor1_city = StringField("City", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the city where the affiliation of reference #1 is located"})
    lor1_country = SelectField("Country", choices=country_list)

    lor2_firstname = StringField("First name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the first name of reference #2"})
    lor2_lastname = StringField("Last name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the last name of reference #2"})
    lor2_email = StringField("Email", validators=[validators.InputRequired(), validators.Email()], render_kw={"placeholder": "Enter the email address of reference #2"})
    lor2_affiliation = StringField("Affiliation", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter the affiliation of reference #2"})
    lor2_city = StringField("City", validators=[validators.InputRequired()], render_kw={ "placeholder": "Enter the city where the affiliation of reference #2 is located"})
    lor2_country = SelectField("Country", choices=country_list)


#######################################################################################
## main
#######################################################################################

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

