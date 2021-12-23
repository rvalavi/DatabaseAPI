from flask import Flask, request, jsonify, render_template, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from urllib.parse import quote 


# from routes import api

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://admin:%s@172.20.0.5:5432/postgres" % quote("{{ dbpass }}")
# app.config["SQLALCHEMY_POOL_RECYCLE"] = 10 # second to recycle the db connection

# init db
db = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)

# app.register_blueprint(request_api.get_blueprint())

# app.register_blueprint(api)


# class for chem table
class chemsModel(db.Model):
    __tablename__ = "chems"
    id = db.Column(db.Integer, primary_key=True)
    chem_active = db.Column(db.String(75), nullable=False)
    chem_group = db.Column(db.String(200), nullable=True)
    chem_irac = db.Column(db.String(5), nullable=True)

    def __init__(self, id, chem_active, chem_group, chem_irac):
        self.id = id
        self.chem_active = chem_active
        self.chem_group = chem_group
        self.chem_irac = chem_irac


# class for species table
class speciesModel(db.Model):
    __tablename__ = "species"
    id = db.Column(db.Integer, primary_key=True)
    species = db.Column(db.String(100), nullable=False)

    def __init__(self, id, species):
        self.id = id
        self.species = species


# class for paper table
class paperModel(db.Model):
    __tablename__ = "papers"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(200), nullable=True)
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(300), nullable=False, unique=True)
    journal = db.Column(db.String(200))
    doi = db.Column(db.String(200))

    def __init__(self, id, author, year, title, journal, doi):
        self.id = id
        self.author = author
        self.year = year
        self.title = title
        self.journal = journal
        self.doi = doi


# create schema for the tables
# allowed feild to show on the get requests
class ChemSchema(ma.Schema):
	class Meta:
		fields = ("chem_active", "chem_group", "chem_irac")

# init schema
chem_schema = ChemSchema(many=False)
chems_schema = ChemSchema(many=True)

# define the get requests
@app.route("/")
@app.route("/api")
@app.route("/api/")
def home():
    return redirect(url_for("get_docs")) # re-direct to docs


@app.route("/api/docs")
def get_docs():
    print("sending docs")
    return render_template("swaggerui.html")


# @app.route("/api/chems/all", methods=["GET"])
# def chem_list():
#     allchems = chemsModel.query.all()
#     output = []
#     for ch in allchems:
#         currChem = {}
#         currChem["chem_active"] = ch.chem_active
#         currChem["chem_group"] = ch.chem_group
#         currChem["chem_irac"] = ch.chem_irac
#         output.append(currChem)
#     return jsonify(output)

# get request with schema
@app.route("/api/chems/all", methods=["GET"])
def get_chems():
	all_chems = chemsModel.query.all()
	result = chems_schema.dump(all_chems)
	return jsonify(result)



# @app.route("/api/chems/id=<int:id>", methods=["GET"])
# def chem_id(id):
#     ch = chemsModel.query.filter(chemsModel.id == id).first_or_404(
#         description = 'The id {} was not found!'.format(id)
#     )
#     output = {}
#     output["chem_active"] = ch.chem_active
#     output["chem_group"] = ch.chem_group
#     output["chem_irac"] = ch.chem_irac
#     return jsonify(output)

@app.route("/api/chems/id=<int:id>", methods=["GET"])
def get_chem(id):
	chembyid = chemsModel.query.get(id)
	# if len(chembyid) < 1:
	# 	abort(404, 
	# 		description = "The id was not found!"
	# 	)
	return chem_schema.jsonify(chembyid)


# @app.route("/api/chems/active=<query>", methods=["GET"])
# def chem_by_active(query):
#     search = "%{}%".format(query)
#     chemQuery = chemsModel.query.filter(chemsModel.chem_active.like(search)).all()
#     if len(chemQuery) < 1:
#         abort(404, 
#             description = "No active similar to {} was found!".format(str(query))
#         )
#     output = []
#     for ch in chemQuery:
#         currChem = {}
#         currChem["chem_active"] = ch.chem_active
#         currChem["chem_group"] = ch.chem_group
#         currChem["chem_irac"] = ch.chem_irac
#         output.append(currChem)
#     return jsonify(output)

@app.route("/api/chems/active=<query>", methods=["GET"])
def chem_by_active(query):
	search = "%{}%".format(query)
	chemQuery = chemsModel.query.filter(chemsModel.chem_active.like(search)).all()
	if len(chemQuery) < 1:
		abort(404, 
			description = "No active similar to {} was found!".format(str(query))
		)
	result = chems_schema.dump(chemQuery)
	return jsonify(result)


@app.route("/api/species/all", methods=["GET"])
def species_list():
    allspecies = speciesModel.query.all()
    output = []
    for sp in allspecies:
        currSp = {}
        # currSp["id"] = sp.id
        currSp["name"] = sp.species
        output.append(currSp)
    return jsonify(output)

@app.route("/api/species/name=<query>", methods=["GET"])
def sp_by_name(query):
    search = "%{}%".format(query)
    speciesQuery = speciesModel.query.filter(speciesModel.species.like(search)).all()
    if len(speciesQuery) < 1:
        abort(404, 
            description = "No species name similar to {} was found!".format(str(query))
        )
    output = []
    for sp in speciesQuery:
        currSp = {}
        currSp["name"] = sp.species
        output.append(currSp)
    return jsonify(output)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
