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


def group_by_career(courses):
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
