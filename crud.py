from flask import flash

import cs304dbi as dbi
import os
myStaffId = os.getuid()

def find_incomplete_movies(conn):
    """
    Returns the titles and tts of movies without release dates or without directors
    """
    curs = dbi.dict_cursor(conn)
    curs.execute(
        """
        select tt, title from movie 
        where (director is null) or (`release` is null);
        """
    )
    return curs.fetchall()


def update_movie(conn, formData, tt_old):
    """
    Change the data associated with a movie whose tt is movDict.get('tt')
    Checks validity of input data
    """
    cursOld = dbi.dict_cursor(conn)
    cursNew = dbi.dict_cursor(conn)
    tt_Form = formData.get('movie-tt')
    cursOld.execute(# Find the movie's previous data
        """
        select tt, title, `release`, director, addedby
        from movie
        where tt = %s;
        """, [tt_old]
    )
    oldMovie = cursOld.fetchone()

    # convert string 'None' to actual Nones
    movieData = {}
    for elt in formData:
        if formData.get(elt) == 'None':
            movieData[elt] = None
        elif formData.get(elt) == '':
            movieData[elt] = None
        else:
            movieData[elt] = formData.get(elt)
    
    # check whether title has changed
    newTitle = movieData.get('movie-title')
    titleSuccess = (str(newTitle) != str(oldMovie.get('title')))

    # check that director exists in person table
    newDirector, directorSucess = check_director_valid(conn, oldMovie.get('director'), movieData.get('movie-director'))
    
    # check that tt is available
    tt_new, ttIsAvail = check_tt_avail(conn, oldMovie.get('tt'), movieData.get('movie-tt'))

    #check that staff exists, if they do exist, proceed and otherwise flash error
    newStaff, staffSuccess = check_addedby_exists(conn, oldMovie.get('addedby'), movieData.get('movie-addedby'))

    #check that release year is a valid int
    newRelease, releaseSuccess = check_release_valid(conn, oldMovie.get('release'), movieData.get('movie-release'))

    results = [directorSucess, ttIsAvail, staffSuccess, releaseSuccess, titleSuccess]
    print(f"directorSucess: {results[0]}, ttIsAvail: {results[1]}, staffSuccess: {results[2]}, releaseSuccess: {results[3]}")
    
    # if tt has not changed or tt is unique, proceed
    if (str(tt_old) == str(tt_Form)) or (ttIsAvail):
        print(f"tt_old: {tt_old}, tt_Form:{tt_Form}, ttIsAvail: {ttIsAvail}")
        # make those changes
        cursNew.execute(# Update movie with new data
        """
            update movie
            set tt = %s, title = %s, `release` = %s, director = %s, addedby = %s
            where tt = %s;
        """, [tt_new, newTitle, newRelease, newDirector, newStaff, tt_old]
        )
        conn.commit()
        # Flash the result to user
        if not (True in results): # everything failed
            flash(f"No changes to movie database were made")  
        else: # something was updated to a valid value
            flash(f"Movie ({movieData.get('movie-title')}) was updated successfully")
    else: # if tt is not unique (is associated with another show), tell app.py to flash an error
        flash(f'Movie already exists')
    return tt_new


def check_tt_avail(conn, tt_current, tt_proposed):
    """
    Takes current tt and the proposed tt. If the proposed tt doesnt belong to an existing movie or belongs to an existing movie, returns the proposed tt
    If the new tt is not valid, then return the current tt
    """
    if tt_proposed == None: # empty tt given
        flash(f"Movie ID must not be empty. Using current ID of {tt_current}")
        return tt_current, False
    elif (str(tt_current) != str(tt_proposed)): # A change was proposed
        ttTest = check_tt_exists(conn, tt_proposed) # is tt_proposed in use elsewhere?
        if (ttTest != None): # proposed tt is associated with another movie
            flash(f"Movie with ID {tt_proposed} already exists. Using current ID of {tt_current}")
            return tt_current, False        
        else: # tt_proposed is available
            return tt_proposed, True
    else: # tt has not changed
        return tt_current, False

def check_release_valid(conn, release_current, release_proposed):
    """
    Takes current release year and the proposed release. If the proposed year is valid, returns the proposed year and true
    If the new release is not valid, then return the current release year and false
    """
    if (str(release_current) == str(release_proposed)): # no change proposed
        return release_current, False
    #convert to int
    try:
        release_proposed_int = int(release_proposed)
        if release_proposed_int < 0:
            print(f"{release_proposed_int} is less than zero")
            raise(ValueError)
        else:
            print(f"{release_proposed_int} is valid int")
            return release_proposed, True
    except: # ValueError:
        print(f"Using {release_current}")
        flash(f"Year {release_proposed} is invalid, year must be a positive int. Using previous release of {release_current}")
        return release_current, False


