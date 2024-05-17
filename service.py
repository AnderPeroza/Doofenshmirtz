
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask import Flask, request, render_template, redirect, url_for, flash
from db import collectionUser,collectionCategory,collectionExam
from bson import ObjectId

app = Flask(__name__, template_folder="./template")
app.config['SECRET_KEY'] = "clave secreta"

def userLogin(confirm):
    if  confirm == 1:
        return True
    else:
        return False

userlog = False


def consultC():
    categories = collectionCategory.find()
    return categories

@app.route("/createCategory", methods=["GET", "POST"])

def createCategory():

   
    
    if request.method == "POST":
        
        name = request.form["name"]
        description = request.form["description"]
        collectionCategory.insert_one({"name":name, "description":description})
        flash("Categoría creada con éxito")
        
    return render_template("createCategory.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        comprobar = collectionUser.find_one({"username":username})
        if comprobar == None:
            collectionUser.insert_one({"username": username, "password": password})
            flash("User created successfully")
        else:
            flash("Usuario existente")
    return render_template("register.html")

@app.route("/createExam", methods=["GET", "POST"])
def createExam():
   
    categories = consultC()
    if  request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        sampleType = request.form["sampleType"]
        price = request.form["price"]
        indications = request.form["indications"]
        
        collectionExam.insert_one({"name":name, "category":category, "sampleType":sampleType,"price":price,"indications":indications})
        flash("Examen creado con éxito")
        return redirect(url_for("listExam"))
    return render_template("createExam.html", categories=categories)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username =request.form["username"]
        password = request.form["password"]
        user = collectionUser.find_one({"username":username})
        if user != None:
            if user['username']== username and user['password'] == password:
                flash("Sesion iniciada")
                userlog == True
                
            else:
                flash("Contraseña invalida")        
        else:
            flash("el usuario no existe")        
    return render_template("login.html")

@app.route("/", methods=["GET"])
def base():
    
    return render_template("base.html",userLogin = userlog)

@app.route("/logout")
def logout():
    userlog == True
    return redirect(url_for("base"))

@app.route("/list-exam", methods=["GET"])
def listExam():
    find = collectionExam.find()
    examen=[]
    
    for exam in find:

        ca = ''
        if exam['category'] != '':
            id = ObjectId(exam["category"])
            c = collectionCategory.find_one({"_id": id})
            ca = c['name']
    
        newExam = {"id":exam["_id"],
                   "name":exam["name"],
                   "category":ca,
                   "sampleType":exam["sampleType"],
                   "price":exam["price"],
                   "indications":exam["indications"]}
        
        examen.append(newExam)

    return render_template("examsList.html", exams = examen)

@app.route("/exam/<string:exam_id>", methods=["GET"])
def exam(exam_id):
    id = ObjectId(exam_id)
    examen = collectionExam.find_one({"_id": id})
    ca = ''
    if examen['category'] != '':
        idExam = ObjectId(examen["category"])
        c = collectionCategory.find_one({"_id": idExam})
        ca = c['name']

    


    return render_template("detailExam.html", exam=examen ,category = ca)

@app.route("/update_exam/<exam_id>",methods=["GET","POST"])
def updateExam(exam_id):
    id = ObjectId(exam_id)
    exam = collectionExam.find_one({"_id": id})
    category = consultC()
    if request.method == "POST":
        exam["name"] = request.form["name"]
        exam["category"] = request.form["category"]
        exam["sampleType"] = request.form["sampleType"]
        exam["price"] = request.form["price"]
        exam["indications"] = request.form["indications"]
        collectionExam.update_one({"_id": id}, {"$set": exam})

    return render_template("updateExam.html", exam = exam, categories = category)    

@app.route("/delete_exam/<string:exam_id>")
def deleteExam(exam_id):
    id = ObjectId(exam_id)
    collectionExam.delete_one({"_id": id})
    flash("Examen eliminado con éxito")
    return redirect(url_for("listExam"))



@app.route("/category/<string:category_id>", methods=["GET"])
def category(category_id):
    id = ObjectId(category_id)
    
    category = collectionCategory.find_one({"_id": id})
    return render_template("detailCategory.html", category = category)

@app.route("/update_category/<category_id>",methods=["GET","POST"])
def updateCategory(category_id):
    id = ObjectId(category_id)
    category = collectionCategory.find_one({"_id": id})
    if request.method == "POST":
        category["name"] = request.form["name"]
        category["description"] = request.form["description"]
        collectionCategory.update_one({"_id": id}, {"$set": category})

    return render_template("updateCategory.html", category = category)

@app.route("/delete_category/<string:category_id>")
def deleteCategory(category_id):
    id = ObjectId(category_id)
    collectionCategory.delete_one({"_id": id})

    exams = collectionExam.find()

    
    for exam in exams:
        exam['category'] = ''
        collectionExam.update_one({'_id': exam['_id']},{"$set": exam})
        
    flash("categoria eliminada con éxito")
    return redirect(url_for("listCategory"))  

@app.route("/list-category", methods=["GET"])
def listCategory():
    category = collectionCategory.find()

    return render_template("listCategory.html", categories = category)

@app.route("/report")
def report():


   

    exams_by_category = collectionCategory.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ])
    most_common_indication = collectionCategory.aggregate([
        {"$unwind": "$indications"},
        {"$group": {"_id": "$indications", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ])
    exams_by_price = collectionCategory.aggregate([
        {"$bucket": {"groupBy": "$price", "boundaries": [1, 100, 200, 300, 500, float("inf")]}}
    ])
    return render_template("report.html", exams_by_category=exams_by_category, most_common_indication=most_common_indication, exams_by_price=exams_by_price)
if __name__ == "__main__":
    c = consultC()
    print(c)
    app.run(debug=True)