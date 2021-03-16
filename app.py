from flask_bootstrap import Bootstrap
from flask import Flask, render_template, flash, request, redirect,\
                    session, url_for
from pymongo import MongoClient
from secrets import token_hex
from forms import *
import datetime

# Ρυθμίσεις εφαρμογής
DEBUG = True
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = token_hex(16)
client = MongoClient('mongodb://mongodb:27017')
infocinemas = client["InfoCinemas"]
users = infocinemas["users"]
movies = infocinemas["movies"]

# Αν δεν υπάρχει διαχειριστής στο σύστημα
if users.find_one({"is_admin":"False"}) is None:
    # εισάγει έναν
    users.insert_one({"name":"admin","email":"admin@site.com",
            "movies_seen":[], "passw":"admin", "is_admin":True})


# Εγγραφή ενός χρήστη
@app.route("/register", methods=["GET", "POST"])
def register():
    # φόρμα εγγραφής
    form  = RegisterForm()
    # μήνυμα προβολής
    msg   = ""
    # αρχικοποιεί το όνομα
    name  = None
    # αρχικοποιεί το email
    email = None
    # αρχικοποιεί τον κωδικό
    passw = None
    # αν ο χρήστης είναι συνδεδεμένος
    if "logged_in" in session and session["logged_in"] == True:
        # επιστρέφει στην αρχική με μήνυμα
        flash("Είσαι συνδεδεμένος", "success")
        return redirect(url_for("index"))
    # αν έχει συμπληρωθεί η φόρμα
    if form.validate_on_submit():
        # παίρνει το όνομα του χρήστη
        name = form.name.data
        form.name.data = '' 
        # παίρνει το email του χρήστη
        email = form.email.data
        form.email.data = '' 
        # βρίσκει αν υπάρχει χρήστης με αυτό το email
        us = users.find({"email":email})
        # αν υπάρχει
        if us.count() == 1:
            # φτιάχνει το μήνυμα για να ενημερώσει ότι το email δεν είναι διαθέσιμο
            flash("Το email δεν είναι διαθέσιμο","warning")
            # επιστρέφει στην σελίδα το μήνυμα
            return render_template('register.html', form=form, name=name,\
                    email=email, passw=passw, message=msg)
        # παίρνει τον κωδικό
        passw = form.passw.data
        form.passw.data = ''
        # φτιάχνει την εγγραφή 
        entry = {"name":name, "email":email, "passw":passw,\
                "movies_seen":[], "is_admin":False}
        # εισάγει την εγγραφή
        users.insert_one(entry)
        # δημιουργεί το μήνυμα για να ενημερώσει ότι ο χρήστης δημιουργήθηκε
        flash('Ο χρήστης δημιουργήθηκε', "success")
        # επιστρέφει στην σελίδα της σύνδεσης
        return redirect(url_for("login"))
    return render_template('register.html', form=form, name=name,\
                    email=email, passw=passw, message=msg)


# αρχική σελίδα
@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    return render_template('index.html')


@app.route("/admin_index", methods=["GET"])
def admin_index():
    # αν ο χρήστης δεν είναι admin
    if "logged_in" not in session or not session["logged_in"] \
        or not session["is_admin"]:
        # δημιουργεί το μήνυμα για να ενημερώσει
        flash("Δεν έχεις αρκετά δικαιώματα", "alert")
        # επιστρέφει στην αρχική σελίδα
        return redirect(url_for("index"))
    return render_template('admin-index.html')

# συνδέει χρήστη
@app.route("/login", methods=["GET", "POST"])
def login():
    # αν ο χρήστης είναι συνδεδεμένος
    if "logged_in" in session and session["logged_in"] == True:
        flash("Είσαι συνδεδεμένος", "success")
        return redirect(url_for("index"))
    email = None
    passw = None
    msg = ""
    form = LoginForm()
    if form.validate_on_submit():
        # παίρνει το email που έχει δώσει ο χρήστης
        email = form.email.data
        form.email.data = ''
        # παίρνει τον κωδικό
        passw = form.passw.data
        form.passw.data = ''
        # βρίσκει εάν υπάρχει ο χρήστης 
        user = users.find_one({"email":email})
        # εάν υπάρχει και έχει δώσει σωστά το κωδικό
        if user is not None and user["passw"] == passw:
            # τον συνδέει
            flash("Είσαι συνδεδεμένος", "success")
            session['logged_in'] = True
            session['is_admin'] = user["is_admin"]
            session['email'] = user["email"]
        # αλλιώς
        else:
            # εμφανίζει κατάλληλο μήνυμα και επιστρέφει στην αρχική σελίδα
            flash("Λάθος δεδομένα αυθεντικοποίησης", "danger")
            session['logged_in'] = False
            return redirect(url_for("index"))
        if session["is_admin"]:
            # αν είναι διαχειριστής τον στέλνει στην σελίδα των διαχειριστών
            return redirect(url_for("admin_index"))
        return redirect(url_for("index"))

    return render_template('login.html', form=form, email=email,\
                        passw=passw, message=msg)

