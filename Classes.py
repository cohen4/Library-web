
#import pymysql as mdb
#from flask import Flask, request, render_template, redirect, session
from Functions import *

class Reader:
    def __init__(self, email, password, first_name, last_name, date, phone, city, street, house):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.date = date
        self.phone = phone
        self.city = city
        self.street = street
        self.house = house

    def add_reader(self):  #Insert data about new reader that signed up to the website to the DB
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        query = """INSERT INTO reader VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');""" % (self.email, self.password,
                self.first_name, self.last_name, self.date, self.phone, self.city, self.street, self.house)
        cursor.execute(query)
        con.commit()
        cursor.close()
        con.close()

    def checking_reader_existance(self):      #Check if the user type is a reader by compering the input email with the
                                              #emails in reader database
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("SELECT Email FROM reader ")
        readers_emails = cursor.fetchall()
        cursor.execute("SELECT Email FROM librarian ")
        librarian_emails = cursor.fetchall()
        cursor.close()
        con.close()
        for (email,) in readers_emails:
            if self.email == email:
                return "already exists"
        for (email,) in librarian_emails:
            if self.email == email:
                return "already exists"
        return "no exists"

class Librarian(Reader):
    def __init__(self,email, password, first_name, last_name, date, phone, city, street, house, branch):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.date = date
        self.phone = phone
        self.city = city
        self.street = street
        self.house = house
        self.branch = branch

    def add_librarian(self):    #Insert data about new librarian that signed up to the website to the DB
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        query = """INSERT INTO librarian VALUES ('%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');""" % (self.email,
            self.password, self.first_name, self.last_name, self.date, self.phone, self.city, self.street, self.house, self.branch)
        cursor.execute(query)
        con.commit()
        cursor.close()
        con.close()


class Books:
    def __init__(self, serial_no_book, book_name, author_name, rel_date, publisher, total_quantity):
        self.serial_no_book = serial_no_book
        self.book_name = book_name
        self.author_name = author_name
        self.rel_date = rel_date
        self.publisher = publisher
        self.total_quantity = total_quantity

    def add_new_book(self):     ##Insert data about new book to the DB
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        query1 = """INSERT INTO book(Serial_Number_Book,Book_Name,Author_Name,Release_Date,Publisher,Total_Quantity)
         VALUES ('%s', "%s", '%s','%s', '%s', '%s');""" % (self.serial_no_book, self.book_name, self.author_name,
                                                          self.rel_date, self.publisher, 1)
        cursor.execute(query1)
        con.commit()
        cursor.close()
        con.close()


class Check_Book:

    def __init__(self, serial_no_book):
        self.serial_no_book = serial_no_book

    def checking_book_exist(self):     #Check if the same book already exists in "book" database by checking if the unique
                                       #serial number exists in DB
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("SELECT Serial_Number_Book FROM book; ")
        numbers = cursor.fetchall()
        cursor.close()
        con.close()
        for (number,) in numbers:
            if int(self.serial_no_book) == number:
                return "book already exists in DB"
        return "book does not exist in DB"

    def add_quantity(self):         #update quantity of a book in "book" database if already exists
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        query1 = """UPDATE book
                      SET Total_Quantity=Total_Quantity+1
                      WHERE Serial_Number_Book = '%s';""" % self.serial_no_book
        cursor.execute(query1)
        con.commit()
        cursor.close()
        con.close()


    def extract_book_info(self):  #Extract all data about a requested book from "book" DB
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("""SELECT * FROM book WHERE Serial_Number_Book= '%s' ;""" % self.serial_no_book)
        all_data_about_book = cursor.fetchall()
        con.commit()
        cursor.close()
        con.close()
        return all_data_about_book

    def available_books(self, member_mail):         #Extract an available copy of a requested book for the reader to borrow if exists
        email = session["email"]
        member_mail = member_mail
        branch_name= find_branch(email)
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("""SELECT order_book.Serial_Number_Book_Copy
                            FROM order_book JOIN books_exist_in_branch
                            ON order_book.Serial_Number_Book_Copy = books_exist_in_branch.Serial_Number_Book_Copy
                            JOIN book_copy
                            ON order_book.Serial_Number_Book_Copy = book_copy.Serial_Number_Book_Copy
                            WHERE Email = "%s" AND book_copy.Serial_Number_Book = "%s" 
                            AND books_exist_in_branch.Branch_Name = "%s" AND book_copy.Book_Status = "ordered"
                            AND order_book.Start_Collection_Date <= "%s" and order_book.Final_Collection_Date <= "%s" ;"""
                                % (member_mail, self.serial_no_book, branch_name, today_dt(),
                                                                                final_order_collection_date(today_dt())))
        ordered_copy = cursor.fetchall()
        if len(ordered_copy) > 0:
            for (copy,) in ordered_copy:
                return copy
        else:
            cursor.execute("""SELECT distinct(books_exist_in_branch.Serial_Number_Book_Copy)
                        ,book_copy.Serial_Number_Book
                        FROM books_exist_in_branch,book_copy
                        WHERE books_exist_in_branch.Serial_Number_Book_Copy=book_copy.Serial_Number_Book_Copy
                        AND book_copy.Serial_Number_Book='%s' AND Book_Status="Available"
                        AND Branch_Name='%s';"""
                        %(self.serial_no_book,branch_name))
            list_of_available_books_in_branch = cursor.fetchall()
            if len(list_of_available_books_in_branch) == 0:
                return None
            else:
                for (copy,book) in list_of_available_books_in_branch:
                    return copy


