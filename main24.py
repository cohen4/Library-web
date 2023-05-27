# Importing
from flask import Flask, request, render_template, redirect, session
from flask_session import Session
import pymysql as mdb
from datetime import timedelta, date
import string #For books name
from Classes import *

app = Flask(__name__)       # Setting up our application - (__name__ is referencing this file)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

'''------------------------Data Base:-----------------------'''
#connect to the database
con = mdb.connect(host = "xxxx", user = "xxxx", passwd= "xxxx")
#get the cursor object
cursor = con.cursor()
cursor.execute("xxxx;")


'''------------------------static pages:-----------------------'''
@app.route('/')
def home_page():
    if session.get("email"):
        daily_order_update()
        daily_borrow_update()
        email = session.get("email")
        login_check = Login(email)
        user_name="Hello"+" "+login_check.fetch_name()+"!"
        if login_check.checking_user_kind() == "reader_login":   #Display home page with reader functions
            return render_template("home_page.html", reader_login="reader_login",user_name=user_name)
        if login_check.checking_user_kind() == "librarian_login": #Display home page with librarian functions
            return render_template("home_page.html", librarian_login="librarian_login",user_name=user_name)
    else:  #Display home page for everyone with sign in options for both readers and librarians
        return render_template('home_page.html')



'''-----------------------form pages:-----------------------'''

@app.route('/reader_registration', methods= ['POST', 'GET'])
def reader_reg():
    if request.method == 'POST':   #After the user has completed his reader sign-in form on the website
        email = request.form["email"]
        password = request.form["password"]
        first_name = request.form["first_name"].title()
        last_name = request.form["last_name"].title()
        date = request.form["birth_date"]
        phone = request.form["phone"]
        city = request.form["city"].title()
        street = request.form["street"].title()
        house = request.form["house"]
        create_reader = Reader(email, password, first_name, last_name, date, phone, city, street, house) #Create new object of class Reader
        if create_reader.checking_reader_existance() == "already exists":  #If the user tries to sign-up with an email that already in DB
            email_already_exists = "This email is already exits! Please register with another email."
            #returns a message to the user that he needs to sign-up with different email
            return render_template('reader_reg.html', email_already_exists = email_already_exists )
        else:
            create_reader.add_reader() #Use method of class Reader to insert all data about new reader to DB
            return render_template("reg_success.html", email = email, password = password, first_name = first_name, user_type='Reader',
                               last_name = last_name, type_of_date = 'Birth Date:', date = date ,
                               phone = phone, city = city, street = street, house = house, more='')
            #returns all data of the new reader for the user to see that the process went successfully
    else:
        today_date = today_dt()  #The user clicked on button "reader sign-up"
        return render_template('reader_reg.html', today_date = today_date)

@app.route('/librarian_registration' , methods= ['POST', 'GET'])
def lib_reg():   #After the user has completed his librarian sign-in form on the website
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        first_name = request.form["first_name"].title()
        last_name = request.form["last_name"].title()
        date = request.form["start_date"]
        phone = request.form["phone"]
        city = request.form["city"].title()
        street = request.form["street"].title()
        house = request.form["house"]
        branch =  request.form["branch"]
        create_librarian = Librarian(email, password, first_name, last_name, date, phone, city, street, house, branch)
        # Create new object of class Librarian
        if create_librarian.checking_reader_existance() == "already exists":   #If the user tries to sign-up with an email that already in DB
            email_already_exists = "This email is already exits! Please register with another email."
            return render_template('lib_reg.html', email_already_exists=email_already_exists)
            # returns a message to the user that he needs to sign-up with different email
        else:
            create_librarian.add_librarian()  #Use method of class Librarian to insert all data about new librarian to DB
            return render_template("reg_success.html", password = password, email=email, first_name=first_name, user_type='Librarian',
                    last_name=last_name, type_of_date='Employment Start Date:', date=date,
                    phone=phone, city=city, street=street, house =house ,more='Branch', branch=branch)
            # returns all data of the new librarian for the user to see that the process went successfully

    else:
        today_date = today_dt()  #The user clicked on button "librarian sign-up"
        return render_template("lib_reg.html", today_date = today_date)