# προσθέτει ταινία
@app.route('/add_movie', methods=["GET", "POST"])
def add_movie():
    # ελέγχει εάν ο χρήστης έχει τα δικαιώματα
    if "logged_in" not in session or session["logged_in"] == False \
            or not session['is_admin']:
        flash("Δεν έχεις δικαιώματα για να προσθέσεις ταινία", "danger")
        return redirect(url_for("index"))
    form = MovieForm()
    title = ''
    year = ''
    desc = ''
    timedate = ''
    tickets = 0
    if form.validate_on_submit():
        # παίρνει τον τίτλο
        title = form.title.data
        form.title.data = ''
        # παίρνει το έτος
        year = form.year.data
        form.year.data = None
        # παίρνει την περιγραφή
        desc = form.desc.data
        form.desc.data = ''
        # παίρνει την ημερομηνία
        timedate = form.timedate.data
        form.timedate.data = None
        # παίρνει τα εισιτήρια
        tickets = form.tickets.data
        form.tickets.data = None
        # δημιουργεί την εγγραφή
        entry = {"title":title, "year":year, "desc":desc,\
                    "timedate":timedate, "tickets":tickets} 
        # αποθηκεύει την εγγραφή
        movies.insert_one(entry)
        # ενημερώνει τον χρήστη
        flash("Η ταινία προσθέτηκε", "success")
        return redirect(url_for("admin_index"))
    return render_template("add_movie.html", form=form, title=title,\
            year=year, desc=desc, timedate=timedate)


@app.route('/search_movie', methods=["GET", "POST"])
def search_movie():
    # ελέγχει εάν ο χρήστης έχει τα δικαιώματα
    if "logged_in" not in session or not session["logged_in"]:
        flash("Δεν είσαι συνδεδεμένος", "warning")
        return redirect(url_for("index"))
    form = MovieSearch()
    lst = []
    title = None
    msg = ""
    res = None
    if form.validate_on_submit():
        # παίρνει τον τίτλο
        title = form.title.data
        form.title.data = ''
        # αν ο χρήστης δεν έχει βάλει όνομα ταινίας
        if title == '':
            # βρίσκει όλες τις ταινίες
            res = movies.find()
        # αλλιώς
        else:
            # βρίσκει τις ταινίες με τον τίτλο
            res = movies.find({"title":title})
            # αρχικοποιεί την λίστα που θα αποθηκευτούν
            lst = []
            # ατέρμονος βρόγχος
            while True:
                try:
                    # βάζει την ταινία στη λίστα
                    lst.append(res.next())
                except:
                    # αν προκύψει πρόβλημα σπάει τον βρόγχο
                    break
        # αν δεν έχει βρεθεί κάποια ταινία
        if res.count() == 0:
            # ενημερώνει τον χρήστη
            flash("Δεν βρέθηκε καμία ταινία", "info")
            return redirect(url_for("index"))
        # επιστρέφει την συνάρτηση results
        return results(lst)

        #return redirect(url_for("results", data = lst))
    return render_template("search_movie.html", form=form, title=title)


@app.route('/results', methods=["GET","POST"])
def results(data):
    # ελέγχει εάν ο χρήστης είναι συνδεδεμένος
    if "logged_in" not in session or not session["logged_in"]:
        flash("Δεν είσαι συνδεδεμένος", "warning")
        return redirect(url_for("index"))
    return render_template("results.html", data=data)


