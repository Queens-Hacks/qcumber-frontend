#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime
import os
import json

ES_INDEX = 'qcumber'

def is_current(section):
    """
    This function determines if a given section is current.

    If the event is in the future, it should always be included.
    If the event is in the past by more than a season, it should be excluded
    """

    if section['season'] == 'Winter':
        season = 0
    elif section['season'] == 'Summer':
        season = 1
    else:
        season = 2

    year = int(section['year'])
    section_num = 3 * year + season

    now = datetime.now()
    now_num = 3 * now.year + ((now.month - 1) // 4)

    return now_num - section_num <= 1

####################
# Import Functions #
####################
def courses(es):
    courses = os.listdir(os.path.join('out', 'courses'))
    for course in courses:
        with open(os.path.join('out', 'courses', course)) as f:
            coursedata = json.loads(f.read())
            cd = coursedata['basic']
            cd.update(coursedata['extra'])

            print('Registering Course: {subject} {number}'.format(**cd))

            # Push the item into the elasticsearch
            es.index(index=ES_INDEX, doc_type='raw_course', id='{subject} {number}'.format(**cd), body=cd)

def sections(es):
    sections = os.listdir(os.path.join('out', 'sections'))
    for section in sections:
        with open(os.path.join('out', 'sections', section)) as f:
            sectiondata = json.loads(f.read())
            sd = sectiondata['basic']
            sd['classes'] = sectiondata['classes']

            if not is_current(sd): continue # Reject non-current sections

            print('Registering Section: {year} {season} {subject} {course}'.format(**sd))

            es.index(index=ES_INDEX, doc_type='section', id='{year} {season} {subject} {course} {solus_id}'.format(**sd), body=sd)

def subjects(es):
    subjects = os.listdir(os.path.join('out', 'subjects'))
    for subject in subjects:
        with open(os.path.join('out', 'subjects', subject)) as f:
            subjectdata = json.loads(f.read())

            print('Registering Subject: {abbreviation}'.format(**subjectdata))

            es.index(index=ES_INDEX, doc_type='subject', id=subjectdata['abbreviation'], body=subjectdata)

def textbooks(es):
    textbooks = os.listdir(os.path.join('out', 'textbooks'))
    for textbook in textbooks:
        with open(os.path.join('out', 'textbooks', textbook)) as f:
            textbookdata = json.loads(f.read())
            isbn = textbookdata['isbn_13'] or textbookdata['isbn_10']

            print('Registering Textbook: {}'.format(isbn))

            es.index(index=ES_INDEX, doc_type='textbook', id=isbn, body=textbookdata)

def denormalized_courses(es):
    """
    The courses(es) function inserts the raw courses into the elasticsearch database.
    For display purposes, it is nice to denormalize some of the section data into the
    course objects stored in elasticsearch. This function does that.
    """

    raw_courses = es.search(index=ES_INDEX, doc_type='raw_course', body={
        'query': {
            'match_all': {}
        }
    }, size=100000)['hits']['hits']

    # raw_courses = [x['_source'] for x in rraw_courses]

    for raw_course in raw_courses:
        course = raw_course['_source']
        rsections = es.search(index=ES_INDEX, doc_type='section', body={
            'query': {
                'bool': {
                    'must': [
                        {
                            'match': { 'course': course['number'] }
                        },
                        {
                            'match': { 'subject': course['subject'] }
                        }
                    ]
                }
            }
        }, size=100000)['hits']['hits']
        sections = [x['_source'] for x in rsections]

        # Record all of the seasons
        course['seasons'] = list({x['season'] for x in sections})

        print('Registering Denorm Course: {_id}'.format(**raw_course))

        es.index(index=ES_INDEX, doc_type='course', id=raw_course['_id'], body=course)


def main() :
    # Connect to the Elasticsearch instance
    es = Elasticsearch()

    # courses(es)
    sections(es)
    # subjects(es)
    # textbooks(es)
    # denormalized_courses(es)

if __name__ == '__main__':
    main()
