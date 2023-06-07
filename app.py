from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/atribucion")
def atribucion():
    return render_template("atribucion.html")

if __name__ == "__main__":
    app.run()