@app.route('/reserve', methods=["GET", "POST"])
def reserve():
    # ελέγχει εάν ο χρήστης είναι συνδεδεμένος
    if "logged_in" not in session or not session["logged_in"]:
        flash("Δεν είσαι συνδεδεμένος", "warning")
        return redirect(url_for("index"))
    # παίρνει και χειρίζεται τα δεδομένα ταινίας
    data = request.args.get('data')
    data = data.replace("ObjectId","")
    data = eval(data)
    form = ReserveTickets()
    number = 0
    if form.validate_on_submit():
        # παίρνει τον αριθμό εισιτηρίων
        number = form.number.data
        form.number.data = None
        # δημιουργεί την εγγραφή
        movie = movies.find_one({"title":data["title"], \
                            "year":data["year"], "desc":data["desc"], \
                            "timedate":data["timedate"], \
                            "tickets":data["tickets"]})
        # αν δεν έχει βρεθεί ταινία
        if movie == None:
            # ενημερώνει τον χρήστη
            flash("Δεν βρέθηκε η ταινία", "warning")
            return redirect(url_for("index"))
        # αν υπάρχουν αρκετά εισιτήρια
        if int(movie["tickets"]) >= int(number):
            # φτιάχνει την ενημέρωση
            newvals = { "$set": { "tickets": \
                            str(int(movie["tickets"]) - int(number))}}
            # κάνει την ενημέρωση εισιτηρίων
            movies.update(movie, newvals)
            # ενημερώνει την εγγραφή που έχει ληφθεί
            movie["tickets"] = str(int(movie["tickets"]) - int(number))
            # παίρνει το email του χρήστη που έχει κάνει την εγγραφή
            email = session["email"]
            # παίρνει τον χρήστη
            query = users.find_one({"email":email})
            # προετοιμάζει την αλλαγή που θα γίνει
            newvals = {"$set": {"movies_seen": \
                        query["movies_seen"]+[movie]}}
            # ενημερώνει τον χρήστη
            users.update(query, newvals)
            # ενημερώνει τον χρήστη
            flash("Η κράτηση πραγματοποιήθηκε", "success")
            # αν είναι διαχειριστής
            if session["is_admin"]:
                # επιστρέφει στην σελίδα διαχειριστών
                return redirect(url_for("admin_index"))
            # αλλιώς επιστρέφει στην κανονική σελίδα
            return redirect(url_for("index"))
        else:
            # αλλιώς ενημερώνει πως δεν υπάρχουν αρκετά εισιτήρια
            flash("Δεν υπάρχουν αρκετά εισιτήρια", "warning")
            return render_template('reserve.html', form=form,\
                                            data=data)
    return render_template("reserve.html", form=form, data=data)


# διαγραφή ταινίας
@app.route('/delete_movie', methods=["GET", "POST"])
def delete_movie():
    # ελέγχει τα δικαιώματα του χρήστη
    if "logged_in" not in session or session["logged_in"] == False \
            or not session['is_admin']:
        flash("Δεν έχεις δικαιώματα για να διαγράψεις ταινία", "danger")
        return redirect(url_for("index"))

    # δίνει την φόρμα
    form = MovieDelete()
    # αρχικοποιεί τον τίτλο
    title = ''
    # αρχικοποιεί το μήνυμα
    msg = ''
    if form.validate_on_submit():
        # παίρνει τον τίτλο
        title = form.title.data
        form.title.data = ''
        # βρίσκει την ταινία
        res = movies.find({"title":title})
        # αν δεν έχει βρεθεί κάποια ταινία
        if res.count() == 0:
            # ενημερώνει τον χρήστη
            flash("Δεν βρέθηκε η ταινία", "alert")
            return redirect(url_for("admin_index"))
        # παίρνει την πρώτη ταινία ως την ταινία με το αργότερο έτος
        min_movie = res.next()
        # αποθηκεύει το έτος
        min_year = min_movie["year"]
        # ατέρμονος βρόγχος
        while True:
            try:
                # παίρνει την επόμενη ταινία
                current = res.next()
                # αν το έτος της είναι προγενέστερο
                if current["year"] < first_year:
                    # γίνεται αυτό το τωρινό ´ετος
                    first_year = current["year"]
                    # η τωρινή ταινία γινεται η ταινία με το μικρότερο έτος
                    min_movie = current 
            except:
                # αν προκύψει σφάλμα σπάει τον βρόγχο
                break
        # διαγράφει την ταινία
        movies.delete_one(min_movie)
        # ενημερώνει τον χρήστη
        flash("Η ταινία διαγράφηκε", "success")
        return redirect(url_for("admin_index"))
    return render_template("movie_delete.html", form=form, title=title,\
                                        message=msg)


