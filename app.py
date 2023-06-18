#FaceMash
#01/06/2023

from flask import Flask, render_template, request, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)

class pictures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    votes = db.Column(db.Integer)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    pics_data = pictures.query.all()
    if len(pics_data) < 2:
        return redirect("/add-picture")
    
    pic1 = choice(pics_data)
    pics_data.remove(pic1)
    pic2 = choice(pics_data)
    return render_template("comparison.html", pic1=pic1, pic2=pic2)

@app.route("/vote", methods=["POST"])
def vote():
    winner = pictures.query.filter_by(id=request.form["winner"]).first()
    looser = pictures.query.filter_by(id=request.form["looser"]).first()
    
    if winner.votes < looser.votes:
        winner.votes += 2
        looser.votes -= 2
    else:
        winner.votes += 1
        looser.votes -= 1
    
    db.session.commit()
    return redirect("/")

@app.route("/leaderboard")
def leaderboard():
    if "p" in request.args:
        page = int(request.args.get("p"))
        if page < 1: page = 1
    else:
        page = 1
    pics_data = pictures.query.order_by(pictures.votes).offset(page * 10 - 10).limit(10).all()
    pics_count = pictures.query.count()
    print(pics_count)
    return render_template("leaderboard.html", pictures=pics_data, page=page, pics_count=pics_count)

@app.route("/add-picture")
def add_picture():
    return render_template("picture-upload-form.html")

@app.route("/upload", methods=["POST"])
def upload():
    for file in request.files.getlist("img"):
        pic_entry = pictures(votes=0)
        
        db.session.add(pic_entry)
        
        file.save("pictures/" + str(pictures.query.count()) + ".png")
        print(file)
    db.session.commit()
    return redirect("/add-picture")

@app.route("/pictures/<file>")
def picture_file(file):
    return send_from_directory("pictures", file)

app.run()