from flask import Flask, render_template, abort, redirect, url_for, request
from elasticsearch import Elasticsearch
import re

BIGNUM=1000 # The maximum number of things which you query for

es = Elasticsearch() # TODO: Set port & shit

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    PROPAGATE_EXCEPTIONS=True
)

@app.route('/')
def index():
    # Get all of the subjects
    res = es.search(index='qcumber', doc_type='subject', body={
        'query': {
            'match_all': {}
        }
    }, _source=True, size=BIGNUM)

    hits = res['hits']['hits']

    letters = [{'letter': x} for x in "abcdefghijklmnopqrstuvwxyz"]
    for letter in letters:
        subjects = [i['_source'] for i in hits if i['_source']['abbreviation'][0].lower() == letter['letter']]
        letter['subjects'] = subjects

    return render_template('index.html', letters=letters)

@app.route('/catalog/<subject>')
def subject(subject):
    sub = es.get(index='qcumber', doc_type='subject', id=subject)
    if not sub['found']:
        abort(404)

    res = es.search(index='qcumber', doc_type='course', body={
        'query': {
            'match': {
                'subject': sub['_source']['abbreviation']
            }
        }
    }, _source=True, size=BIGNUM)['hits']['hits']

    courses = sorted([x['_source'] for x in res], key=lambda x: x['number'])

    return render_template('subject.html', subject=sub['_source'], courses=courses)

@app.route('/catalog/<subject>/<course>')
def course(subject, course):
    sub = es.get(index='qcumber', doc_type='subject', id=subject)
    if not sub['found']:
        abort(404)

    course = es.get(index='qcumber', doc_type='course', id=sub['_source']['abbreviation'] + ' ' + course)
    if not course['found']:
        return abort(404)

    sections = [] # TODO: Implement

    return render_template('course.html', subject=sub['_source'], course=course['_source'], sections=sections)

subjectre = r'^[A-Za-z]{2,4}$'
coursere = r'^[A-Za-z]{2,2} [A-Za-z0-9]{2,4}$'
@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query.strip() == '':
        return redirect('/')

    results = es.search(index='qcumber', doc_type='course', body={
        'query': {
            'fuzzy_like_this': {
                'fields': ['title', 'number', 'description'],
                'like_text': query.strip()
            }
        }
    }, _source=True, size=100)['hits']['hits']

    reses = [x['_source'] for x in results]

    return render_template('search.html', query=query, results=reses)

#@app.route('/search')
#def search():
    #query = request.args.get('q', '')
    #if query.strip() == '':
        #return render_template('search.html', results=[], query=query)
    #else:
        #es.get(index='qcumber', doc_type='')

if __name__ == '__main__':
    app.run(port=3000)
