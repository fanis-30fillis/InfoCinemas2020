from wtforms import Form, TextField, StringField,\
        SubmitField, PasswordField, IntegerField, DateTimeField,\
        BooleanField
from wtforms.validators import required, EqualTo, Length, NumberRange,\
        Optional, Email, InputRequired, ValidationError
from flask_wtf import FlaskForm

class RegisterForm(FlaskForm):
    name  = TextField("Όνομα χρήστη", validators=[InputRequired(message="Πρέπει να\
                                εισαχθεί όνομα χρήστη"), Length(min=4, max=20,\
                            message="Το όνομα χρήστη πρέπει να είναι από 4 έως 20\
                            χαρακτήρες")])
    email = TextField("Email χρήστη", validators=[InputRequired(message="Πρέπει να\
                                εισαχθεί email"), Email(message="Δεν έχει εισαχθεί\
                                    έγκυρο email")])
    passw  = PasswordField("Κωδικός χρήστη", validators=[InputRequired(message="Πρέπει να\
                                εισαχθεί κωδικός"),\
                    EqualTo("confirm", message="Οι κωδικοί πρέπει να\
                    είναι ίδιοι"), Length(min=8, max=64, message="Ο\
                    κωδικός πρέπει να είναι από 8 έως 64 χαρακτήρες")])
    confirm = PasswordField('Επιβεβαίωση Κωδικού')
    submit = SubmitField("Εγγραφή Χρήστη")


class LoginForm(FlaskForm):
    email = TextField("Email χρήστη", validators = [InputRequired(message="Πρέπει\
                                να εισαχθεί email"), Email(message="Δεν έχει\
                                εισαχθεί έγκυρο email")])
    passw  = PasswordField("Κωδικός χρήστη", validators = [InputRequired()])
    remember = BooleanField("Θυμήσου Με")
    submit = SubmitField("Σύνδεση Χρήστη")


class MovieForm(FlaskForm):
    title = TextField("Ονομα Ταινίας", validators=[InputRequired(message="Πρέπει να\
                                        δωθεί όνομα ταινίας")])
    year = IntegerField("Έτος Κυκλοφορίας", validators=[InputRequired(message="Πρέπει\
                                            να δωθεί το έτος κυκλοφορίας")])
    desc = TextField("Περιγραφή", validators=[InputRequired(message="Πρέπει να δωθεί\
                                            περιγραφή")])
    timedate = DateTimeField("Ημέρες και ώρες προβολής (ΗΗ/ΜΜ/ΕΕΕΕ\
                        Ώρα:Λεπτά)", validators=[InputRequired(message="Πρέπει να δωθεί σωστή\
                            Ημερομηνία (ΗΗ/ΜΜ/ΕΕΕΕ Ώρα:Λεπτά")],\
                         format="%d/%m/%Y %H:%M")
    tickets = IntegerField("Εισητήρια", validators=[InputRequired(message="Δεν έχει δωθεί\
                                            αριθμός εισιτηρίων"),\
                        NumberRange(min=1, message="Πρέπει να έχει\
                            δωθεί τουλάχιστον 1 εισιτήριο")])
    submit = SubmitField("Εισαγωγή Ταινίας")


class MovieSearch(FlaskForm):
    title = TextField("Ονομα Ταινίας")
    submit = SubmitField("Εύρεση Ταινίας")


class MovieDelete(FlaskForm):
    title = TextField("Ονομα Ταινίας", validators=[InputRequired(message="Πρέπει \
                                        να δωθεί το όνομα ταινίας")])
    submit = SubmitField("Διαγραφή Ταινίας")


class ReserveTickets(FlaskForm):
    number = IntegerField("Αριθμός Εισιτηρίων για κράτηση", validators=\
                        [InputRequired(message="Δεν έχει δωθεί αριθμός εισητιρίων"),\
                        NumberRange(min=1, message="Πρέπει να κρατηθεί τουλάχιστον 1\
                        εισιτήριο")])
    submit = SubmitField("Κράτηση")


class UpdateForm(FlaskForm):
    title = TextField("Ονομα Ταινίας", validators=[Optional()])
    year = IntegerField("Έτος Κυκλοφορίας",validators=[Optional()])
    desc = TextField("Περιγραφή",validators=[Optional()])
    timedate = DateTimeField("Ημέρες και ώρες προβολής (ΗΗ/ΜΜ/ΕΕΕΕ\
                        Ώρα:Λεπτά)", format="%d/%m/%Y %H:%M",
                        validators=[Optional()])
    tickets = IntegerField("Εισιτήρια", validators=\
                            [NumberRange(min=0, message="Δεν μπορεί να υπάρχει αρνητικός\
                                    αριθμός εισιτηρίων"), Optional()])
    submit = SubmitField("Ενημέρωση Ταινίας")



class ResetPassword(FlaskForm):
    current = PasswordField("Τωρινός Κωδικός", validators=[InputRequired(message="Δεν έχει δωθεί ο\
                                τωρινός κωδικός")])
    passw = PasswordField("Καινούργιος Κωδικός", validators=[InputRequired(message="Δεν έχει δωθεί ο\
                                καινούργιος κωδικός"),EqualTo("confirm", message="Οι κωδικοί πρέπει να\
                                είναι ίδιοι"), Length(min=8, max=64, message="Ο κωδικός πρέπει να είναι\
                                από 8 έως 64 χαρακτήρες")])
    confirm = PasswordField("Επιβεβαίωση Κωδικού")
    submit = SubmitField("Επιβεβαίωση Αλλαγής")