@app.route('/enter_serial_no_book', methods=['POST', 'GET'])
def enter_serial_no_book():
    if request.method == 'POST':
        global serial_no_book
        serial_no_book = request.form["serial_no_book"]
        book_input = Check_Book(serial_no_book)
        message = book_input.checking_book_exist()  #Check if the serial number of the book that the librarian entered is already in DB
        if message == "book does not exist in DB":
            # If serial number of a book does not exists in DB, the librarian is transferred to "add book" page
            return render_template("add_book.html",serial_no_book=serial_no_book,
                                   name_not_exists="Book does not exist in branch!")

        else: #If serial number of a book already exists in DB
            create_new_book_copy = Book_Copy("Available", serial_no_book) #Creats new object of class Book Copy
            create_new_book_copy.add_book_copy() #Calls method of class Book Copy to insert all data about new copy to DB
            email = session["email"]
            branch = find_branch(email)
            serial_no_book_copy = find_last_serial_copy() #Returns id of the new copy of the book that was created in line 230
            add_copy_to_branch = Exist_In_Branch(branch, serial_no_book_copy)  #Creats new object of class Exist In Branch
            add_copy_to_branch.add_book_to_branch()  #Calls method of class Exist In Branch to insert all data about copy in branch to DB
            added_book = Check_Book(serial_no_book)  #Creats new object of class Check Book
            added_book.add_quantity()  #Calls method of class Check Book to update quantity of the book in DB
            all_data_about_book = added_book.extract_book_info()  #Extract all info about new copy of the book from DB
            quantity_in_branch = add_copy_to_branch.quantity_of_copies_in_branch(serial_no_book) #Update number of copies in branch
            return render_template("book_already_exist.html",
                                   all_data_about_book=all_data_about_book, quantity_in_branch = quantity_in_branch)
            #Returns all data of new book copy to the librarian to see that the process went successfully
    else:   #When the librarian clicks on button "Add Book"
        return render_template("enter_serial_no_book.html")


