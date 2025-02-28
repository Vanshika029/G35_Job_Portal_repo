from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required, current_user
from datetime import datetime
from sqlalchemy import func
import functools

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "welcome"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'




class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(10), nullable=False)  

    def save_hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_hash_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Join(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Ensure it fetches the correct user

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        mobile = request.form.get("mobile")
        role = request.form.get("role")  
        # print("register",username,email,password,mobile,role)
        # if not username or not email or not password or not mobile:
        #     flash("All fields are required.", "danger")
        #     return redirect(url_for("register"))
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("User already exists. Please log in.", "danger")
            return redirect(url_for("login"))

       
        user_data = User(username=username, email=email, mobile=mobile,role=role)
        user_data.save_hash_password(password)

        # Save to database
        db.session.add(user_data)
        db.session.commit()
        flash("User registered successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html") 

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user_data = User.query.filter_by(email=email).first()

        if user_data and user_data.check_hash_password(password):
            login_user(user_data)
            # print("User logged in:", user_data.email, "Role:", user_data.role)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        
        flash("Invalid email or password", "danger")

    return render_template("login.html")




@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# @login_manager.user_loader
# def load_user(user_id):
#     return db.session.get(User, int(user_id))

# class Job(db.Model):
#     __tablename__ = "jobs"
#     id = db.Column(db.Integer, primary_key=True)
#     company = db.Column(db.String(100), nullable=False)
#     job_title = db.Column(db.String(100), nullable=False)
#     salary = db.Column(db.String(50))
#     location = db.Column(db.String(100), nullable=False)
#     posted_at = db.Column(db.DateTime, default=datetime.utcnow)




    

# @app.route("/join", methods=["GET", "POST"])
# # @login_required
# def join():
#     # print("User Authenticated:", current_user.is_authenticated)
#     # print("User Role:", current_user.role)
#     # # Only admin users are allowed to post job info
#     # if current_user.role != 'admin':
#     #   flash("unauthorized: Only admins can post job information.", "danger")
#     #   return render_template("index.html")
    
#     if request.method == "POST":
        
#         company = request.form.get("company")
#         job_title = request.form.get("job_title")
#         salary = request.form.get("salary")
#         location = request.form.get("location")

#         # Save the job posting
#         new_job = Join(company=company, job_title=job_title, salary=salary, location=location)
#         db.session.add(new_job)
#         db.session.commit()

#         flash("Job posted successfully!", "success")
#         return redirect(url_for("join"))
#     return render_template("join.html") 




@app.route("/join", methods=["GET", "POST"])
@login_required  # Ensures only logged-in users can access this route
def join():
    # Ensure only admins can post jobs
    if current_user.role != 'admin':
        flash("Unauthorized: Only admins can post job information.", "danger")
        return render_template("index.html")
    print(current_user.role,"role")
    if request.method == "POST":
        print("something")
        company = request.form.get("company")
        job_title = request.form.get("job_title")
        salary = request.form.get("salary")
        location = request.form.get("location") 
        # if not company or not job_title or not salary or not location:
        #     flash("All fields are required!", "warning")
        #     return redirect(url_for("jo"))

        # Save the job posting
        new_job = Join(company=company, job_title=job_title, salary=salary, location=location)
        db.session.add(new_job)
        db.session.commit()

        flash("Job posted successfully!", "success")
        return redirect(url_for("join"))

    return render_template("join.html")
    # jobs=Join.query.all()
    # return render_template("list.html" , jobs=jobs)


@app.route("/delete_job/<int:job_id>", methods=["POST"])
@login_required
def delete_job(job_id):
    # Ensure only admins can delete jobs
    if current_user.role != 'admin':
        flash("Unauthorized: Only admins can delete job information.", "danger")
        return redirect(url_for("join"))

    job = Join.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    
    flash("Job deleted successfully!", "success")
    return redirect(url_for("join"))


@app.route("/logout")
def logout():
    logout_user()
    flash("User  logged out successfully")
    return redirect(url_for("home"))


@app.route("/hero")
def hero():
    return render_template("hero.html") 

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/itjobs")
def itjobs():
    return render_template("itjobs.html")


@app.route("/it1")
def it1():
    return render_template("it1.html")

@app.route("/it2")
def it2():
    return render_template("it2.html")


@app.route("/sales")
def sales():
    return render_template("sales.html") 


@app.route("/sales1")
def sales1():
    return render_template("sales1.html")



@app.route("/sales2")
def sales2():
    return render_template("sales2.html")


@app.route("/marketing")
def marketing():
    return render_template("marketing.html")


@app.route("/marketing1")
def marketing1():
    return render_template("marketing1.html")

@app.route("/marketing2")
def marketing2():
    return render_template("marketing2.html")

@app.route("/data")
def data():
    return render_template("data.html")

@app.route("/data1")
def data1():
    return render_template("data1.html")

@app.route("/data2")
def data2():
    return render_template("data2.html")


@app.route("/hr")
def hr():
    return render_template("hr.html")

@app.route("/hr1")
def hr1():
    return render_template("hr1.html") 

@app.route("/hr2")
def hr2():
    return render_template("hr2.html") 

@app.route("/engineering")
def engineering():
    return render_template("engineering.html")

@app.route("/engineering1")
def engineering1():
    return render_template("engineering1.html")

@app.route("/engineering2")
def engineering2():
    return render_template("engineering2.html")


# jobs by demands
@app.route("/fresher")
def fresher():
    return render_template("fresher.html")

@app.route("/fresher1")
def fresher1():
    return render_template("fresher1.html")


@app.route("/fresher2")
def fresher2():
    return render_template("fresher2.html")

@app.route("/mnc")
def mnc():
    return render_template("mnc.html") 

@app.route("/mnc1")
def mnc1():
    return render_template("mnc1.html") 

@app.route("/mnc2")
def mnc2():
    return render_template("mnc2.html") 


@app.route("/remote")
def remote():
    return render_template("remote.html") 


@app.route("/remote1")
def remote1():
    return render_template("remote1.html") 


@app.route("/remote2")
def remote2():
    return render_template("remote2.html") 

@app.route("/work from home")
def work():
    return render_template("work.html") 

@app.route("/work from home")
def work1():
    return render_template("work1.html") 

@app.route("/work from home")
def work2():
    return render_template("work2.html")


@app.route("/walk")
def walk():
    return render_template("walk.html")


@app.route("/walk")
def walk1():
    return render_template("walk1.html")

@app.route("/walk")
def walk2():
    return render_template("walk2.html")

@app.route("/part")
def part():
    return render_template("part.html")

@app.route("/part1")
def part1():
    return render_template("part1.html")

@app.route("/part2")
def part2():
    return render_template("part2.html")

@app.route("/delhi")
def delhi():
    return render_template("delhi.html")

@app.route("/mumbai")
def mumbai():
    return render_template("mumbai.html") 

@app.route("/banglore") 
def banglore():
    return render_template("banglore.html")

@app.route("/hyderabad")
def hyderabad():
    return render_template("hyderabad.html") 

@app.route("/chennai") 
def chennai():
    return render_template("chennai.html") 

@app.route("/pune")
def pune():
    return render_template("pune.html")

@app.route("/tesla") 
def tesla():
    return render_template("tesla.html")

@app.route("/meta") 
def meta():
    return render_template("meta.html") 

@app.route("/list")
def list():
    return render_template("list.html")


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash("Unauthorized: Only admins can access the dashboard.", "danger")
        return redirect(url_for("home"))
    
    jobs = Join.query.all()
    return render_template("dashboard.html", jobs=jobs)

with app.app_context():
    # db.drop_all()  # Remove this lineEnsure all tables are created






    db.create_all()  # Ensure all tables are created
if __name__ == "__main__":
    app.run(debug=True)