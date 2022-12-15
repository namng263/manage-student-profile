from genericpath import exists
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import true
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' # We use SQLite3 for the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#student - course relationship
student_course = db.Table("student_course",
    db.Column("stuID", db.Integer, db.ForeignKey("student.id")),
    db.Column("courseID", db.Integer, db.ForeignKey("course.id"))
)

#skill - student relationship
skill_student = db.Table("skill_student",
    db.Column("skillID", db.Integer, db.ForeignKey("skill.id")),
    db.Column("stuID", db.Integer, db.ForeignKey("student.id"))
)

class studentData(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    stuID = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(100))
    dob = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phoneNum = db.Column(db.String(100))

    addToCourse = db.relationship("courseData", secondary=student_course, backref="student")

class accountData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer)
    password = db.Column(db.String(100))
    admin = db.Column(db.Integer)

#skill - course relationship
skill_course = db.Table("skill_course",
    db.Column("skillID", db.Integer, db.ForeignKey("skill.id")),
    db.Column("courseID", db.Integer, db.ForeignKey("course.id"))
)

class skillData(db.Model):
    __tablename__ = "skill"
    id = db.Column(db.Integer, primary_key=True)
    skillName = db.Column(db.String(100))
    
    addToCourse = db.relationship("courseData", secondary=skill_course, backref="softSkill")
    addToCV = db.relationship("studentData", secondary=skill_student, backref="cvSkill")

class courseData(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True)
    courseID = db.Column(db.String(100))
    courseVieName = db.Column(db.String(100))
    courseEngName = db.Column(db.String(100))
    courseStatus = db.Column(db.String(100))

@app.route("/")
def base():
    list = accountData.query.all()
    return render_template('login.html', accountList = list)

@app.route("/login", methods=["POST"])
def login():
        global currentAccount
        global currentStudent
        userID = int(request.form.get("userID"))
        password = request.form.get("password")
        account = accountData.query.filter_by(userID = userID).first()
        student = studentData.query.filter_by(stuID = userID).first()
        currentAccount = account
        currentStudent = student
        if currentAccount is None:
            return redirect(url_for("base"))
        else:
            if currentAccount.password == password:
                if currentAccount.admin == 1:
                    return redirect(url_for("adminHome"))
                else:
                    return redirect(url_for("stuHome"))
            else:
                return redirect(url_for("base"))

@app.route("/logout", methods=["POST"])
def logout():
    return redirect(url_for("base"))

@app.route("/adReturn", methods=["POST"])
def adReturn():
    return redirect(url_for("adminHome"))

# ***Student*** -start
@app.route("/stuHome")
def stuHome():
    return render_template('stuHome.html')

@app.route("/stuHome/access", methods=["POST"])
def stuAccess():
    if request.form["clickBtn"] == "manageAccount":
        return redirect(url_for("manageAccount"))
    if request.form["clickBtn"] == "viewCV":
        return redirect(url_for("cvList"))


# **Student manage account** -start
@app.route("/manageAccount")
def manageAccount():
    try:
        return render_template('manageAccount.html', currentAccount = currentAccount, currentStudent = currentStudent)
    except:
        return render_template('manageAccount.html', currentAccount = currentAccount, currentStudent = currentStudent)

@app.route("/manageAccount/editAccount", methods=["POST"])
def editAccount():
    id = int(request.form.get("id"))
    userID = request.form.get("userID")
    password = request.form.get("password")
    account = accountData.query.filter_by(id = id).first()
    
    currentAccount.userID = userID
    currentAccount.password = password
    account.userID = userID
    account.password = password
    
    db.session.commit()
    return redirect(url_for("manageAccount"))

@app.route("/manageAccount/editInfo", methods=["POST"])
def editInfo():
    stuID = request.form.get("stuID")
    name = request.form.get("name")
    dob = request.form.get("dob")
    email = request.form.get("email")
    phoneNum = request.form.get("phoneNum")
    student = studentData.query.filter_by(stuID = stuID).first()

    currentStudent.name = name
    currentStudent.dob = dob
    currentStudent.email = email
    currentStudent.phoneNum = phoneNum

    student.name = name
    student.dob = dob
    student.email = email
    student.phoneNum = phoneNum

    db.session.commit()
    return redirect(url_for("manageAccount"))
# **Student manage account** -end
# ***Student*** -end


# ***Teacher*** -start
@app.route("/adminHome")
def adminHome():
    return render_template('adminHome.html')