@app.route('/login', methods= ['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        login_check = Login(email, password)
        if login_check.checking_user_existance() == "reader_login":  #If the user logged in with an email that's in reader DB
            session["email"] = request.form["email"]
            user_name = "Hello" + " " + login_check.fetch_name() + "!"
            return render_template("home_page.html", reader_login = "reader_login",user_name=user_name)
            # Display home page with reader functions and also the reader's name
        if login_check.checking_user_existance() == "librarian_login":  #If the user logged in with an email that's in librarian DB
            session["email"] = request.form["email"]
            user_name = "Hello" + " " + login_check.fetch_name() + "!"
            return render_template("home_page.html", librarian_login = "librarian_login",user_name=user_name)
            # Display home page with librarian functions and also the librarian's name
        else:
            #Entered email is not in librarian or reader DB
            email_doesnt_exists = "This is a problem with the email or password. Please insert again."
            return  render_template('login.html', email_doesnt_exists = email_doesnt_exists)
            #Returns the same page with a message for the user to try and log in with different email

    else:
        #The user clicked on button "Log In"
        return render_template('login.html')

@app.route('/add_book', methods=['POST', 'GET'])
def add_book():
    if request.method == 'POST':  #After the librarian has entered all data about new book
        book_name = string.capwords(request.form["book_name"], ' ')
        author_name = request.form["author_name"].title()
        rel_date = request.form["rel_date"]
        publisher = request.form["publisher"].title()
        email= session["email"]
        serial_number = serial_no_book
        branch = find_branch(email)
        create_new_book = Books(serial_no_book, book_name, author_name, rel_date, publisher, 1) #Creats new object of class Books
        create_new_book_copy = Book_Copy("Available", serial_no_book) #Create new object of class Book Copy
        create_new_book.add_new_book()  #Calls method of class Books to insert all data about new book to DB
        create_new_book_copy.add_book_copy() #Calls method of class Book Copy to insert all data about new copy of the book
        serial_no_book_copy=find_last_serial_copy()  #Returns id of the new copy of the book that was created in line 286
        add_new_book_to_branch=Exist_In_Branch(branch,serial_no_book_copy) #Create new object of class Exist In Branch
        add_new_book_to_branch.add_book_to_branch() #Calls method of class Exist In Branch to insert all data of book copy in branch to DB
        return render_template("book_success.html", serial_number=serial_number, book_name=book_name,
                               author_name=author_name
                               , rel_date=rel_date, publisher=publisher, branch=branch)
        #Returns all data about new book for the librarian to see that the process went successfully
    else:
        #Librarian has entered a new serial number of a book that does not exist in DB
        return render_template("add_book.html")

@app.route("/logout")
def logout(): #If the user clicked on button "Log Out"
    session["email"] = None
    return render_template("home_page.html")

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        input_search = request.form["search_input"]
        input_search_kind = request.form["search_kind"]
        look_for_books = Search(input_search)  #Creats new object of class Search
        books_found = look_for_books.search_book(input_search_kind) #Looks for relatable data to the user input in book and book copy DB
        if books_found == 'not found':  #If it did not yield any relatable data returns "not found" page
            return render_template("not_found.html")
        else:
            # Append to the original list, the branches thats hold each book
            branch_holds_book = look_for_books.find_branches_hold_book(books_found)
            #Append to the new list the available quantity of each book in the branches that hold it
            quantity_of_branch_holds_book = look_for_books.quantity_in_each_branch(branch_holds_book)
            #Append to the newest list. for each book in it we append the phone number of each branch that holds it
            quantity_and_phones_of_branches = look_for_books.find_branch_phone(quantity_of_branch_holds_book)
            if check_if_reader_search() == "reader exists":
                return render_template("search_results.html", quantity_of_branch_holds_book = quantity_and_phones_of_branches,
                                                                                        reader_login = "reader_login")
            #Return all relatable data to the reader input and also data about availability of the requested books, also with "order book" option
            else:
                return render_template("search_results.html",quantity_of_branch_holds_book=quantity_and_phones_of_branches)
            # Return all relatable data to the user input and also data about availability of the requested books,not with "order book" option

    else:
        return render_template('search.html')

@app.route('/borrow_book',methods=['POST', 'GET'])
def borrow_book():
    if request.method == 'POST':
        serial_number_book = request.form["serial_number_book"]
        member_mail=request.form["member_mail"]
        checking_existance = Login(member_mail)
        if checking_existance.checking_reader_existance() == "reader exists": #Checks if the entered reader email exists in DB
            borrow_start_date = date.today()
            book_to_borrow = Check_Book(serial_number_book) #Create object of class Check Book
            if count_member_borrowed_books(member_mail) >= 3:  #If the reader already has 3 borrowed books at the moment
                cannot_borrow="The member already has 3 borrowed books at the moment,cannot borrow more"
                return render_template("borrowing_book.html",cannot_borrow=cannot_borrow)
            elif book_to_borrow.available_books(member_mail) is None: #If there are not any available copies of the requested book to borrow in branch
                book_not_found="The book you tried to borrow is not available,please try another book"
                return render_template("borrowing_book.html",book_not_found=book_not_found)
            else:
                borrow_end_date=rent_default_date()
                selected_copy_to_borrow= book_to_borrow.available_books(member_mail)
                borrowed_copy= Borrowed_Book(selected_copy_to_borrow,borrow_start_date,borrow_end_date,member_mail)
                #Create new object of class Borrowed Book
                borrowed_copy.add_borrow_book() #Calls method of class Borrowed Book to insert all data about the borrow to DB
                borrowed_copy.update_status()   #Calls method of class Borrowed Book to update status of the copy to "Borrowed" in DB
                email=session["email"]
                branch = find_branch(email)
                number_of_available_book_after_borrow=Exist_In_Branch(branch,selected_copy_to_borrow)
                quantity=number_of_available_book_after_borrow.count_number_of_available_books_in_branch(serial_number_book)
                #Returns quantity of available copies of the requested book in branch after borrow
                all_data_about_borrowed_book=extract_borrowed_book_info(selected_copy_to_borrow)
                #Extract all data about the borrow of the book copy from DB
                return render_template("borrow_success.html",all_data_about_borrowed_book=all_data_about_borrowed_book,
                                       member_mail=member_mail,quantity=quantity)
                #Returns all data about the borrow to the librarian to see that the process went successfully
        else:
            return render_template('borrowing_book.html', borrow_start_date=date.today(),
                email_not_exists = "This email doesn't exsits, please tell the reader to register or try another email")
            #If the librarian has entered email that does not exist in reader DB
    else:   #If the librarian has clicked on button "Borrow Book"
        return render_template('borrowing_book.html',borrow_start_date=date.today())

@app.route('/borrow_history',methods=['POST', 'GET'])
def borrow_history():
        member_mail=session["email"]
        member_login = Login(member_mail)
        member_name = member_login.fetch_name()  #Calls a function that exrtact reader's name from DB based on his email
        member_borrow_history = reader_borrow_history(member_mail) #Extract of data of reader's borrow history from "borrow book" DB
        if str(member_borrow_history) == "zero books borrowed by member":
            answer="We did not find any books borrowed by this member"
            return render_template("borrow_history_result.html",answer=answer, member_name = member_name)
            #If there are zero borrowed books in reader's borrow history,returs a message to the reader
        else:
            date_today = date.today()
            return render_template("borrow_history_result.html",member_borrow_history=member_borrow_history
                            ,member_name=member_name,date_today=date_today)
            #Returns reader's borrow history with all data from "borrow book" DB, also with option to extend borrow if possible


@app.route('/extend_borrow',methods=['POST', 'GET'])
def extend_borrow():
    if request.method == "POST":
        sn_book_copy=request.form["serial_number_book_copy"]
        member_mail=request.form["member_mail"]
        borrow_start_date=request.form["borrow_start_date"]
        if check_if_book_is_ordered(sn_book_copy):  #If the requested copy of the book was ordered by another reader
            borrow_extend_request_date = date.today()
            update_borrow_extension_request_date(sn_book_copy, member_mail, borrow_start_date,borrow_extend_request_date)
            return render_template("cannot_extend_borrow.html")
        else:
            borrow_extend_request_date = date.today()
            update_borrow_extension_request_date(sn_book_copy,member_mail,borrow_start_date,borrow_extend_request_date)
            #Update borrow extension request date in DB to current date
            extended_borrow_date=extend_rent_date(sn_book_copy,member_mail,borrow_start_date)
            return render_template("extend_borrow.html",extended_borrow_date=extended_borrow_date,
                                   sn_book_copy=sn_book_copy,member_mail=member_mail,
                                   borrow_extend_request_date=borrow_extend_request_date)
            #Return a page with all the info about the data of extend borrow with final borrow date set to be
            #14 days from borrow start date

    else:   #If the reader clickes of button "Extend Date" for specific copy in his borrow history page
        return render_template("extend_borrow.html")


@app.route('/order_book', methods=['POST', 'GET'])
def order_book():
    if request.method == 'POST':
        serial_number_book = request.form["serial_number_book"]
        branch_name = request.form["branch_name"]
        email = session["email"]
        create_order = Order_Book(serial_number_book, branch_name, email) #Crate new object of class Order Book
        order_result = create_order.try_to_order() #Calls a method from class Order Book to check if the requested book copy can be ordered
        if order_result == "high demand": #If the reader tried to order a copy that's not available to order due to high demand
            return render_template("cant_order.html")
        else:
            final_collection_date = final_order_collection_date(order_result[-1])
            return render_template("order_book.html", all_order_data = order_result, final_collection_date = final_collection_date)
            #Returns a page with all data about order book copy for the reader to see that the process went successfully
    else:   #If the reader clicked on button "Home Page"
        return render_template('home_page.html')

@app.route('/ordered_books_list', methods=['POST', 'GET'])
def ordered_books_list():
    email = session.get("email")
    ordered_books_list = make_ordered_books_list(email) #Get two values in list
    waiting_for_you = ordered_books_list[0] #Books that wait for the reader to take them
    still_not_return = ordered_books_list[1] #Books that still not return by the borrower
    return  render_template("ordered_books_list.html", waiting_for_you = waiting_for_you, still_not_return = still_not_return)
    #Return a page with all data about reader's order history


con.commit()
cursor.close()
con.close()

if __name__ == "__main__":
    app.run(debug=True)