#!/usr/bin/env python

from flask import Flask, render_template, abort, redirect, url_for, request, Markup, escape, jsonify
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError, NotFoundError
from datetime import datetime
import dateutil.parser
import re

BIGNUM = 10000 # The maximum number of things which you query for

es = Elasticsearch() # TODO: Set port & shit

# pylint : C0103
app = Flask(__name__)

def term_ordering(term):
    """
    Generates the order for a given term
    """
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

def escape_query_segment(segment):
    """
    Transform a query segment such that it is safe to include in a query
    """
    return segment.replace(' ', '\\ ')

@app.template_filter('nl2br')
def nl2br(string):
    """
    Convert newlines into <br> tags, and produce HTML.
    Also escapes all of the text passed in
    """
    return Markup('<br>'.join([escape(x) for x in string.split('\n')]))

@app.template_filter('slugify')
def slugify(value):
    """TODO: Make this less lazy"""
    return '_' + value.replace(' ', '-').lower()

@app.template_filter('oldterm')
def is_oldterm(term):
    now = datetime.now()
    now_rank = now.year * 3 + (now.month - 1) % 4
    return now_rank > term_ordering(term)

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
    elif section == 'SEM':
        return 'Seminar'
    elif section == 'ONL':
        return 'Online'
    return section

@app.route('/')
def index():
    # Get all of the subjects
    res = es.search(index='qcumber', doc_type='subject', body={
        'sort': [
            { 'abbreviation': { 'order': 'asc' } }
        ],
        'query': {
            'match_all': {}
        }
    }, _source=True, size=BIGNUM)['hits']['hits']

    letters = [{'letter': x} for x in "abcdefghijklmnopqrstuvwxyz"]
    for letter in letters:
        subjects = [i['_source'] for i in res if i['_source']['abbreviation'][0].lower() == letter['letter']]
        letter['subjects'] = subjects

    return render_template('index.html', letters=letters)


@app.route('/catalog/<subject>/<course>')
def course(subject, course):
    subject = subject.upper()
    course = course.upper()

    course_query = 'subject: {} number: {}'.format(subject, course)
    # Get the subject
    try:
        sub = es.get(index='qcumber', doc_type='subject', id=subject)
    except NotFoundError:
        return abort(404)

    # Get the course
    try:
        course = es.get(index='qcumber', doc_type='course', id=sub['_source']['abbreviation'] + ' ' + course)
    except NotFoundError:
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
        section['_source']['_id'] = section['_id'] # Record the _id

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
                           query='subject: {} number: {}'.format(
                               sub['_source']['abbreviation'], course['_source']['number']))


@app.route('/catalog/<subject>')
def subject(subject):
    if subject != subject.upper():
        return redirect(url_for('subject', subject=subject.upper()))

    subject = subject.strip()
    subject_query = 'subject: {}'.format(escape_query_segment(subject))

    try:
        sub = es.get(index='qcumber', doc_type='subject', id=subject)
    except NotFoundError:
        return redirect(url_for('search', q=subject_query))

    return results_page(subject_query,
            short_title='{abbreviation}'.format(**sub['_source']),
            title='{abbreviation} - {title}'.format(**sub['_source']),
            force_all=True)


SUBJECT_RE = re.compile(r'^(?:SUBJECT: ?)?([A-Z]{2,4})$')
COURSE_RE = re.compile(r'^(?:(?:SUBJECT: ?([A-Z]{2,4}) NUMBER: ?([A-Z0-9]{2,4}))|(?:([A-Z]{2,4}) ?([A-Z0-9]{2,4})))$')
@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query.strip() == '':
        return redirect(url_for('index'))

    # Check if there is a course/subject with the exact name
    subject_match = SUBJECT_RE.match(query.upper())
    if subject_match:
        s = subject_match.group(1)
        try:
            subject = es.get(index='qcumber', doc_type='subject', id='{}'.format(s))
            return redirect(url_for('subject', subject=s))
        except:
            pass # The course doesn't exist

    course_match = COURSE_RE.match(query.upper())
    if course_match:
        s = course_match.group(1) or course_match.group(3)
        c = course_match.group(2) or course_match.group(4)
        try:
            course = es.get(index='qcumber', doc_type='course', id='{} {}'.format(s, c))
            return redirect(url_for('course', subject=s, course=c))
        except:
            pass # The course doesn't exist

    return results_page(query)


def results_page(query, short_title=None, title=None, force_all=False):
    """
    Performs a Query String Query on the course doctype, and displays the results
    With title, the results can be given a title. By default, only returns 100 results,
    but all results can be forced using the force_all parameter
    """
    query = query.strip()

    try:
        results = es.search(index='qcumber', doc_type='course', body={
            'sort': [
                {'number': {'order': 'asc'}}
            ],
            'query': {
                'query_string': {
                    'query': query,
                    'lenient': True,
                    'default_operator': 'AND',
                },
            },
        }, size=BIGNUM if force_all else 100)['hits']['hits']
    except RequestError:
        return render_template('error.html',
                               query=query,
                               error='Parse error while processing query: "{}"'.format(query))

    reses = group_courses([x['_source'] for x in results])

    return render_template('search.html',
                           short_title=short_title,
                           title=title,
                           query=query,
                           careers=reses)

###############
# STATIC URLS #
###############

@app.route('/timetable')
def timetable(): return render_template('timetable.html')

@app.route('/timetable/section/<section_id>')
def sectionJSON(section_id):
    try:
        section_data = es.get(index='qcumber', doc_type='section', id=section_id)['_source']
    except NotFoundError:
        return abort(404, 'There is no such section')

    return jsonify(section_data)

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

# Run the debug server
if __name__ == '__main__':
    app.run(port=3000, debug=True)
