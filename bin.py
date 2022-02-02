import json, string, os
from time import time
from random import choices

from flask import (
	Flask,
	render_template,
	request,
	Response,
	redirect,
	url_for
)

#line textarea
#mettre le texte à la couleur du langage
#report button

app = Flask(__name__) 

with open("config.json", "r") as file:
	json_file = json.load(file)

max_characters = json_file["MAX_CHARACTERS"]
langages_list = json_file["LANGAGES_LIST"]

@app.route("/", methods=["GET"])
def index():
	return render_template("index.html", langages_list=langages_list)

@app.route("/<key>", methods=["GET"])
def access(key=None):
	with open("data/bin.json", "r") as file:
		json_file = json.load(file)

	try:
		infos = json_file[key]
	except:
		return Response(status=404)

	if infos["expiration"]:
		if time() >= infos["expiration"]:
			del json_file[key]

			with open("data/bin.json", "w") as file:
				json.dump(json_file, file, indent=4)

			return Response(status="404")

	elif infos["maxusage"]:
		infos["views"] += 1

		if infos["views"] == int(infos["maxusage"]):
			del json_file[key]

		with open("data/bin.json", "w") as file:
			json.dump(json_file, file, indent=4)

		if infos["views"] == int(infos["maxusage"]):
			return Response(status="404")

	return render_template("bin.html", code=infos["code"])

@app.route("/new", methods=["POST"])
def new():
	if not request.form["code"] or not request.form["langage"]:
		return Response(status="403")

	langages_list["txt"] = "Text"
	if request.form["langage"] not in langages_list:
		return Response(status="403")

	if len(request.form["code"]) > max_characters:
		return Response(status="403")

	if request.form["maxusage"]:
		try:
			maxusage = int(request.form["maxusage"])
		except:
			return Response(status="403")
	else:
		maxusage = ""

	if request.form["expiration"]:
		pos = ["s","m","h","d"]
		unit = request.form["expiration"][-1]
		time_dict = {"s": 1,"m": 60,"h": 3600,"d": 86400}

		if unit not in pos:
			return Response(status="403")

		try:
		    timeVal = int(request.form["expiration"][:-1])
		except:
		    return -2

		expiration = time() + timeVal * time_dict[unit]
	else:
		expiration = ""

	random_characters = "".join(choices(string.ascii_letters + string.digits, k=6))

	with open("data/bin.json", "r") as file:
		json_file = json.load(file)

	json_file[random_characters] = {
		"author": request.environ.get('HTTP_X_REAL_IP', request.remote_addr),
		"code": request.form["code"],
		"maxusage": maxusage,
		"expiration": expiration,
		"langage": request.form["langage"],
		"views": 0
	}

	with open("data/bin.json", "w") as file:
		json.dump(json_file, file, indent=4)

	return redirect(url_for("access", key=random_characters))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
