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


def group_by_course_num(courses):
    """
    Groups courses based on their course number. This is done rather than
    grouping based on career, as the career values contain options other than
    graduate/undergraduate, which adds noise and can make it difficult to find
    the information you are looking for.
    """

    groups = {}

    # Group by keys
    for course in courses:
        key = course['number'][0]

        if key in groups:
            groups[key].append(course)
        else:
            groups[key] = [course]

    # Sort by the keys, mostly ascending (P should come before everything else
    return sorted(groups.iteritems(),
                  key=lambda x: '0' if x[0] == 'P' else x[0])
