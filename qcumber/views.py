# pylint: disable=W0142,C0111

import re
from flask import render_template, redirect, url_for, request, jsonify
from elasticsearch.exceptions import NotFoundError, RequestError

# pylint: disable=W0611
from qcumber import APP, search, util, filters

@APP.route('/')
def index():
    """
    Qcumber's Homepage
    Displays a list of all of the sections, organized by letter
    """
    subjects = search.subjects()
    letters = [{'letter': x} for x in "abcdefghijklmnopqrstuvwxyz"]

    for letter in letters:
        letter['subjects'] = [x for x in subjects
                              if x['abbreviation'][0].lower() == letter['letter']]

    return render_template('index.html', letters=letters)


@APP.route('/catalog/<subject_id>/<course_id>')
def course_page(subject_id, course_id):
    """
    Single course detail page
    Displays information about the course, its sections, textbooks etc.
    """
    # TODO: Redirect to uppercase subject_id and course_id

    subject = search.subject(subject_id)
    course = search.course(subject_id, course_id)
    textbooks = search.textbooks(subject_id, course_id)
    sections = search.sections(subject_id, course_id)

    terms = {}
    for section in sections:
        # section['_id'] TODO: Ensure this is set
        term_name = '{year} {season}'.format(**section)

        # Add it to that term's list
        term = terms.get(term_name, [])
        term.append(section)
        terms[term_name] = term

    sorted_terms = sorted(terms.iteritems(), key=lambda x: util.term_ordering(x[0]))

    course_query = 'subject: {} number: {}'.format(subject_id, course_id)

    return render_template('course.html',
                           subject=subject,
                           course=course,
                           terms=sorted_terms,
                           textbooks=textbooks,
                           query=course_query)


@APP.route('/catalog/<subject_id>')
def subject_page(subject_id):
    """
    Subject course listing page
    Displays all of the courses within the subject
    """
    # TODO: Redirect to uppercase subject_id and course_id

    subject = search.subject(subject_id)
    subject_query = 'subject: {}'.format(subject_id)

    return results_page(subject_query,
                        short_title='{abbreviation}'.format(**subject),
                        title='{abbreviation} - {title}'.format(**subject),
                        force_all=True)


SUBJECT_RE = re.compile(r'^(?:SUBJECT: ?)?([A-Z]{2,4})$')
COURSE_RE = re.compile(
    r'^(?:(?:SUBJECT: ?([A-Z]{2,4}) NUMBER: ?([A-Z0-9]{2,4}))|(?:([A-Z]{2,4}) ?([A-Z0-9]{2,4})))$')

@APP.route('/search')
def search_results_page():
    """
    Search Results Page
    Displays a list of courses which match the search results
    """
    query = request.args.get('q', '')
    if query.strip() == '':
        return redirect(url_for('index'))

    # Check if there is a course/subject with the exact name
    subject_match = SUBJECT_RE.match(query.upper())
    if subject_match:
        subject_id = subject_match.group(1)
        try:
            # This will throw if it cannot find the subject
            search.subject(subject_id)
            return redirect(url_for('subject_page',
                                    subject_id=subject_id))
        except NotFoundError:
            pass # The course doesn't exist

    course_match = COURSE_RE.match(query.upper())
    if course_match:
        subject_id = course_match.group(1) or course_match.group(3)
        course_id = course_match.group(2) or course_match.group(4)
        try:
            search.course(subject_id, course_id)
            return redirect(url_for('course_page',
                                    subject_id=subject_id,
                                    course_id=course_id))
        except NotFoundError:
            pass # The course doesn't exist

    # It is a generic results page
    return results_page(query)


def results_page(query, short_title=None, title=None, force_all=False):
    """
    Performs a Query String Query on the course doctype, and displays the results
    With title, the results can be given a title. By default, only returns 100 results,
    but all results can be forced using the force_all parameter
    """
    try:
        results = search.search_query(query, force_all)
    except RequestError:
        return render_template('error.html',
                               query=query,
                               error='Parse error while processing query: "{}"'.format(query))

    careers = util.group_by_career(results)

    return render_template('search.html',
                           short_title=short_title,
                           title=title,
                           query=query,
                           careers=careers)

###############
# STATIC URLS #
###############

@APP.route('/timetable')
def timetable(): return render_template('timetable.html')

@APP.route('/timetable/section/<section_id>')
def section_json(section_id):
    """
    Return JSON data for the given section
    """
    section = search.section(section_id)

    return jsonify(section)

@APP.route('/faq')
def faq(): return render_template('static/faq.html')

@APP.route('/resources')
def resources(): return render_template('static/resources.html')

@APP.route('/about')
def about(): return render_template('static/about.html')

@APP.route('/contact')
def contact(): return render_template('static/contact.html')

@APP.route('/issues')
def issues(): return render_template('static/issues.html')
