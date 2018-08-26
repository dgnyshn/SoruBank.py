from flask import Flask ,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,SelectField,RadioField
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.secret_key = "soruBank"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "soruBank"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"


mysql = MySQL(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/questions")
def questions():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From sorular" 
    result = cursor.execute(sorgu)

    if result > 0 :
        questions = cursor.fetchall()
        return render_template("questions.html" , questions = questions)
    else:
        return render_template("questions.html")

    
    
    return render_template("questions.html")


@app.route("/about")
def about():
    return render_template("about.html")


class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

@app.route("/login",methods =["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
       username = form.username.data
       password_entered = form.password.data
       
       cursor = mysql.connection.cursor()

       sorgu = "Select * From users where username = %s"

       result = cursor.execute(sorgu,(username,))

       if result > 0:
           data = cursor.fetchone()
           real_password = data["password"]
           if sha256_crypt.verify(password_entered,real_password):
               flash("Başarıyla giriş yaptın.","success")

               session["logged_in"] = True
               session["username"] = username
               

               return redirect(url_for("index"))
           else:
               flash("Parolanızı yanlış girdiniz.","danger")
               return redirect(url_for("login")) 

       else:
           flash("Böyle bir kullanıcı bulunmamaktadır","danger")
           return redirect(url_for("login"))

    
    return render_template("login.html",form = form)
  

    
class RegisterForm(Form):
    name = StringField("Ad Soyad", validators=[validators.Length(min=3 , max=20)])
    username = StringField("Kullanıcı Adı", validators=[validators.length(min=5 , max=15)])
    email = StringField("E-Mail", validators=[validators.Email(message="Lütfen geçerli bir email girin.")])

    password = PasswordField("Parola" , validators=[
        validators.DataRequired(message="Bir parola belirleyin."),
        validators.EqualTo(fieldname = "confirm" , message="Parola uyuşmuyor.")
        
        
        ])
    confirm = PasswordField("Parola Doğrula")

@app.route("/register", methods = ["GET" , "POST"])
def register():
    form = RegisterForm(request.form)



    
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()

        cursor.close()
        flash("Başarıyla kayıt oldun." , "success")





        return redirect(url_for("login"))
    else:
        return render_template("register.html", form = form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için giriş yapmalısın." , "danger")
            return redirect(url_for("login"))
    return decorated_function

@app.route("/dashboard")
@login_required
def dashboard():

    cursor = mysql.connection.cursor()

    sorgu = "Select * From sorular where ekleyen = %s"
    result = cursor.execute(sorgu,(session["username"],))
    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html", articles = articles)
    else:
        return render_template("dashboard.html")

    


class klasikForm(Form):
    soru = TextAreaField("Soru", validators=[validators.Length(min=3 , max=20)])
    klasikcevap = TextAreaField("Cevap", validators=[validators.Length(min=3 , max=20)])

class testForm(Form):
    soru = TextAreaField("Soru", validators=[validators.Length(min=3 , max=20)])
    aSikki = TextAreaField("A şıkkı", validators=[validators.Length(min=3 , max=20)])
    bSikki = TextAreaField("B şıkkı", validators=[validators.Length(min=3 , max=20)])
    cSikki = TextAreaField("C şıkkı", validators=[validators.Length(min=3 , max=20)])
    dSikki = TextAreaField("D şıkkı", validators=[validators.Length(min=3 , max=20)])
    cevap = SelectField('Doğru Cevap', choices = [('A', 'A'), 
      ('B', 'B') ,('C', 'C'),('D', 'D') ])

class dyForm(Form):
    soru = TextAreaField("Soru", validators=[validators.Length(min=3 , max=20)])
    dycevap = RadioField('Cevap', choices = [('D','Doğru'),('Y','Yanlış')])

class ArticleForm(Form):
    soru = TextAreaField("Soru" ,validators=[validators.Length(min=5 , max = 100)])
    klasikcevap = TextAreaField("Klasik Cevap", validators=[validators.Length(min = 10)] )
    aSikki = TextAreaField("A Şıkkı" ,validators=[validators.Length(min=5 , max = 100)])
    bSikki = TextAreaField("B Şıkkı" ,validators=[validators.Length(min=5 , max = 100)])
    cSikki = TextAreaField("C Şıkı" ,validators=[validators.Length(min=5 , max = 100)])
    dSikki = TextAreaField("D Şıkkı" ,validators=[validators.Length(min=5 , max = 100)])
    dogruyanlis = RadioField('Cevap', choices = [('D','Doğru'),('Y','Yanlış')])
    secmelicevap = SelectField('Doğru Cevap', choices = [('A', 'A'), 
      ('B', 'B') ,('C', 'C'),('D', 'D') ])


@app.route("/klasiksoruEkle", methods=["GET" , "POST"])
@login_required
def klasikEkle():
    form = klasikForm(request.form)
    if request.method == "POST" and form.validate():
        soru = form.soru.data 
        klasikcevap = form.klasikcevap.data

        cursor = mysql.connection.cursor()
        sorgu = "Insert into sorular(soru,ekleyen,klasikcevap)  VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(soru,session["username"],klasikcevap))
        mysql.connection.commit()

        cursor.close()

        flash("Klasik soru başarı ile eklendi." , "success")
        return redirect(url_for("dashboard"))
    return render_template("klasiksoruEkle.html", form = form)


@app.route("/testEkle", methods=["GET" , "POST"])
@login_required
def testEkleme():
    form = testForm(request.form)
    if request.method == "POST" and form.validate():
        soru = form.soru.data
        aSikki = form.aSikki.data
        bSikki = form.bSikki.data
        cSikki = form.cSikki.data
        dSikki = form.dSikki.data
        cevap = form.cevap.data

        cursor = mysql.connection.cursor()
        sorgu = "Insert into sorular(soru,ekleyen,asikki,bsikki,csikki,dsikki,secmelicevap) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sorgu,(soru,session["username"],aSikki,bSikki,cSikki,dSikki,cevap))
        mysql.connection.commit()

        cursor.close()

        flash("Çoktan seçmeli soru başarı ile eklendi." , "success")
        return redirect(url_for("dashboard"))
    return render_template("testEkle.html", form = form)


@app.route("/dogruyanlisEkle", methods=["GET" , "POST"])
@login_required
def dyEkle():
    form = dyForm(request.form)
    if request.method == "POST" and form.validate():
        soru = form.soru.data
        dycevap = form.dycevap.data 

        cursor = mysql.connection.cursor()
        sorgu = "Insert into sorular(soru,ekleyen,dogruyanlis) VALUES (%s,%s,%s)"
        cursor.execute(sorgu ,(soru,session["username"],dycevap))
        mysql.connection.commit()
        cursor.close()



        flash("Doğru yanlış sorun başarıyla eklendi" , "success")
        return redirect(url_for("dashboard"))
    return render_template("dogruyanlisEkle.html" , form = form)


@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select*From sorular where ekleyen = %s and id = %s"
    result = cursor.execute(sorgu,(session["username"],id))

    if result > 0:
        sorgu2 = "Delete from sorular where id = %s"
        cursor.execute(sorgu2, (id,))
        mysql.connection.commit()

        return redirect(url_for("dashboard"))
    else:
        flash("Bu işleme yetkiniz yok." , "danger")
        return redirect(url_for("index"))


@app.route("/edit/<string:id>", methods = ["GET","POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()

        sorgu = "Select * From sorular where id = %s and ekleyen = %s"
        result = cursor.execute(sorgu,(id,session["username"]))

        if result == 0:
            flash("Böyle bir soru yok veya böyle bir yetkiniz yok." , "danger")
            return redirect(url_for("index"))

        else:
            article = cursor.fetchone()
            form = ArticleForm()
            form.soru.data = article["soru"]
            form.klasikcevap.data = article["klasikcevap"]
            
            form.aSikki.data = article["asikki"]
            form.bSikki.data = article["bsikki"]
            form.cSikki.data = article["csikki"]
            form.dSikki.data = article["dsikki"]
            form.dogruyanlis.data = article["dogruyanlis"]
            form.secmelicevap.data = article["secmelicevap"]

            return render_template("updateKlasik.html", form = form)
    
    
    
    else:
        form = ArticleForm(request.form)
        newSoru = form.soru.data
        newKlasikcevap = form.klasikcevap.data
        newA = form.aSikki.data
        newB = form.bSikki.data
        newC = form.cSikki.data
        newD = form.dSikki.data
        newdy = form.dogruyanlis.data 
        newSecmeli = form.secmelicevap.data

        sorgu2 = "Update sorular Set soru = %s , klasikcevap = %s, asikki = %s, bsikki = %s, csikki = %s, dsikki = %s, dogruyanlis = %s, secmelicevap = %s where id = %s"
        cursor=mysql.connection.cursor()
        cursor.execute(sorgu2,(newSoru,newKlasikcevap,newA,newB,newC,newD,newdy,newSecmeli,id))

        mysql.connection.commit()
        flash("Kod başarıyla güncellendi", "success")
        return redirect(url_for("dashboard"))

@app.route("/search" ,methods =["GET", "POST"])

def search():
    if request.method == "GET":
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()

        sorgu = "Select * From sorular where soru like '%" + keyword + "%' " 
        result = cursor.execute(sorgu)
        cursor.execute(sorgu)
        if result == 0:
            flash("Aranan kelimeye uygun sonuç bulunamadı" , "warning")
            return redirect(url_for("dashboard"))
        else:
            articles = cursor.fetchall()

            return render_template("dashboard.html", articles = articles)





if __name__ == "__main__":
    app.run(debug=True)