@app.route("/adminHome/access", methods=["POST"])
def adminAccess():
    if request.form["clickBtn"] == "manageStudent":
        return redirect(url_for("manageStudent"))
    if request.form["clickBtn"] == "manageCourse":
        return redirect(url_for("manageCourse"))
    if request.form["clickBtn"] == "manageSkill":
        return redirect(url_for("manageSkill"))
    if request.form["clickBtn"] == "editAccount":
        return redirect(url_for("manageAccount"))
    if request.form["clickBtn"] == "viewCV":
        return redirect(url_for("cvList"))

# **Teacher manage Student** -start
@app.route("/manageStudent")
def manageStudent():
        list = studentData.query.all()
        return render_template('manageStudent.html', studentList = list)    
@app.route("/manageStudent/searchStudent", methods=["GET"])
def searchStudent():   
    q = request.args.get('q')
    if q:
        list = studentData.query.filter(studentData.stuID.contains(q) |
        studentData.name.contains(q))
    else:
        list = studentData.query.all()
    return render_template('manageStudent.html', studentList = list)

@app.route("/manageStudent/addStudent", methods=["POST"])
def addStudent():
        name = request.form.get("name")
        stuID = int(request.form.get("stuID"))
        newStudent = studentData(stuID = stuID, name = name)
        newAccount = accountData(userID = stuID, password = 123456, admin = 0)
        try:
            db.session.add(newStudent)
            db.session.add(newAccount)
            if stuID is None:           
                return redirect(url_for("manageStudent"))  
            else:
                db.session.commit()
                return redirect(url_for("manageStudent"))
        except IntegrityError:
                return redirect(url_for("manageStudent"))


@app.route("/manageStudent/editStudent", methods=["POST"])
def editStudent():    
    id = int(request.form.get("id"))
    name = request.form.get("name")
    stuID = int(request.form.get("stuID"))
    student = studentData.query.filter_by(id = id).first()
    account = accountData.query.filter_by(userID = stuID).first()

    # update name
    if request.form["clickBtn"] == "update":
        student.name = name
    
    # delete student
    if request.form["clickBtn"] == "delete":
        db.session.delete(student)
        db.session.delete(account)
    
    db.session.commit()
    return redirect(url_for("manageStudent"))
# **Teacher manage Student** -end

# **Teacher manage course** -start
@app.route("/manageCourse")
def manageCourse():
        skillList = skillData.query.all()
        courseList = courseData.query.all()
        return render_template('manageCourse.html', skillList = skillList, courseList = courseList)
@app.route("/manageCourse/searchCourse", methods=['GET', 'POST'])
def searchCourse():
    q = request.args.get('q')
    if q:
        courseList = courseData.query.filter(courseData.courseID.contains(q)|
        courseData.courseVieName.contains(q)|
        courseData.courseEngName.contains(q))
        skillList = skillData.query.all()
    else:
        courseList = courseData.query.all()
        skillList = skillData.query.all()
    return render_template('manageCourse.html', skillList = skillList, courseList = courseList)
@app.route("/manageCourse/addCourse", methods=["POST"])
def addCourse():
    courseID = request.form.get("courseID")
    courseVieName = request.form.get("courseVieName")
    courseEngName = request.form.get("courseEngName")
    newCourse = courseData(courseID = courseID, courseVieName = courseVieName, courseEngName = courseEngName, courseStatus = "unfinish")

    db.session.add(newCourse)
    db.session.commit()
        

    skills = request.form.getlist("checkbox")
    for skill in skills:
        softSkill = skillData.query.filter_by(skillName = skill).first()
        relatedCourse = courseData.query.filter_by(courseID = courseID).first()
        softSkill.addToCourse.append(relatedCourse)
        db.session.commit()

    return redirect(url_for("manageCourse"))

@app.route("/manageCourse/editCourse", methods=["POST"])
def editCourse():
    global currentCourseID
    id = int(request.form.get("id"))
    courseID = request.form.get("courseID")
    courseVieName = request.form.get("courseVieName")
    courseEngName = request.form.get("courseEngName")
    course = courseData.query.filter_by(id = id).first()
    currentCourseID = id

    # view details
    if request.form["clickBtn"] == "view":
        return redirect(url_for("viewCourse"))
    else:
        # update courseName
        if request.form["clickBtn"] == "update":
            course.courseID = courseID
            course.courseVieName = courseVieName
            course.courseEngName = courseEngName
    
        # delete course
        if request.form["clickBtn"] == "delete":
            db.session.delete(course)
            
        db.session.commit()
        return redirect(url_for("manageCourse"))
