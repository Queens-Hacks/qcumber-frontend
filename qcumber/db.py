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
