import datetime
import traceback

from flask import render_template
from wtforms.fields.core import BooleanField, DateTimeField
from flask import request, flash

from init import *

from wtforms import Form, StringField, validators, SelectField, IntegerField, TextAreaField, BooleanField

from tables import *


@app.route("/", methods=["GET",])
def index():
    return render_template("index.html", form = ApplicationForm())

@app.route("/", methods=["POST",])
def post_application():
    form = ApplicationForm(request.form)

    if form.validate():
        disability = 1 if form.disability.data else 0
        new_app = Application(firstname=form.firstname.data, lastname=form.lastname.data,
                              birthday=form.birthday.data, application_time=datetime.datetime.now(),
                              level=form.level.data, disability=disability,
                              nationality=form.nationality.data, email=form.email.data)

        try:
            session.add(new_app)
            session.commit()

            id = new_app.id

            lor1 = Letter(app_id=id, firstname=form.lor1_firstname.data, lastname=form.lor1_lastname.data,
                          email=form.lor1_email.data, city=form.lor1_city.data, country=form.lor1_country.data)
            session.add(lor1)

            lor2 = Letter(app_id=id, firstname=form.lor2_firstname.data, lastname=form.lor2_lastname.data,
                          email=form.lor2_email.data, city=form.lor2_city.data, country=form.lor2_country.data)
            session.add(lor2)

            session.commit()

            return "Added record for %d" % id

        except Exception as e:
            print("exception: %s" % str(e))
            print(traceback.format_exc())
            flash("An error occurred while adding your application. If the problem persists, please get in touch with XXX")
            # TODO - XXX
            return render_template("index.html", form=form)

    else:
        print("validation")
        return render_template("index.html", form=form)




class ApplicationForm(Form):
    email = StringField("Email", validators=[validators.InputRequired(), validators.Email()], render_kw={"placeholder": "Enter your email address"})
    firstname = StringField("First name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter your first name"})
    lastname = StringField("Last name", validators=[validators.InputRequired()], render_kw={"placeholder": "Enter your last (family) name"})
    birthday = DateTimeField("Date of birth", format="%Y/%m/%d", render_kw={"placeholder": "Enter your birthday (YYYY/MM/DD)"})
    level = SelectField("Level", choices=[("Postdoc", "Postdoc"), ("PhD Student", "PhD Student")])
    disability = BooleanField("Disability")
    nationality = SelectField("Nationality", choices=country_list)

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

