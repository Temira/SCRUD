from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

import OutputUtil
import dbutil
from OutputUtil import *
import hashlib

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'your secret key'

def get_pwd():
    with open("password.txt") as f: return f.read().strip()

def make_form(file_name, inputs, values, table, optional=""):
    heading = create_element("head", f'''<meta charset="UTF-8">\n<title>{file_name}</title> <link rel="stylesheet" href="../static/mystyle.css">''')
    print(heading)
    form = ""
    for i in range(len(inputs)):
        form += f'<p>{inputs[i]}: <input type="text" name="{inputs[i]}" value="{values[i]}"/></p> \n'
    print(form)
    form += '\n<p><input type="submit" value="submit"/></p>'
    form = create_element("form", form, attributes=f'action="{table}" method="POST"')

    print(form)
    body = create_element("body", form)
    print(body)
    message = create_element("html", heading + body)
    print(message)
    write_file("./templates/"+file_name+".html", message)


# def make_form(file_name, inputs, values, table):
#     heading = create_element("head",
#     f'''<meta charset="UTF-8">\n<title>{file_name}</title> <link rel="stylesheet" href="../static/mystyle.css">''')
#     print(heading)
#
#     # Create the form table structure
#     form = create_element("table")
#     for i in range(len(inputs)):
#         tr = create_element("tr")
#
#         # Input label cell
#         label_td = create_element("td", inputs[i])
#         tr += label_td
#
#         # Input field cell
#         input_td = create_element("td")
#         input_element = create_element("input", "",attributes=f'type="text" name="{inputs[i]}" value="{values[i]}" class="form-input"')
#         input_td += input_element
#         tr += input_td
#
#         form += tr
#
#     # Submit button row
#     submit_tr = create_element("tr")
#     submit_td = create_element("td", attributes='colspan="2"')
#     submit_button = create_element("input", "", attributes='type="submit" value="Submit" class="submit-button"')
#     submit_td += submit_button
#     submit_tr += submit_td
#     form += submit_tr
#
#     form = create_element("form", form, attributes=f'action="{table}" method="post"')
#
#     body = create_element("body", form)
#     message = create_element("html", heading + body)
#     write_file("./templates/" + file_name + ".html", message)

def write_html_fileS(file_name, heading, headers, types, alignments, data, google_links=False, hrefs=None):
    # link_attributes = 'rel="stylesheet" href="myStyle.css"'
    # link = create_element(TAG_LINK, "", link_attributes, end_tag=False)
    # head = create_element(TAG_HEAD, link)
    style_sheet = "" #read_style()
    heading = create_element(TAG_H1, heading)
    table = create_table(headers, types, alignments, data, google_links, hrefs)
    style = create_element(TAG_STYLE, style_sheet)
    script = create_element(TAG_SCRIPT, sort_script)
    head = create_element(TAG_HEAD, style + script + ' <link rel="stylesheet" href="../static/mystyle.css">')
    body = create_element(TAG_BODY, '<div class="container"> ' + heading + table + ' </div>')
    print("BODY = "+ body)

    message = create_element(TAG_HTML, head + body)
    write_file(file_name, message)
    print("Wrote output file", file_name)

@app.route('/')
def hello_world():  # put application's code here
    return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    print('in login 1')
    msg = ''
    print("rf: ")
    for x in request.form: print(x)
    print(request.method)
    for y in request.args: print(y)
    if request.method == 'POST' and 'login' in request.form and 'password' in request.form:
        print('in if')
        password = get_pwd()
        typed_login = request.form['login']
        typed_password = request.form['password']
        typed_host = request.form['host']
        typed_port = int(request.form['port'])
        typed_database = request.form['database']
        conn = pymysql.connections.Connection(host=typed_host, user="root", passwd=password, db=typed_database, port=typed_port)
        cursor = conn.cursor()
        # md5_password = hashlib.md5(typed_password.encode('utf-8')).hexdigest()
        query = "SELECT * FROM users WHERE login = '" + typed_login + "' AND pwd = '" + typed_password + "'"
        print(query)
        cursor.execute(query)
        user_row = cursor.fetchone()
        if user_row:
            session['loggedin'] = True
            session['user_id'] = user_row[0]
            session['login'] = user_row[1]
            session['host'] = typed_host
            session['port'] = typed_port
            session['database'] = typed_database
            return render_template('home.html')
        else:
            msg = 'Incorrect login / password !'
    return render_template('login.html', msg=msg)
    # return msg


