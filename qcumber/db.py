# get a db cursor

#list of all subjects

# course by subject abbreviation / course number
# detailed course info, join in sections, textbooks
import psycopg2
import psycopg2.extras

try:
    from qcumber import config
except ImportError:
    from qcumber import default_config as config

def get_connection():
    conn = psycopg2.connect(database=config.db_name, user=config.db_user, host=config.db_host, password=config.db_password)
    return conn

def query(*args):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(*args)
        results = cur.fetchall()
    conn.close()
    return results

def dict_query(*args):
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(*args)
        results = cur.fetchall()
    conn.close()
    return results

def section_get_classes(section):
    section['classes'] = dict_query("""
                SELECT sc.*, scina.instructors
                FROM
                    queens.section_classes sc
                        LEFT JOIN queens.section_class_instructors_name_arr scina
                            ON (id = section_class_id)
                WHERE section_id = %s
                """, (section['id'],))
    return section

def course_by_abbrev(subject_abbr, course_num):
    subject = subject_by_abbrev(subject_abbr)
    course = dict_query("""
        SELECT * FROM queens.courses
        WHERE subject_id = %s AND number = %s""", (subject['id'], course_num))[0]
    return subject, course

def subject_by_abbrev(subject_abbr):
    subject = dict_query("""
        SELECT * FROM queens.subjects
        WHERE abbreviation = %s""", (subject_abbr,))[0]
    return subject


def search_courses(qargs):
    q = {
        'query': """
            SELECT
                c.*,
                cso.seasons::text[],
                s.abbreviation as subject_abbr
            FROM
                queens.courses c
                    JOIN queens.subjects s ON (c.subject_id = s.id)
                    LEFT JOIN queens.course_seasons_offered cso ON (c.id = cso.course_id)
            """,
        'where_count': 0,
    }
    if 'subject' in qargs:
        add_condition(q, "s.abbreviation LIKE %(subject)s||'%%'")
    if 'course' in qargs:
        add_condition(q, "c.number LIKE %(course)s||'%%'")
    if 'units' in qargs:
        add_condition(q, "c.units = %(units)s")
    if 'seasons' in qargs:
        # TODO should cast input and catch proper error
        add_condition(q, "cso.seasons::text[] && %(seasons)s")
    if 'career' in qargs:
        add_condition(q, "c.career = %(career)s")
    return dict_query(q['query'], qargs)

def add_condition(q, condition):
    if (q['where_count'] == 0):
        q['query'] += " WHERE "
    else:
        q['query'] += " AND "
    q['query'] += condition
    q['where_count'] += 1

