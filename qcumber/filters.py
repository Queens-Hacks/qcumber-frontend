"""
Template Filters used by the Qcumber frontend
"""
from datetime import datetime
from flask import Markup, escape
from qcumber import APP, util

@APP.template_filter('nl2br')
def nl2br(string):
    """
    Convert newlines into <br> tags, and produce HTML.
    Also escapes all of the text passed in
    """
    # some environments don't use unicode
    try:
        string = string.decode('utf8')
    except:
        pass
    return Markup('<br>'.join([escape(x) for x in string.split('\n')]))


@APP.template_filter('slugify')
def slugify(value):
    """
    Transform the input value to have no spaces and be uniformly lowercase
    """
    return '_' + value.replace(' ', '-').lower()


@APP.template_filter('oldterm')
def is_oldterm(term):
    """
    Returns True if the term is old
    """
    now = datetime.now()
    now_rank = now.year * 3 + (now.month - 1) // 4
    return now_rank > util.term_ordering(term)


@APP.template_filter('timeformat')
def format_time(value):
    """
    Format a time for display
    """
    if value:
        # pylint: disable=E1101
        return value.strftime("%I:%M%p")
    else:
        return ''


@APP.template_filter('dayformat')
def format_day(value):
    """
    Format a day for display
    """
    if value:
        day = dateutil.parser.parse(value)
        # pylint: disable=E1101
        return day.strftime("%B %d %Y")
    else:
        return 'N/A'


@APP.template_filter('dayofweek')
def format_dow(value):
    """
    Format an integer day of week into a full-word day of week
    """
    if value:
        return {
            'SUNDAY':   'Sunday',
            'MONDAY':   'Monday',
            'TUESDAY':  'Tuesday',
            'WEDNESDAY':'Wednesday',
            'THURSDAY': 'Thursday',
            'FRIDAY':   'Friday',
            'SATURDAY': 'Saturday',
        }[value]
    else:
        return 'N/A'


@APP.template_filter('fancy_section_type')
def fancy_section_type(section):
    """
    Transform 3-letter section type into a nicer format for display
    """
    return {
        'LEC': 'Lecture',
        'LAB': 'Laboratory',
        'TUT': 'Tutorial',
        'PRA': 'Practicum',
        'COR': 'Correspondence',
        'SEM': 'Seminar',
        'ONL': 'Online',
    }.get(section, section)