@app.route('/create_admin', methods=["GET","POST"])
def create_admin():
    # ελέγχει τα δικαιώματα του χρήστη
    if "logged_in" not in session or session["logged_in"] == False \
            or not session['is_admin']:
        flash("Δεν έχεις δικαιώματα για να προσθέσεις διαχειριστή", "danger")
        return redirect(url_for("index"))
    form = RegisterForm()
    msg = ''
    name  = None
    email = None
    passw = None
    if form.validate_on_submit():
        # παίρνει το όνομα του χρήστη
        name = form.name.data
        form.name.data = ''
        # παίρνει το email
        email= form.email.data
        form.email.data = ''
        # βρίσκει αν υπάρχει χρήστης
        us = users.find({"email":email})
        # αν υπάρχει
        if us.count() == 1:
            # ενημέρωσε τον χρήστη
            flash("Υπάρχει ήδη χρήστης με αυτό το email", "danger")
            return render_template('register.html', form=form,\
                    name=name, email=email, passw=passw)
        # παίρνει τον κωδικό
        passw = form.passw.data
        form.passw.data = ''
        # φτιάχνει την εγγραφή
        entry = {"name":name, "email":email, "passw":passw,\
            "movies_seen":[], "is_admin":True}
        # εισάγει την εγγραφή
        users.insert_one(entry)
        # ενημερώνει πως δημιουργήθηκε
        flash("Ο διαχειριστής προσθέτηκε", "success")
        return redirect(url_for("admin_index"))
    return render_template('register.html', form=form, name=name,\
                        email=email, passw=passw, message=msg)


@app.route('/history', methods=["GET"])
def history():
    # ελέγχει εάν ο χρήστης είναι συνδεδεμένος
    if "logged_in" not in session or not session["logged_in"]:
        flash("Δεν είσαι συνδεδεμένος", "warning")
        return redirect(url_for("index"))
    # παίρνει το email
    email = session["email"]
    # παίρνει τις ταινίες του χρήστη
    movies = users.find_one({"email":email})["movies_seen"]
    # εμφανίζει τις ταινίες
    return render_template("history.html", data=movies)


@app.route('/update', methods=["GET","POST"])
def update():
    # ελέγχει τα δικαιώματα του χρήστη
    if "logged_in" not in session or session["logged_in"] == False \
            or not session['is_admin']:
        flash("Δεν έχεις δικαιώματα για να ενημερώσεις ταινία", "danger")
        return redirect(url_for("index"))
    form = MovieSearch()
    lst = []
    title = None
    msg = ""
    res = None
    if form.validate_on_submit():
        # παίρνει τον τίτλο
        title = form.title.data
        form.title.data = ''
        # αν ο χρήστης δεν έχει βάλει όνομα ταινίας
        if title == '':
            # βρίσκει όλες τις ταινίες
            res = movies.find()
        else:
            # βρίσκει τις ταινίες με τον τίτλο
            res = movies.find({"title":title})
            # δημιουργεί κενή λίστα για τα αποτελέσματα
            lst = []
            # ατέρμονος βρόγχος
            while True:
                try:
                    # βάζει κάθε αποτέλεσμα στη λίστα
                    lst.append(res.next())
                except:
                    # όταν προκύψει πρόβλημα σταματάει τον βρόγχο
                    break
        # αν δεν έχει βρεθεί ταινία
        if res.count() == 0:
            # ενημερώνει τον χρήστη
            flash("Δεν βρέθηκε ταινία", "danger")
            return redirect(url_for("admin_index"))
        # επιστρέφει τα αποτελέσματα 
        return update_results(data=lst)
    return render_template("search_update.html", form=form, title=title)

        
@app.route('/update_results', methods=["GET", "POST"])
def update_results(data):
    # ελέγχει τα δικαιώματα του χρήστη
    if "logged_in" not in session or session["logged_in"] == False \
            or not session['is_admin']:
        flash("Δεν έχεις δικαιώματα για να ενημερώσεις ταινία", "danger")
        return redirect(url_for("index"))
    # εκτυπώνει τα αποτελέσματα
    return render_template("update_results.html", data=data)