def check_director_valid(conn, nm_current, nm_proposed):
    """
    Takes current nm and the proposed nm. If the proposed nm is valid, returns the proposed nm
    If the new nm is not valid, then return the current nm
    """
    # assume already valid if nm_current == nm_proposed:
    if (str(nm_current) == str(nm_proposed)):
        return nm_current, False
    elif (nm_proposed == None): # data was removed
        return nm_proposed, True
    # valid if director nm_proposed exists
    curs = dbi.dict_cursor(conn)
    curs.execute(
        """
        select nm from person
        where nm = %s;
        """, [nm_proposed]
    )
    result = curs.fetchone()
    if (result == None):
        flash(f"Director with ID {nm_proposed} does not exist. Using old ID of {nm_current}")
        return nm_current, False
    else:
        return nm_proposed, True


def delete_movie(conn, tt):
    """
    Remove movie with given tt from the database
    Assumes the tt is valid
    """
    curs = dbi.dict_cursor(conn)
    curs.execute(
        """
        delete from movie
        where tt = %s;
        """, [tt]
    )
    conn.commit() # Makes the deletion permanent

def movie_details(conn, tt):
    """
    Returns a dict with information about a given movie based on the tt
    """
    cursMovie = dbi.dict_cursor(conn)
    cursDirector = dbi.dict_cursor(conn)
    cursMovie.execute( # find the given movie
        '''
        select tt, title, `release`, director as 'directorid', addedby
        from movie
        where tt = %s;
        ''', [tt]
    )
    cursDirector.execute( # find the given movie
        '''
        select name
        from person inner join movie on (director = nm)
        where tt = %s;
        ''', [tt]
    )
    movDict = cursMovie.fetchone()
    if movDict != None:
        director = cursDirector.fetchone()
        movDict['directorName'] = director.get('name') if (director != None) else ('none specified')  
    return movDict

def check_tt_exists(conn, tt):
    """
    If a movie with the given tt is in the database, return a dictionary containing the title of the movie
    If a movie with the given tt does NOT exist in the database, return None
    """
    curs = dbi.dict_cursor(conn)
    curs.execute( # search for the given movie
        '''
        select title from movie
        where tt = %s;
        ''', [tt]
    )
    return curs.fetchone()

def check_addedby_exists(conn, addedby_current, addedby_proposed):
    """
    If the proposed addedby is in the database, return proposed added by and true
    If the proposed addedby is not in the database, return current added by and false
    """
    # if addedbys are idential, assume addedby_current is valid
    if (str(addedby_current) == str(addedby_proposed)):
        return addedby_current, False
    # A change was proposed:
    curs = dbi.dict_cursor(conn)
    curs.execute( # search for the given addedby
        '''
        select uid from staff
        where uid = %s;
        ''', [addedby_proposed]
    )
    result = curs.fetchone()
    print(result)
    if result == None:
        flash(f"Staff member with ID {addedby_proposed} doesn't exist. Using previous added by of {addedby_current}")
        return addedby_current, False
    else:
        return addedby_proposed, True
    
def insert_movie(conn, formData):
    """
    Insert a movie row into movie table
    using tt, title, and release year
    Assumes that title, addedby, and tt are filled in
    """
    curs = dbi.dict_cursor(conn)
    curs.execute( # insert given movie into movie table
        '''
        insert into movie(tt, title, `release`, addedby)
        values (%s, %s, %s, %s);
        ''', [formData.get('movie-tt'), formData.get('movie-title'), formData.get('movie-release'), myStaffId]
    )
    conn.commit() # Makes the change permanent
    return 'You just added {title} at tt = {tt}'.format(title=formData.get('movie-title'), tt=formData.get('movie-tt'))



if __name__ == '__main__':
    database = os.getlogin() + '_db'
    dbi.conf(database)
    conn = dbi.connect()
    #print(movie_details(conn, 555))
    #print(delete_movie(conn, 555))
    # fakeMovie = {'tt':556, 'title':'The Worst Movie You Ever Wasted 3 Hours On', 'addedby':myStaffId}
    # success = insert_movie(conn, fakeMovie)
    """     shows = find_incomplete_movies(conn)
    for i in range(10):
        print(f"{shows.get('title')} has tt {shows.get('tt')}") """
    check_release_valid(conn,2024, -1)
    check_release_valid(conn,2024, 2020)
    check_release_valid(conn,2024, "ehofidskl")
    # print(success)
    