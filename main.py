from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''



API_Key='cec9d48e72898afbaabeb19e86fe805c'
access_token='eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjZWM5ZDQ4ZTcyODk4YWZiYWFiZWIxOWU4NmZlODA1YyIsIm5iZiI6MTczMDE2MTk2MC41MzcxNCwic3ViIjoiNjcyMDJhYmU0YmUxNTQ2OWU3MGU1OGMwIiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.8YfLS2AbTW5eDc4WoeZX3X4NoIyREPLfwknPZiTMrsM'
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DB object using SQLAlchemy constructor
class Base(DeclarativeBase):
    pass


#Configure the extension
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///moviess.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)




class Movie(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250))
    year: Mapped[int]=mapped_column(Integer)
    description:Mapped[int]=mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[float] = mapped_column(Float, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url:Mapped[str] =mapped_column(String(250), nullable=False)

# CREATE TABLE

with app.app_context():
    db.create_all()

movies=[]

class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

class AddMovieForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()])
    submit=SubmitField("Add Movie")

new_movie = Movie(
    title="Phone Booth1",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)
second_movie = Movie(
    title="Avatar The Way of Water1",
    year=2022,
    description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
    rating=7.3,
    ranking=9,
    review="I liked the water.",
    img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
)


@app.route("/")
def home():
    result=db.session.execute(db.select(Movie))
    all_movies=result.scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html",movies=all_movies)



@app.route("/add", methods=['POST','GET'])
def add():
    form=AddMovieForm()
    if form.validate_on_submit():
        movie_title=form.title.data
        response=requests.get(url='https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1',params={"api_key": API_Key, "query": movie_title})

        print(response.json())
        data=response.json()["results"]

        return render_template('select.html',options=data)
    return render_template("add.html", form=form)






@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        #The language parameter is optional, if you were making the website for a different audience
        #e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": API_Key, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("rate_movie"), id=new_movie.id)

@app.route("/rate_movie", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