# **Teacher manage course** -end

# **Teacher edit course detail** -start
@app.route("/viewCourse")
def viewCourse():
    currentCourse = courseData.query.filter_by(id = currentCourseID).first()
    softSkillList = currentCourse.softSkill
    studentList = currentCourse.student
    skillList = skillData.query.all()
    return render_template('viewCourse.html', currentCourse = currentCourse, softSkillList = softSkillList, skillList =skillList, studentList = studentList)

@app.route("/viewCourse/editSoftSkill", methods=["POST"])
def editSoftSkill():
    db.session.query(skill_course).filter_by(courseID = currentCourseID).delete()
    db.session.commit()

    skills = request.form.getlist("checkbox")
    for skill in skills:
        softSkill = skillData.query.filter_by(skillName = skill).first()
        relatedCourse = courseData.query.filter_by(id = currentCourseID).first()
        softSkill.addToCourse.append(relatedCourse)
        db.session.commit()

    return redirect(url_for("viewCourse"))

@app.route("/viewCourse/addStudent", methods=["POST"])
def addStudentToCourse():
    stuID = request.form.get("stuID")
    relatedStudent = studentData.query.filter_by(stuID = stuID).first()
    if relatedStudent is None:
        return redirect(url_for("viewCourse"))
    else:
        relatedCourse = courseData.query.filter_by(id = currentCourseID).first()
        relatedStudent.addToCourse.append(relatedCourse)
        db.session.commit()

    return redirect(url_for("viewCourse"))

@app.route("/viewCourse/failStudent", methods=["POST"])
def failStudent():
    id = int(request.form.get("id"))
    relatedStudent = studentData.query.filter_by(id = id).first()
    relatedCourse = courseData.query.filter_by(id = currentCourseID).first()

    relatedStudent.addToCourse.remove(relatedCourse)
    
    db.session.commit()
    return redirect(url_for("viewCourse"))

@app.route("/viewCourse/passStudent", methods=["POST"])
def passStudent():
    currentCourse = courseData.query.filter_by(id = currentCourseID).first()
    softSkillList = currentCourse.softSkill
    allStudent = currentCourse.student
    for student in allStudent:
        for skill in softSkillList:
            skill.addToCV.append(student)
    currentCourse.courseStatus = "finish"

    db.session.commit()
    return redirect(url_for("viewCourse"))
# **Teacher edit course detail** -end

# **Teacher manage softskill** -start
@app.route("/manageSkill")
def manageSkill():
        skillList = skillData.query.all()
        return render_template('manageSkill.html', skillList = skillList)

@app.route("/manageSkill/addSkill", methods=["POST"])
def addSkill():
    skillName = request.form.get("skillName")
    newSkill = skillData(skillName = skillName)
    
    db.session.add(newSkill)
    db.session.commit()
    return redirect(url_for("manageSkill"))

@app.route("/manageSkill/editSkill", methods=["POST"])
def editSkill():    
    id = int(request.form.get("id"))
    skillName = request.form.get("skillName")
    skill = skillData.query.filter_by(id = id).first()

    # update skillName
    if request.form["clickBtn"] == "update":
        skill.skillName = skillName
    
    # delete skill
    if request.form["clickBtn"] == "delete":
        db.session.delete(skill)
    
    db.session.commit()
    return redirect(url_for("manageSkill"))
# **Teacher manage softskill** -end
# ***Teacher*** -end

# **View CV** -start
@app.route("/cvList")
def cvList():
    studentList = studentData.query.all()
    return render_template('cvList.html', studentList = studentList)
@app.route("/cvList/searchCV", methods=['GET', 'POST'])
def searchCV():
    q = request.args.get('q')
    if q:
        studentList = studentData.query.filter(studentData.stuID.contains(q) |
        studentData.name.contains(q))
    else:
        studentList = studentData.query.all()
    return render_template('cvList.html', studentList = studentList)
@app.route("/viewCV", methods=["POST"])
def viewCV():
    currentStudentID = request.form.get("id")
    currentStudent = studentData.query.filter_by(id = currentStudentID).first()
    skillList = currentStudent.cvSkill
    return render_template('cv.html', currentStudent = currentStudent, skillList = skillList)
# **View CV** -end
        


if __name__ == '__main__':
    db.create_all()
    app.run(debug = True)
#Please use:   python app.py   to test run the app