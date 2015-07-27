# pylint: disable=W0142,C0111

import datetime
import re
from collections import OrderedDict
from flask import render_template, redirect, url_for, request, jsonify, abort

# pylint: disable=W0611
from qcumber import APP, util, filters, db

ALPHABET="abcdefghijklmnopqrstuvwxyz"

@APP.route('/')
def index():
    """
    Qcumber's Homepage
    Displays a list of all of the sections, organized by letter
    """
    subjects = db.dict_query("SELECT abbreviation, title from queens.subjects ORDER BY abbreviation")

    subject_groups = OrderedDict([(x,[]) for x in ALPHABET])

    for subj in subjects:
        letter = subj['abbreviation'][0].lower()
        subject_groups[letter].append(subj)

    return render_template('index.html', subject_groups=subject_groups)


@APP.route('/catalog/<subject_abbr>/<course_num>')
def course_page(subject_abbr, course_num):
    """
    Single course detail page
    Displays information about the course, its sections, textbooks etc.
    """
    if subject_abbr.upper() != subject_abbr or course_num.upper() != course_num:
        return redirect(url_for('course_page',
                                subject_abbr=subject_abbr.upper(),
                                course_num=course_num.upper()))

    try:
        subject, course = db.course_by_abbrev(subject_abbr, course_num)
    except IndexError as e:
        return abort(404,'There doesn\'t appear to be a course named {} {}'.format(subject_abbr, course_num))

    textbooks = db.dict_query("""
        SELECT t.*, bkstr.price, bkstr.url
        FROM
            queens.textbooks t
                JOIN queens.course_textbooks ct ON (t.id = ct.textbook_id)
                LEFT JOIN queens.textbooks_bookstore bkstr on (t.id = bkstr.textbook_id)
        WHERE course_id = %s """, (course['id'],))

    sections = db.dict_query("SELECT * FROM queens.sections WHERE course_id = %s", (course['id'],))
    for section in sections:
        section = db.section_get_classes(section)

    terms = {}
    for section in sections:
        term_name = '{year} {season}'.format(**section)

        # Add it to that term's list
        term = terms.get(term_name, [])
        term.append(section)
        terms[term_name] = term

    sorted_terms = sorted(terms.items(), key=lambda x: util.term_ordering(x[0]))

    course_query = 'subject: {} number: {}'.format(subject_abbr, course_num)

    return render_template('course.html',
                           subject=subject,
                           course=course,
                           terms=sorted_terms,
                           textbooks=textbooks,
                           query=course_query)


@APP.route('/catalog/<subject_abbr>')
def subject_page(subject_abbr):
    """
    Subject course listing page
    Displays all of the courses within the subject
    """
    if subject_abbr.upper() != subject_abbr:
        return redirect(url_for('subject_page', subject_abbr=subject_abbr.upper()))

    try:
        subject = db.subject_by_abbrev(subject_abbr)
    except IndexError as e:
        return abort(404, 'There doesn\'t appear to be a subject named {}'.format(subject_abbr))

    courses = db.dict_query("""
        SELECT c.*, csf.seasons::text[]
        FROM
            queens.courses c
                LEFT JOIN queens.course_seasons_offered csf ON c.id = csf.course_id
        WHERE subject_id = %s""", (subject['id'],))
    for c in courses:
        c['subject_abbr'] = subject['abbreviation']
    grouped_courses=util.group_by_course_num(courses)

    subject_query = 'subject: {}'.format(subject_abbr)

    return render_template('search.html',
                        query=subject_query,
                        short_title='{abbreviation}'.format(**subject),
                        title='{abbreviation} - {title}'.format(**subject),
                        groups=grouped_courses)


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
    course_match = COURSE_RE.match(query.upper())
    if subject_match:
        subject_abbr = subject_match.group(1)
        try:
            subject = db.subject_by_abbrev(subject_abbr)
            return redirect(url_for('subject_page',
                                    subject_abbr=subject_abbr))
        except IndexError as e:
            pass # The subject doesn't exist
    elif course_match:
        subject_abbr = course_match.group(1) or course_match.group(3)
        course_id = course_match.group(2) or course_match.group(4)
        try:
            subject, course = db.course_by_abbrev(subject_abbr, course_num)
            return redirect(url_for('course_page',
                                    subject_abbr=subject_abbr,
                                    course_id=course_id))
        except IndexError as e:
            pass # The course doesn't exist

    # TODO a generic results page
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

    groups = util.group_by_course_num(results)

    return render_template('search.html',
                           short_title=None,
                           title=None,
                           query=query,
                           groups=groups)

#################
# API-ish STUFF #
#################

# psuedo api, only GET allowed right now
@APP.route('/api/sections/<section_id>')
def api_section(section_id):
    try:
        section = db.dict_query("""
            SELECT
                s1.*,
                c.number as course_num,
                s2.abbreviation as subject_abbrev
            FROM
                queens.sections s1
                    LEFT JOIN queens.courses c on (s1.course_id = c.id)
                    LEFT JOIN queens.subjects s2 on (c.subject_id = s2.id)
            WHERE s1.id = %s""", (section_id,))[0]
        section = db.section_get_classes(section)
        for cl in section['classes']:
            for k,val in cl.items():
                if isinstance(val, (datetime.time, datetime.date)):
                    cl[k] = val.isoformat()

    except IndexError as e:
        response = jsonify({'error': 404, 'message': 'Section not found'})
        response.status_code = 404
        return response
    return jsonify(section)

###############
# STATIC URLS #
###############

# TODO make one dynamic thing to serve these pages in static

@APP.route('/timetable')
def timetable(): return render_template('timetable.html')

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

@APP.errorhandler(404)
def not_found(e):
    """
    The 404 error page. Displays an error message to the screen
    """
    return render_template('error.html', error=e), 404

