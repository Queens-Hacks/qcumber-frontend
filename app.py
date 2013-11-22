from flask import Flask, render_template, request
from flask.ext.gears import Gears
from gears_less import LESSCompiler

app = Flask(__name__)

gears = Gears(
    compilers={'.less': LESSCompiler.as_handler()},
    assets_folder='static',
)
gears.init_app(app)

@app.route('/')
def home():
    return render_template('home.html');

@app.route('/catalog')
def catalog():
    query = request.args.get('q')
    if query:
        # Filter
        return render_template('search.html');
    else:
        return render_template('catalog.html');

@app.route('/catalog/<subject>')
def subject():
    return render_template('catalog.html');


if __name__ == '__main__':
    app.run(debug=True)
