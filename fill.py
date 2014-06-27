#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime
import os
import json

def is_current(section):
    """
    This function determines if a given section is current.
    I haven't checked to make sure that the logic makes sense... someone should do that

    If the event is in the future, it should always be included.
    If the event is in the past by more than 2 seasons, it should be excluded
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

    return now_num - section_num <= 2

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

            # Push the item into the elasticsearch
            es.index(index='qcumber', doc_type='course', id='{subject} {number}'.format(**cd), body=cd)

def sections(es):
    sections = os.listdir(os.path.join('out', 'sections'))
    for section in sections:
        with open(os.path.join('out', 'sections', section)) as f:
            sectiondata = json.loads(f.read())
            sd = sectiondata['basic']
            sd['classes'] = sectiondata['classes']

            if not is_current(sd): continue # Reject non-current sections

            es.index(index='qcumber', doc_type='section', id='{year} {season} {subject} {course} {solus_id}'.format(**sd), body=sd)

def subjects(es):
    subjects = os.listdir(os.path.join('out', 'subjects'))
    for subject in subjects:
        with open(os.path.join('out', 'subjects', subject)) as f:
            subjectdata = json.loads(f.read())
            es.index(index='qcumber', doc_type='subject', id=subjectdata['abbreviation'], body=subjectdata)

def textbooks(es):
    textbooks = os.listdir(os.path.join('out', 'textbooks'))
    for textbook in textbooks:
        with open(os.path.join('out', 'textbooks', textbook)) as f:
            textbookdata = json.loads(f.read())
            isbn = textbookdata['isbn_13'] or textbookdata['isbn_10']
            es.index(index='qcumber', doc_type='textbook', id=isbn, body=textbookdata)

def main() :
    # Connect to the Elasticsearch instance
    es = Elasticsearch()

    courses(es)
    sections(es)
    subjects(es)
    textbooks(es)

if __name__ == '__main__':
    main()
