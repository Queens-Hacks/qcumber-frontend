from elasticsearch import Elasticsearch
import os
import json

def courses(es):
    courses = os.listdir(os.path.join('out', 'courses'))
    for course in courses:
        with open(os.path.join('out', 'courses', course)) as f:
            coursedata = json.loads(f.read())
            cd = coursedata['basic']
            cd.update(coursedata['extra'])

            # Push the item into the elasticsearch
            es.index(index='qcumber', doc_type='course', id=cd['subject'] + ' ' + cd['number'], body=cd)

def sections(es):
    sections = os.listdir(os.path.join('out', 'sections'))
    for section in sections:
        with open(os.path.join('out', 'sections', section)) as f:
            sectiondata = json.loads(f.read())
            sd = sectiondata['basic']
            sd['classes'] = sectiondata['classes']

            es.index(index='qcumber', doc_type='section', id=sd['subject'] + ' ' + sd['class_num'] + ' ' + sd['solus_id'], body=sd)

def subjects(es):
    subjects = os.listdir(os.path.join('out', 'subjects'))
    for subject in subjects:
        with open(os.path.join('out', 'subjects', subject)) as f:
            subjectdata = json.loads(f.read())
            es.index(index='qcumber', doc_type='subject', id=subjectdata['abbreviation'], body=subjectdata)

def main() :
    es = Elasticsearch()
    courses(es)
    sections(es)
    subjects(es)
    pass

if __name__ == '__main__':
    main()
