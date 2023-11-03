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
    return render_template('main.html',title='Hello')

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
    else: # Post - redirect
        movieDict = request.form
        conn = dbi.connect()
        tt = movieDict.get('movie-tt')
        existingMovieTitle = crud.check_tt_exists(conn, tt)
        # Before inserting, check that a movie with this tt does not already exist in the database
        if existingMovieTitle != None: # a movie with this tt already exists
            title = existingMovieTitle.get('title')
            flash(f"ERROR: movie exists; The movie, {title}, with tt = {tt} is already in database.")
        else: # No movie with this tt exists in the database
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

@app.route('/select/')
def select():
    '''
    On GET shows a menu of movies with incomplete information, (null value for either release or director)
    On POST redirects to the /update/nnn page for that movie
    '''
    return render_template('select_menu.html', page_title='Select Incomplete Movie')

@app.route('/update/<int:tt>', method=['GET','POST']) # require an integer
def update(tt):
    '''
    Shows a form for updating a particular movie, with the TT of the movie in the URL on GET.
    On POST does the update and shows the form again.
    '''
    conn = dbi.connect()
    movieDict = crud.movie_details(conn, tt)
    tt_old = movieDict.get('tt')
    if request.method == 'POST':
        # if updating the form
        # check new tt (is there an existing movie with this tt? if yes, flash error, if no, proceed)
        # check whether director nm exists
        # convert values to None
        # 
        # if deleting the form
        # find movie with the given tt and delete the row from the movie table
        flash(f'TO DO: Movie ({movieDict.get('title')}) was updated successfully')
    return render_template('update_form.html', page_title='Fill in Missing Data', movieDict = movieDict)

# You will probably not need the routes below, but they are here
# just in case. Please delete them if you are not using them

@app.route('/INSERT2/', methods=['GET','POST'])
def INSERT2():
    if request.method == 'GET':
        return render_template(
            'insert_form.html',
            page_title = 'Insert Movie')
    else: # Post - redirect
        movieDict = request.form
        conn = dbi.connect()
        confirmation = crud.insert_movie(conn, movieDict) # Insert movie into database
        # redirect to update page for reloads
        tt = request.form.get('tt')
        # redirect is a new import from flask
        return redirect(url_for('update',tt=tt))

@app.route('/country/<city>')
def country(city):
    if city in countries.known:
        return render_template(
            'msg.html',
            msg=('{city} is the capital of {country}'
                 .format(city=city,
                         country=countries.known[city])))
    else:
        return render_template(
            'msg.html',
            msg=('''I don't know the country whose capital is {city}'''
                 .format(city=city)))

@app.route('/greet/', methods=["GET", "POST"])
def greet():
    if request.method == 'GET':
        return render_template('greet.html', title='Customized Greeting')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )

@app.route('/formecho/', methods=['GET','POST'])
def formecho():
    if request.method == 'GET':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.args)
    elif request.method == 'POST':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.form)
    else:
        # maybe PUT?
        return render_template('form_data.html',
                               method=request.method,
                               form_data={})

@app.route('/testform/')
def testform():
    # these forms go to the formecho route
    return render_template('testform.html')


if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    db_to_use = 'kb102_db' 
    print('will connect to {}'.format(db_to_use))
    dbi.conf(db_to_use)
    app.debug = True
    app.run('0.0.0.0',port)