@app.route("/update_movie", methods=["GET","POST"])
def update_movie():
    # ελέγχει τα δικαιώματα του χρήστη
    if "logged_in" not in session or session["logged_in"] == False \
            or not session['is_admin']:
        flash("Δεν έχεις δικαιώματα για να ενημερώσεις ταινία", "danger")
        return redirect(url_for("index"))
    # παίρνει τα δεδομένα
    data = request.args.get('data')
    data = data.replace("ObjectId","")
    data = eval(data)
    form = UpdateForm()
    title = ''
    year = ''
    desc = ''
    timedate = ''
    tickets = 0
    # αν δεν έχει βρεθεί ταινία
    if data == None:
        # ενημερώνει τον χρήστη
        flash("Δεν βρέθηκε η ταινία", "warning")
        return redirect(url_for("index"))
    if form.validate_on_submit():
        # βρίσκει την ταινία
        movie = movies.find_one({"title":data["title"], \
                            "year":data["year"], "desc":data["desc"], \
                            "timedate":data["timedate"], \
                            "tickets":data["tickets"]})
        # αν δεν έχει βρει ταινία
        if movie == None:
            # ενημερώνει τον χρήστη
            flash("Δεν βρέθηκε η ταινία", "danger")
            return redirect(url_for("admin_index"))
        # παίρνει τον τίτλο
        title = request.form.get("title")
        form.title.data = ''
        αν έχει δωθεί τίτλος
        if title != '':
            # ενημερώνει τις εγγραφές
            newvals = { "$set": { "title": title}}
            movies.update(movie, newvals)
            movie["title"] = title
            data["title"] = title
        year = request.form.get("year")
        form.year.data = None
        # αν έχει δοθεί έτος
        if year != '':
            # ενημερώνει τις εγγραφές
            newvals = { "$set": { "year": year}}
            movies.update(movie, newvals)
            movie["year"] = year
            data["year"] = year
        desc = request.form.get("desc")
        form.desc.data = ''
        # αν έχει δοθεί περίληψη
        if desc != '':
            # ενημερώνει τις εγγραφές
            newvals = { "$set": { "desc": desc}}
            movies.update(movie, newvals)
            movie["desc"] = desc
            data["desc"] = desc
        timedate = request.form.get("timedate")
        form.timedate.data = ''
        # αν έχει δοθεί χρονολογία
        if timedate != '':
            # ενημερώνει 
            newvals = { "$set": { "timedate": timedate}}
            movies.update(movie, newvals)
            movie["timedate"] = timedate
            data["timedate"] = timedate
        tickets = request.form.get("tickets")
        form.tickets.data = None
        # αν έχουν δοθεί εισιτήρια
        if tickets != '':
            # ενημερώνει τις εγγραφές
            newvals = { "$set": { "tickets": tickets}}
            movies.update(movie, newvals)
            movie["tickets"] = tickets
            data["tickets"] = tickets
        flash("Οι αλλαγές αποθηκεύτικαν", "success")
        return redirect(url_for("admin_index"))
    return render_template("update_item.html", form=form, item=data)


@app.route('/logoff', methods=["GET"])
def logoff():
    # αν είναι συνδεδεμένος χρήστης τότε τον αποσυνδέει
    if "logged_in" in session and session['logged_in'] == True:
        session['logged_in'] = False
        session['is_admin'] = False
        session['email'] = ''
        # εμφανίζει μήνμυ στον χρήστη
        flash("Αποσυνδέθηκες", "success")
        return redirect(url_for("index"))
    # αν δεν είναι συνδεδεμένος τότε τον ενημερώνει
    flash("Δεν είσαι συνδεδεμένος", "warning")
    return redirect(url_for("index"))


@app.route('/reset', methods=["GET","POST"])
def reset():
    # αν ο χρήστη δεν είναι συνδεδεμένος
    if "logged_in" not in session or session['logged_in'] == False:
        # τον ενημερώνει
        flash("Δεν είσαι συνδεδεμένος", "alert")
        return redirect(url_for("index"))

    form = ResetPassword()
    old_pass = ''
    new_pass = ''
    if form.validate_on_submit():
        # παίρνει το παλιό κωδικό
        old_pass = form.current.data
        form.current.data = ''
        # παίρνει τον καινούργιο κωδικό
        new_pass = form.passw.data
        form.passw.data = ''
        # παίρνει το email του χρήστη
        email = session["email"]
        # βρίσκει τον χρήστη
        us = users.find_one({"email":email})
        # παίρνει τον τωρινό κωδικό
        cur_pass = us["passw"]
        # αν ο κωδικός που έδωσε είναι ίδιος με αυτόν που έχει
        if cur_pass == old_pass:
            # τότε κάνει την ενημέρωση
            newvals = { "$set": { "passw": new_pass}}
            users.update(us, newvals)
            # ενημερώνει τον χρήστη ότι ο κωδικός άλλαξε
            flash("Ο κωδικός ενημερώθηκε", "success")
            if session["is_admin"]:
                # επιστρέφει στο μενού των διαχειριστών
                return redirect(url_for("admin_index"))
            # επιστρέφει στο μενού των κανονικών χρηστών
            return redirect(url_for("index"))
        else:
            # ενημερώνει οτι ο κωδικός δεν έχει αλλάξει
            flash("Ο κωδικός που έδωσες δεν είναι σωστός", "alert")
            return render_template("password.html", form=form)
    return render_template("password.html", form=form)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