@app.route('/table/<name>', methods=['GET', 'POST'])
def search(name):
    query= "DESCRIBE "+ name
    headers, data = dbutil.run_query(query, "blah", session['database'],'Assignment17')
    print("query executed")
    # data = data[0]
    s = ""
    l = []
    for d in data:
        s += d[0] + "__"
        l.append(d[0])
    s.rstrip('__')
    values = [""] * len(l)
    if request.method == 'POST':
        query = f"SELECT * FROM {name} WHERE "
        criteria = ""
        for i in l:
            if request.form[f'{i}']:
                if criteria == '':
                    criteria += f"{i} = '{request.form[f'{i}']}'"
                else:
                    criteria += f" AND {i} = '{request.form[f'{i}']}'"
        print("CRITERIA = " + criteria)
        query+= criteria
        print(query)
        headers, data = dbutil.run_query(query, "blah", session['database'],'Assignment17')
        types = ["S"] * len(headers)
        alignments = ["l"] * len(headers)
        table = create_table(headers, types, alignments, data)
        print(table)
        write_html_fileS('./templates/search_results.html', 'Found:', headers, types, alignments, data)
        return render_template('search_results.html')
        #return redirect(url_for('search_res'))
        #return table
    make_form("search", l, values, name)
    return render_template('search.html')

@app.route('/delete/<name>', methods=['GET', 'POST'])
def delete(name):
    query= "DESCRIBE "+ name
    headers, data = dbutil.run_query(query, "blah", session['database'],'Assignment17')
    print("query executed")
    # data = data[0]
    s = ""
    l = []
    for d in data:
        s += d[0] + "__"
        l.append(d[0])
    s.rstrip('__')
    values = [""] * len(l)
    if request.method == 'POST':
        query = f"DELETE FROM {name} WHERE "
        criteria = ""
        for i in l:
            if request.form[f'{i}']:
                if criteria == '':
                    criteria += f"{i} = '{request.form[f'{i}']}'"
                else:
                    criteria += f" AND {i} = '{request.form[f'{i}']}'"
        query+= criteria
        print(query)
        dbutil.run_query(query, "blah", session['database'], 'Assignment17')
        return render_template('Deleted.html', criteria=criteria)
    make_form("delete", l, values, name)
    return render_template('delete.html')

@app.route('/create/<name>', methods=['GET', 'POST'])
def create(name):
    query= "DESCRIBE "+ name
    headers, data = dbutil.run_query(query, "blah", session['database'],'Assignment17')
    print("query executed")
    s = ""
    l = []
    for d in data:
        s += d[0] + "__"
        l.append(d[0])
    s.rstrip('__')
    values = [""] * len(l)
    if request.method == 'POST':
        query = f"INSERT INTO {name} "
        components = ""
        criteria = ""
        pretty = ""
        for i in l:
            if request.form[f'{i}']:
                if criteria == '':
                    criteria += i
                    components += "'"+request.form[f"{i}"]+"'"
                    pretty += f"{i} = '{request.form[f'{i}']}'"
                else:
                    criteria += f", {i}"
                    components += ", '"+request.form[f"{i}"]+"'"
                    pretty += f" AND {i} = '{request.form[f'{i}']}'"
        print("CRITERIA =" + criteria)
        print("Components =" + components)
        query+= f'({criteria}) VALUES ({components})'
        print(query)
        dbutil.run_query(query, "blah", session['database'], 'Assignment17')
        return render_template('Created.html', criteria=pretty)
    make_form("create", l, values, name)
    return render_template('create.html')

