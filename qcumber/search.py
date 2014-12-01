# pylint: disable=C0111

from elasticsearch import Elasticsearch

# An arbitrary large number to pass as the maximum # of entries to return
BIGNUM = 10000

# The name of the search index
INDEX = 'qcumber'

# Connect to the elasticsearch database
ES = Elasticsearch()


def extract_source(res):
    """
    Extract the _source property of every element in the res list
    """
    return [item['_source'] for item in res]


def subjects():
    """
    Get a list of all of the subjects
    """

    # pylint: disable=E1123
    res = ES.search(index=INDEX, doc_type='subject', body={
        'sort': [
            {'abbreviation': {'order': 'asc'}}
        ],
        'query': {
            'match_all': {}
        }
    }, _source=True, size=BIGNUM)['hits']['hits']

    return extract_source(res)


def subject(subject_id):
    """
    Get an individual subject based on its subject code
    """
    subject_id = subject_id.upper()
    return ES.get(index=INDEX, doc_type='subject', id=subject_id)['_source']


def course(subject_id, course_id):
    """
    Get an individual course based on its subject & course code
    """
    subject_id = subject_id.upper()
    course_id = course_id.upper()

    return ES.get(index=INDEX,
                  doc_type='course',
                  id='{} {}'.format(subject_id, course_id))['_source']


def textbooks(subject_id, course_id):
    """
    Get a list of textbooks for the course defined by the subject_id & course code
    """
    subject_id = subject_id.upper()
    course_id = course_id.upper()

    # pylint: disable=E1123
    textbook_list = ES.search(index=INDEX, doc_type='textbook', body={
        'query': {
            'match_phrase': {
                'courses': '{} {}'.format(subject_id, course_id)
            }
        }
    }, _source=True, size=BIGNUM)['hits']['hits']

    return extract_source(textbook_list)


def sections(subject_id, course_id):
    """
    Get a list of sections for the course defined by the subject_id & course code
    """
    subject_id = subject_id.upper()
    course_id = course_id.upper()

    # pylint: disable=E1123
    sects = ES.search(index=INDEX, doc_type='section', body={
        'query': {
            'bool': {
                'must': [
                    {'match': {'course': course_id}},
                    {'match': {'subject': subject_id}}
                ]
            }
        }
    }, _source=True, size=BIGNUM)['hits']['hits']

    # XXX: Dirty Hack
    # The timetable code requires the subject's ID to be avaliable in the
    # target page, but that id isn't stored anywhere in _source. Thus,
    # we attach it here
    for sect in sects:
        sect['_source']['_id'] = sect['_id']

    return extract_source(sects)


def section(section_id):
    """
    Get an individual section from the database based on its _id
    """
    return ES.get(index=INDEX, doc_type='section', id=section_id)['_source']


def search_query(query, force_all=False):
    """
    Perform a search query against the elastic search database using the
    given query string
    """

    # TODO: In the future, use our own query parser rather than query_string_query
    query = query.strip()

    # pylint: disable=E1123
    results = ES.search(index=INDEX, doc_type='course', body={
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

    return extract_source(results)