class Book_Copy():
    def __init__(self, status, serial_no_book1):
        self.status = status
        self.serial_no_book = serial_no_book1

    def add_book_copy(self):   #Insert the data about a new copy of a book to the DB
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        query3 = """INSERT INTO book_copy(Book_Status,Serial_Number_Book) VALUES ('%s','%s');""" % (self.status,
                                                                                               self.serial_no_book)
        cursor.execute(query3)
        con.commit()
        cursor.close()
        con.close()


class Exist_In_Branch():
    def __init__(self, branch_name , serial_no_book_copy):
        self.branch_name = branch_name
        self.serial_no_book_copy = serial_no_book_copy

    def add_book_to_branch(self):    #Insert data about new book copy to the branch where the librarian works
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        query4 = """INSERT INTO books_exist_in_branch VALUES ('%s', '%s');""" % (
        self.branch_name, self.serial_no_book_copy)
        cursor.execute(query4)
        con.commit()
        cursor.close()
        con.close()

    def quantity_of_copies_in_branch(self, serial_no_book):    #return quantity of a requested book in branch

        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("""SELECT COUNT(book_copy.Serial_Number_Book)
                        FROM books_exist_in_branch JOIN book_copy
                        ON books_exist_in_branch.Serial_Number_Book_Copy = book_copy.Serial_Number_Book_Copy
                        WHERE Branch_name = '%s' AND book_copy.Serial_Number_Book = '%s';""" % (self.branch_name, serial_no_book))
        number_of_copies = cursor.fetchall()
        for (quantity,) in number_of_copies:
            return quantity

    def count_number_of_available_books_in_branch(self, serial_number_book): #return quantity of the available
                                                                             #copies of a certain book in branch
        con = mdb.connect(host="xxxx", user="xxxx",passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("""SELECT count(book_copy.Serial_Number_Book_Copy) From book_copy inner join
                            books_exist_in_branch on book_copy.Serial_Number_Book_Copy=
                            books_exist_in_branch.Serial_Number_Book_Copy
                            WHERE book_copy.Serial_Number_Book='%s' and Book_Status="Available" and branch_name='%s';"""
                       % (serial_number_book, self.branch_name))
        count = cursor.fetchone()
        con.commit()
        cursor.close()
        con.close()
        return count[0]


class Login(Reader):
    def __init__(self, email, password=0):
        self.email = email
        self.password = password

    def checking_user_existance(self):     #Check if the email that the user entered to the website exists in DB
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("SELECT Email, Password FROM reader ")
        readers_login = cursor.fetchall()
        cursor.execute("SELECT Email, Password FROM librarian ")
        librarians_login = cursor.fetchall()
        cursor.close()
        con.close()
        for reader_login in readers_login:
            if self.email == reader_login[0] and self.password == reader_login[1]:
                return "reader_login"
        for librarian_login in librarians_login:
            if self.email == librarian_login[0] and self.password == librarian_login[1]:
                return "librarian_login"
        return "no exists"

    def checking_user_kind(self):     #Check if the email belongs to a reader or a librarian
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("SELECT Email FROM reader ")
        readers_emails = cursor.fetchall()
        cursor.execute("SELECT Email FROM librarian ")
        librarians_emails = cursor.fetchall()
        cursor.close()
        con.close()
        for (reader_email,) in readers_emails:
            if self.email == reader_email:
                return "reader_login"
        for (librarian_email,) in librarians_emails:
            if self.email == librarian_email:
                return "librarian_login"
        return "no exists"

    def checking_reader_existance(self):
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("SELECT Email FROM reader ")
        readers_emails = cursor.fetchall()
        cursor.close()
        con.close()
        for (reader_email,) in readers_emails:
            if self.email == reader_email:
                return "reader exists"
        return "not exists"

    def fetch_name(self):    #return the name of the user by compering his email with the reader and librarian date
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        if self.checking_user_kind() == "reader_login":
            cursor.execute("""SELECT First_Name FROM reader WHERE Email='%s'""" % self.email)
            reader_name = cursor.fetchone()[0]
            return reader_name
        else:
            cursor.execute("""SELECT First_Name FROM librarian WHERE Email='%s'""" % self.email)
            librarian_name = cursor.fetchone()[0]
            return librarian_name


class Search():
    def __init__(self, search_input):
        self.search_input = search_input

    def search_book(self, input_search_kind):
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        find_partial_name = "%" + self.search_input + "%"
        if input_search_kind == "book_name": #Search by book name
            cursor.execute("""SELECT Serial_Number_Book , Book_Name, Author_Name, Release_Date, Publisher FROM book
                            WHERE Book_Name LIKE "%s"  ;""" % find_partial_name)
        if input_search_kind == "author": #Search by author
            cursor.execute("""SELECT Serial_Number_Book , Book_Name, Author_Name, Release_Date, Publisher FROM book
                                       WHERE Author_Name LIKE "%s" ;""" % find_partial_name)
        search_founds = cursor.fetchall()
        con.commit()
        cursor.close()
        con.close()
        if len(search_founds) > 0:  # Check if there is results
            books_found = []
            for book in search_founds:
                convert_tuple_to_list = list(book)
                add_to_books_found = books_found.append(convert_tuple_to_list)
            return books_found
        else:
            return "not found"
    def find_branches_hold_book(self, books_found):
        i = 0
        for book in books_found:
            con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
            # get the cursor object
            cursor = con.cursor()
            cursor.execute("xxxx;")
            query = ("""SELECT DISTINCT Branch_Name
                        FROM books_exist_in_branch JOIN book_copy
                        ON books_exist_in_branch.Serial_Number_Book_Copy = book_copy.Serial_Number_Book_Copy
                        WHERE Serial_Number_Book ='%s';""" % book[0]) #Gives the branches that hold the relevant books
            cursor.execute(query)
            branches_hold_book = cursor.fetchall()
            con.commit()
            cursor.close()
            con.close()
            branches_list = []
            for (branch,) in branches_hold_book:
                branches_list.append(branch) #Append the branches to empthy list
            books_found[i].append(branches_list) #Append to each book the branches list that hold it.
            i += 1

        return books_found

    def quantity_in_each_branch(self, branches_hold_books_found):
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        i = 0 #Each number represents a book that may be matching for the search input
        for branches in branches_hold_books_found: #Run on each book in the list
            quantity_for_each_branch = []
            for branch in branches[5]: #Run on the branches that holds the book and Check the quantity of avialable books in each branch.
                cursor.execute("""SELECT COUNT(book_copy.Serial_Number_Book)
                FROM book_copy JOIN books_exist_in_branch ON book_copy.Serial_Number_Book_Copy = books_exist_in_branch.Serial_Number_Book_Copy
                 WHERE Book_Status = 'Available' AND Branch_Name = '%s' AND book_copy.Serial_Number_Book = '%s';""" % (branch, branches[0]))
                # in the index 0 there is the serial number book
                # IN index 5 there is the list of the branches that holds the books
                # ALL the books in the list has the same indexes
                number_of_copies = cursor.fetchall()
                for (quantity,) in number_of_copies:
                    quantity_for_each_branch.append(quantity)
            branches_hold_books_found[i].append(quantity_for_each_branch) #Append to each book the avialable quantity in each branch
            i += 1
        return branches_hold_books_found

    def find_branch_phone(self, names_of_branches):
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        i = 0
        for branches in names_of_branches:
            phone_numbers = []
            for branch in branches[5]:
                cursor.execute("""SELECT Phone_Number FROM branch WHERE Branch_Name = '%s';""" % branch)
                branch_phone = cursor.fetchall()
                for (phone,) in branch_phone:
                    phone_numbers.append(phone)
            names_of_branches[i].append(phone_numbers) #Append to each book the phones number of each branch that holds it
            i += 1
        return names_of_branches

class Order_Book:
    def __init__(self, serial_number_book, branch_name, email):
        self.serial_number_book = serial_number_book
        self.branch_name = branch_name
        self.email = email
        self.ordering_date = today_dt()

    def try_to_order(self):  #Check if all the copies of a certain book in branch is borrowed by other readers and
                             # therefore can be ordered
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("""Select book_copy.Serial_Number_Book, book_copy.Serial_Number_Book_Copy, Book_Name, Author_Name, Release_Date,
                Publisher, Book_Status, Branch_Name, Borrow_End_Date
                FROM book_copy Join books_exist_in_branch
                ON book_copy.Serial_Number_Book_Copy = books_exist_in_branch.Serial_Number_Book_Copy
                Join borrow_book On  book_copy.Serial_Number_Book_Copy = borrow_book.Serial_Number_Book_Copy
                Join book on book_copy.Serial_Number_Book = book.Serial_Number_Book
                WHERE book_copy.Serial_Number_Book = '%s' AND Branch_Name = '%s' AND Book_Status = "borrowed"
                ORDER BY Borrow_End_Date ASC LIMIT 1 ;""" % (self.serial_number_book,self.branch_name))
        book_order = cursor.fetchall()
        if len(book_order) == 0 :
            return "high demand"
        else:
            for order in book_order:
                final_collection_date = final_order_collection_date(order[-1]) #The book will wait to the reader for three days
                cursor.execute("""INSERT INTO order_book VALUES ('%s', '%s','%s', '%s', '%s');""" % (
                                    self.email, order[1],order[-1], final_collection_date, self.ordering_date))
                con.commit()
                cursor.execute("""UPDATE book_copy SET Book_Status = 'ordered'
                WHERE Serial_Number_Book_Copy = '%s'; """ % order[1])
                con.commit()
                cursor.close()
                con.close()
                return order


class Borrowed_Book():
    def __init__(self,serial_number_borrowed_copy,borrow_start_date,borrow_end_date,email):
        self.serial_number_borrowed_copy = serial_number_borrowed_copy
        self.borrow_start_date = borrow_start_date
        self.borrow_end_date = borrow_end_date
        self.email = email

    def update_status(self):  #after the reader borrows the book copy,the method updated the status of the certain copy in DB
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("""UPDATE book_copy SET Book_Status="borrowed" WHERE Serial_Number_Book_Copy='%s';"""
                       % self.serial_number_borrowed_copy)
        con.commit()
        cursor.close()
        con.close()

    def add_borrow_book(self):  #Insert data about borrowed copy to the "borrow book" DB
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("""INSERT INTO borrow_book VALUES
                      ('%s', '%s','%s','%s','%s');"""
                      % (self.serial_number_borrowed_copy,"0001-01-01",self.borrow_start_date, self.borrow_end_date, self.email))
        con.commit()
        cursor.close()
        con.close()

