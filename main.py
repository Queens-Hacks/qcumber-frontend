#!/usr/bin/env python

from flask import Flask, render_template, abort, redirect, url_for, request
from elasticsearch import Elasticsearch
from datetime import datetime
import dateutil.parser
import re

BIGNUM=10000 # The maximum number of things which you query for

es = Elasticsearch() # TODO: Set port & shit

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    PROPAGATE_EXCEPTIONS=True
)

def term_ordering(term):
    year, season_name = term.split()
    if season_name == 'Winter':
        season = 0
    elif season_name == 'Summer':
        season = 1
    else:
        season = 2

    return int(year) * 3 + season

def group_courses(courses):
    """
    Groups courses based on the career. The groups are sorted in reverse
    alphabetical order. The return value is an array of pairs, where the
    first element is the Career, and the second is the courses.
    """
    grouped = {}
    for course in courses:
        old = grouped.get(course['career'], [])
        old.append(course)
        grouped[course['career']] = old

    return reversed(sorted(grouped.iteritems(), key=lambda x: x[0]))

@app.template_filter('timeformat')
def format_time(value):
    if value:
        dt = dateutil.parser.parse(value)
        return dt.strftime("%I:%M%p")
    else:
        return ''

@app.template_filter('dayformat')
def format_day(value):
    if value:
        dt = dateutil.parser.parse(value)
        return dt.strftime("%B %d %Y")
    else:
        return 'N/A'

@app.template_filter('dayofweek')
def format_dow(value):
    if value:
        return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][value]
    else:
        return 'N/A'

@app.template_filter('fancy_section_type')
def fancy_section_type(section):
    if section == 'LEC':
        return 'Lecture'
    elif section == 'LAB':
        return 'Laboratory'
    elif section == 'TUT':
        return 'Tutorial'
    elif section == 'PRA':
        return 'Practicum'
    elif section == 'COR':
        return 'Correspondence'
    return section

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
        letter['subjects'] = sorted(subjects, key=lambda x: x['abbreviation'])

    return render_template('index.html', letters=letters)

@app.route('/catalog/<subject>')
def subject(subject):
    subject = subject.upper()

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
    careers = group_courses(courses)

    return render_template('subject.html',
            subject=sub['_source'],
            careers=careers,
            query=sub['_source']['abbreviation'])

@app.route('/catalog/<subject>/<course>')
def course(subject, course):
    subject = subject.upper()
    course = course.upper()

    # Get the subject
    sub = es.get(index='qcumber', doc_type='subject', id=subject)
    if not sub['found']:
        abort(404)

    # Get the course
    course = es.get(index='qcumber', doc_type='course', id=sub['_source']['abbreviation'] + ' ' + course)
    if not course['found']:
        return abort(404)

    # Get the textbooks
    textbooks = es.search(index='qcumber', doc_type='textbook', body={
        'query': {
            'match_phrase': {
                'courses': '{} {}'.format(sub['_source']['abbreviation'], course['_source']['number'])
            }
        }
    }, _source=True, size=BIGNUM)['hits']['hits']

    tbooks = [x['_source'] for x in textbooks]

    # Get the sections
    sects = es.search(index='qcumber', doc_type='section', body={
        'query': {
            'bool': {
                'must': [
                    {
                        'match': { 'course': course['_source']['number'] }
                    },
                    {
                        'match': { 'subject': sub['_source']['abbreviation'] }
                    }
                ]
            }
        }
    }, _source=True, size=BIGNUM)['hits']['hits']

    terms = {}
    for section in sects:
        old = terms.get('{year} {season}'.format(**(section['_source'])), [])
        old.append(section['_source'])
        terms['{year} {season}'.format(**(section['_source']))] = old

    sorted_terms = sorted(terms.iteritems(), key=lambda x: term_ordering(x[0]))


    # sections = [x['_source'] for x in sects]

    return render_template('course.html',
            subject=sub['_source'],
            course=course['_source'],
            terms=sorted_terms,
            textbooks=tbooks,
            query='{} {}'.format(sub['_source']['abbreviation'], course['_source']['number']))

subjectre = re.compile(r'^([A-Za-z]{2,4})$')
coursere = re.compile(r'^([A-Za-z]{2,4}) ([A-Za-z0-9]{2,4})$')
@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query.strip() == '':
        return redirect('/')

    # Check if there is a course/subject with the exact name
    subject_match = subjectre.match(query.upper())
    if subject_match:
        try:
            subject = es.get(index='qcumber', doc_type='subject', id=query.upper())
            return redirect('/catalog/{}'.format(subject_match.group(1)))
        except:
            pass # The course doesn't exist

    course_match = coursere.match(query.upper())
    if course_match:
        try:
            course = es.get(index='qcumber', doc_type='course', id=query.upper())
            return redirect('/catalog/{}/{}'.format(course_match.group(1), course_match.group(2)))
        except:
            pass # The course doesn't exist

    results = es.search(index='qcumber', doc_type='course', body={
        'query': {
            'query_string': {
                'query': query.strip(),
                'lenient': True,
                'default_operator': 'AND'
            }
        }
    }, _source=True, size=100)['hits']['hits']

    reses = [x['_source'] for x in results]

    return render_template('search.html', query=query, courses=reses)

###############
# STATIC URLS #
###############

@app.route('/faq')
def faq(): return render_template('static/faq.html')

@app.route('/resources')
def resources(): return render_template('static/resources.html')

@app.route('/about')
def about(): return render_template('static/about.html')

@app.route('/contact')
def contact(): return render_template('static/contact.html')

@app.route('/issues')
def issues(): return render_template('static/issues.html')

if __name__ == '__main__':
    app.run(port=3000)
