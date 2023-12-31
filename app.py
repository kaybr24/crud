from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
import crud

import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def home():
    '''
    Shows the basic navigation. 
    You can redirect to here when you have no place better to go, such as when a movie is deleted.
    '''
    return render_template('main.html', page_title='WMDB Interactions')

@app.route('/insert/', methods=["GET", "POST"])
def insert():
    '''
    Gives the insert form on a GET and processes the insertion on a POST 
    (and then redirects to the /update/nnn page)
    '''
    if request.method == 'GET':
        return render_template(
            'insert_form.html',
            page_title = 'Insert Movie')
    else: # Post -> redirect
        movieDict = request.form.to_dict()
        conn = dbi.connect()

        ## tt checking
        tt = movieDict.get('movie-tt')
        if len(tt) < 1: # box was left blank
            print(f"User forgot to fill out a tt")
            flash(f"ERROR: Movie ID must not be empty")
            return redirect(url_for('insert'))
        elif not tt.isdigit(): 
            # checks that tt is a digit value
            flash(f'ERROR: movie ID must be a positive integer number.  Got {tt}')
            return redirect(url_for('insert'))
        existingMovieTitle = crud.check_tt_exists(conn, tt)
        # Before inserting, check that a movie with this tt does not already exist in the database
        if existingMovieTitle != None: # a movie with this tt already exists
            print(f"The user's tt is already in use")
            title = existingMovieTitle.get('title')
            flash(f"ERROR: movie exists; The movie, {title}, with tt = {tt} is already in database.")
            # redirect to update page for reloads
            return redirect(url_for('update',tt=tt))

        ## title checking
        elif len(movieDict.get('movie-title')) < 1:
            print(f"The user forgot to provide a title")
            flash(f"ERROR: a movie title is required")
            return redirect(url_for('insert'))
        # No movie with this tt exists in the database, proceed
        else: 
            # Convert blank boxes to None (release year is the only possibility)
            for key in movieDict:
                if movieDict[key] == "": # the user didn't answer this question
                    movieDict[key] = None
            # Insert the data into movieDict
            confirmation = crud.insert_movie(conn, movieDict) # Insert movie into database
            print(confirmation) # to console
            title = movieDict.get('movie-title')
            flash(f"Movie {title} inserted.")
            # redirect to update page for reloads
            return redirect(url_for('update',tt=tt))

@app.route('/search/')
def search():
    '''
    *OPTIONAL*
    Shows a search form to search by partial title on GET 
    and on POST does the search and redirects to the appropriate place 
    (/update/nnn if the page exists and the search page if it doesn't)
    '''
    return render_template("search_form.html", page_title = 'Search for a Movie')

@app.route('/select/', methods=['GET', 'POST'])
def select():
    '''
    On GET shows a menu of movies with incomplete information, (null value for either release or director)
    On POST redirects to the /update/nnn page for that movie
    '''
    conn = dbi.connect()
    if request.method == 'GET':
        incomplete_movies = crud.find_incomplete_movies(conn)
        return render_template('select_menu.html', 
            page_title='Select Incomplete Movie', 
            data = incomplete_movies)
    else: # method = post
        tt = request.form.get('menu-tt')
        return redirect(url_for('update',tt=tt))

@app.route('/update/<int:tt>', methods=['GET','POST']) # require an integer
def update(tt):
    '''
    Shows a form for updating a particular movie, with the TT of the movie in the URL on GET.
    On POST does the update and shows the form again.
    '''
    conn = dbi.connect()
    tt_old = tt
    if request.method == 'POST':
        
        # (TO DO) convert values to None

        if request.form.get('submit') == 'update': # if updating the form, check values
            tt_new = crud.update_movie(conn, request.form, tt_old)
            if (tt_new != tt_old): # if tt changed, redirect to new page
                return redirect(url_for('update', tt=tt_new))
            else: # update data for page rendering
                movieDict = crud.movie_details(conn, tt_new)
        elif request.form.get('submit') == 'delete': # find movie with this tt and delete the movie
            movieDict = crud.movie_details(conn, tt)
            crud.delete_movie(conn, tt_old)
            flash(f"Movie ({movieDict.get('title')}) was deleted successfully")
            return redirect(url_for('home'))
        else:
            flash(f"ERROR: neither update or delete")
    else: # request.method == 'GET':
        movieDict = crud.movie_details(conn, tt)
        if movieDict == None:
            flash(f'{tt} is not a valid tt')
            return redirect(url_for('home'))
    return render_template('update_form.html', page_title='Fill in Missing Data', movieDict = movieDict)


if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
        database = os.getlogin() + '_db'
    db_to_use = database
    print('will connect to {}'.format(db_to_use))
    dbi.conf(db_to_use)
    app.debug = True
    app.run('0.0.0.0',port)