@app.route('/update/<name>', methods=['GET', 'POST'])
def update(name):
    query= "DESCRIBE "+ name
    headers, data = dbutil.run_query(query, "blah", session['database'],'Assignment17')
    print("query executed")
    s = ""
    l = []
    for d in data:
        s += d[0] + "__"
        l.append(d[0])
    s.rstrip('__')
    values = [""] * len(l)
    print("l= ", l)
    if request.method == 'POST':
        components = ""
        criteria = ""
        pretty = ""
        where = f"{l[0]} = "
        if request.form[l[0]]:
            where += "'" + request.form[l[0]] + "'"
            print(where)

        for i in l:
            if request.form[f'{i}']:
                if criteria == '':
                    criteria += i
                    pretty += f"{i} = '{request.form[f'{i}']}'"
                else:
                    criteria += f", {i}"
                    pretty += f" , {i} = '{request.form[f'{i}']}'"
        print("CRITERIA = " + criteria)
        print("Components = " + components)
        print("PRETTY= " + pretty)
        # url = url_for('update2', name=name, pretty=pretty)
        # print("URL= ", url)
        # return redirect(url)
        # query1 = f'''SELECT * FROM {name} WHERE {where}'''
        # print("query1= ", query1)
        # headers1, data1 = dbutil.run_query(query1, "blah", session['database'], 'Assignment17')
        query2 = f'''UPDATE {name} SET {pretty} WHERE {where}'''
        print("query2= ", query2)
        dbutil.run_query(query2, "blah", session['database'],'Assignment17')
        # query3 = f'''SELECT * FROM {name} WHERE {where}'''
        # print("query3= ", query3)
        # headers3, data3 = dbutil.run_query(query3, "blah", session['database'], 'Assignment17')
        msg = f'''<html> <head> <link rel="stylesheet" href="../static/mystyle.css"> </head> <body> 
        <h2> Successfully updated!</h2> </body> </html>'''
        OutputUtil.write_file('templates/update_success.html', msg)
        return render_template('update_success.html')

        #return update2(name, criteria, components, pretty)

    make_form("update", l, values, name)
    return render_template('update.html')

# @app.route('/update2/<name>/<pretty>', methods=['GET', 'POST'])
# def update2(name, pretty):
#     print("in update 2 name, pretty", name, pretty)
#     pretty = pretty.replace("_", " ")
#     print("PRETTY PLEASE " + pretty)
#     query = "DESCRIBE " + name
#     headers, data = dbutil.run_query(query, "blah", session['database'], 'Assignment17')
#     print("query executed")
#     s = ""
#     l = []
#     for d in data:
#         s += d[0] + "__"
#         l.append(d[0])
#     s.rstrip('__')
#     values = [""] * len(l)
#     if request.method == 'POST':
#         print("hey look I made it")
#         print(pretty)
#         query = f"UPDATE {name} SET "
#         query2 = f"WHERE {pretty}"
#         print(query + query2)
#     #     components = ""
#     #     criteria = ""
#     #     pretty2 = ""
#     #     for i in l:
#     #         if request.form[f'{i}']:
#     #             if criteria == '':
#     #                 criteria += i
#     #                 components += "'" + request.form[f"{i}"] + "'"
#     #                 pretty2 += f"{i}_=_'{request.form[f'{i}']}'"
#     #             else:
#     #                 criteria += f", {i}"
#     #                 components += ", '" + request.form[f"{i}"] + "'"
#     #                 pretty2 += f"_AND_{i}_=_'{request.form[f'{i}']}'"
#     #     print("PRETTY1= " + pretty)
#     #     print("PRETTY2= " + pretty2)
#     #     return render_template('home.html')
#     make_form("update2", l, values, name)
#     return render_template('update2.html')
#

@app.route("/search_res")
def search_res():
    return render_template('search_results.html')

@app.route('/table/<table>')
def results(table):
    query = "SELECT * FROM " + table
    headers, data = dbutil.run_query(query, "select all", "udb", "Assignment17")
    return render_template('search_results.html', headers=headers, data=data)

#A bunch of error messages
@app.errorhandler(Exception)
def handle_exception(error):
    # Custom error handling logic goes here
    return render_template('404.html'), 500

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    print('error!')
    return render_template('500.html'), 500

# a route that will trigger a 404 error
@app.route('/not_found')
def not_found():
    abort(404)

# a route that will trigger a 500 error
@app.route('/internal_server_error')
def internal_server_error():
    raise Exception('oops, something went wrong!')

if __name__ == '__main__':
    app.run()
