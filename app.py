from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://"
db = SQLAlchemy(app)
app.secret_key=getenv("SECRET_KEY")

@app.route("/")
def etusivu():
    result = db.session.execute("SELECT title, description, id FROM threads")
    threads = result.fetchall()
    x = 0
    thread2 = []
    for thread in reversed(threads):
        x = x+1
        thread2.append(thread)
        if x == 4:
            break
    threads = thread2
    session["attempt"] = "ok"
    return render_template("frontpage.html", threads=threads)

@app.route("/login")
def login():
    return render_template("login.html", attempt=session["attempt"])

@app.route("/login2",methods=["POST"])
def login2():
    username = request.form["username"]
    password = request.form["password"]
    result = db.session.execute("SELECT password FROM users WHERE name=:username", {"username":username})
    user = result.fetchone()
    if user == None:
        session["attempt"] = "failed"
        return redirect("/login")
    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password):
            session["attempt"] = "ok"
            session["username"] = username
            return redirect ("/")
        else:
            session["attempt"] = "failed"
            return redirect("/login")
            

@app.route("/signin")
def signin():
    return render_template("signin.html", attempt = session["attempt"])

@app.route("/signin2", methods=["POST"])
def signin2():
    username = request.form["username"]
    password = request.form["password"]
    result = db.session.execute("SELECT name FROM users")
    users = result.fetchone()
    if users == None or username not in users:
        hash = generate_password_hash(password)
        bio="Ei kuvausta"
        result = db.session.execute("INSERT INTO users (name, password, bio) VALUES (:username, :password, :bio)",{"username":username,"password":hash, "bio":bio})
        db.session.commit()
        session["username"] = username
        return render_template("signin2.html", username = username)
    else:
        session["attempt"] = "failed"
        return redirect ("/signin")
        
    
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/profiili/<user>")
def profiili(user):
    session["profile"]=user
    result = db.session.execute("SELECT id FROM users WHERE name=:user", {"user":user})
    user_id = result.fetchone()[0]
    if session["username"] == user:
        current_user = True
    else:
        current_user = False
    if session["username"] != None:
        if not current_user:
            result = db.session.execute("SELECT id FROM users WHERE name=:user", {"user":session["username"]})
            user_id2 = result.fetchone()[0]
            result = db.session.execute("SELECT id FROM friends WHERE user_id1=:id1 AND user_id2=:id2", {"id1":user_id, "id2":user_id2})
            test = result.fetchone()
            if user_id < user_id2:
                chat = str(user_id) + str(user_id2)
            elif user_id2 < user_id:
                chat = str(user_id2) + str(user_id)
        else:
            chat = "no"
            test = None
    else:
        chat = "no"
        test = None
    result = db.session.execute("SELECT bio FROM users WHERE name=:user", {"user":user})
    user_bio = result.fetchone()[0]
    result = db.session.execute("SELECT users.name FROM users, friends WHERE friends.user_id1=users.id AND friends.user_id2=:user_id", {"user_id":user_id})
    friends = result.fetchall()
    return render_template("profile.html", test = test, user = user, user_bio = user_bio, friends = friends, chat = chat, current_user = current_user)

@app.route("/kaverilista/<user>")
def kaverilista(user):
    result = db.session.execute("SELECT id FROM users WHERE name=:user", {"user":user})
    id1 = result.fetchone()[0]
    result = db.session.execute("SELECT id FROM users WHERE name=:user", {"user":session["username"]})
    id2 = result.fetchone()[0]
    result = db.session.execute("SELECT id FROM friends WHERE user_id1=:id1 AND user_id2=:id2", {"id1":id1, "id2":id2})
    test = result.fetchone()
    if test == None:
        result = db.session.execute("INSERT INTO friends (user_id1, user_id2) VALUES (:id1, :id2)", {"id1":id1, "id2":id2})
        db.session.commit()
        result = db.session.execute("INSERT INTO friends (user_id1, user_id2) VALUES (:id1, :id2)", {"id1":id2, "id2":id1})
        db.session.commit()
    else:
        result = db.session.execute("DELETE FROM friends WHERE user_id1=:id1 AND user_id2=:id2", {"id1":id1, "id2":id2})
        db.session.commit()
        result = db.session.execute ("DELETE FROM friends WHERE user_id1=:id2 AND user_id2=:id1", {"id1":id1, "id2":id2})
        db.session.commit()
    return redirect("/profiili/"+str(user))

