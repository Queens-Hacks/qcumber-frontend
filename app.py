from flask import Flask, render_template, request
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)
assets = Environment(app)

js = Bundle('js/jquery.js', 'js/jquery.djax.js', 'js/bootstrap.js', 'js/app.js', output='gen/packed.js')
assets.register('js_all', js)

scss = Bundle('styles/app.scss', filters='scss', output='gen/app.css')
assets.register('css_all', scss)
# less = Bundle('styles/global.less', filters='less', output='gen/global.css')
# assets.register('css_all', less)

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