@app.route("/kuvaus")
def kuvaus():
    return render_template("bio.html")

@app.route("/lisaakuvaus", methods=["POST"])
def lisaakuvaus():
    bio = request.form["bio"]
    user = session["username"]
    result = db.session.execute("UPDATE users SET bio=:bio WHERE name=:user", {"user":user, "bio":bio})
    db.session.commit()
    return redirect("/profiili/"+str(user))

@app.route("/keskustelu/<chat_id>")
def keskustelu(chat_id):
    result = db.session.execute("SELECT privmessages.text, users.name FROM privmessages, users WHERE privmessages.chat=:chat_id AND privmessages.user_id=users.id",{"chat_id":chat_id} )
    messages = result.fetchall()
    return render_template("chat.html", messages = messages, chat_id = chat_id)

@app.route("/uusiviesti/<chat_id>", methods=["POST"])
def uusiviesti(chat_id):
    result = db.session.execute("SELECT id FROM users WHERE name=:username", {"username":session["username"]})
    user_id = result.fetchone()[0]
    chattext = request.form["chattext"]
    result = db.session.execute("INSERT INTO privmessages (chat,text,user_id) VALUES (:chat_id, :chattext, :user)", {"chat_id":chat_id, "chattext":chattext, "user":user_id})
    db.session.commit()
    return redirect("/keskustelu/"+ str(chat_id))

@app.route("/Aihe/<aihe>")
def Aihe(aihe):
    result = db.session.execute("SELECT title, description, id FROM threads WHERE topic=:aihe", {"aihe":aihe})
    threads = result.fetchall()
    session["topic"]=aihe
    return render_template("topic.html", topic = aihe, threads = threads)

@app.route("/luopalsta")
def luopalsta():
    return render_template("newthread.html")

@app.route("/luopalsta2", methods=["POST"])
def luopalsta2():
    title = request.form["title"]
    message = request.form["message"]
    result = db.session.execute("SELECT id FROM users WHERE name=:username",{"username":session["username"]})
    user_id = result.fetchone()[0]
    result = db.session.execute("INSERT INTO threads (title,time,user_id,topic,description) VALUES (:title, NOW(), :user_id, :topic, :message) RETURNING id",{"title":title, "user_id":user_id, "topic":session["topic"], "message":message})
    thread_id = result.fetchone()[0]
    db.session.commit()
    return redirect("/keskusteluketju/"+str(thread_id))
    
@app.route("/keskusteluketju/<int:id>")
def keskusteluketju(id):
    session["threadid"]=id
    result=db.session.execute("SELECT title FROM threads WHERE id=:id", {"id":id})
    title=result.fetchone()[0]
    result=db.session.execute("SELECT description FROM threads WHERE id=:id", {"id":id})
    description=result.fetchone()[0]
    result=db.session.execute("SELECT threads.title, threads.description, users.name, threads.time, threads.topic FROM threads, users WHERE users.id=threads.user_id AND threads.id=:id", {"id":id})
    thread=result.fetchone()
    result=db.session.execute("SELECT messages.text, users.name FROM messages, users WHERE messages.thread_id=:id AND messages.user_id=users.id", {"id":id})
    messages=result.fetchall()
    return render_template("thread.html", id = id, thread = thread, messages = messages)

@app.route("/luoviesti", methods=["POST"])
def luoviesti():
    threadid=session["threadid"]
    text=request.form["text"]
    result=db.session.execute("SELECT id FROM users WHERE name=:username",{"username":(session["username"])})
    userid=result.fetchone()[0]
    db.session.execute("INSERT INTO messages (time,thread_id, user_id,text) VALUES (NOW(),:threadid,:userid,:text)",{"threadid":threadid, "userid":userid, "text":text})
    db.session.commit()
    return redirect("keskusteluketju/"+str(threadid))
