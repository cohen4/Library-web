import pymysql as mdb
from datetime import timedelta, date
#from Classes import Login
from flask import Flask, request, render_template, redirect, session


def find_branch(email):  #The function extracts branch name from DB based on input email
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    query = ("""SELECT Branch FROM librarian WHERE Email='%s';""" % email)
    cursor.execute(query)
    branch=cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    for (br,) in branch:
        return br

def find_last_serial_copy():  #The function returns the latest book copy that's in DB
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    cursor.execute("SELECT Serial_Number_Book_Copy FROM book_copy ORDER BY Serial_Number_Book_Copy DESC ")
    all_serial_book_copy = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    for (serial_copy,) in all_serial_book_copy:
        return serial_copy

def extract_borrowed_book_info(book_copy): #The function returns all data about borrowed book from DB based on input id book copy
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    cursor.execute("""SELECT book_copy.Serial_Number_Book_Copy,Book_Name,Author_Name,Borrow_Start_Date
                    ,Borrow_End_Date,email 
                    From book inner join book_copy 
                    ON book.Serial_Number_Book=book_copy.Serial_Number_Book inner 
                    join borrow_book on book_copy.Serial_Number_Book_Copy=borrow_book.Serial_Number_Book_Copy
                    WHERE borrow_book.Serial_Number_Book_Copy='%s' AND Borrow_Start_Date = '%s' ;""" % (book_copy, today_dt()))
    all_data_about_borrowed_book = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return all_data_about_borrowed_book

def reader_borrow_history(member_mail): #The function returns all rows in "borrow book" table in DB based on input mail
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    cursor.execute("""SELECT book_copy.Serial_Number_Book_Copy,Book_Name,Author_Name,Borrow_Start_Date
                            ,Borrow_End_Date,email From book inner join book_copy on 
                            book.Serial_Number_Book=book_copy.Serial_Number_Book inner 
                            join borrow_book on book_copy.Serial_Number_Book_Copy=borrow_book.Serial_Number_Book_Copy
                            WHERE Email='%s'
                            ORDER BY Borrow_Start_Date DESC;""" % member_mail)
    member_borrow_history = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    if len(member_borrow_history) > 0:
        borrows_found = []
        for borrow in member_borrow_history:
            convert_tuple_to_list = list(borrow)
            add_to_borrows_found = borrows_found.append(convert_tuple_to_list)
        return borrows_found
        #Return a list with all tuples of info about borrow history from DB
    else:
        return "zero books borrowed by member"


def count_member_borrowed_books(member_mail): #The function counts how many books the reader borrowed at the moment
                                              #based on his email and a query in DB
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    cursor.execute("""SELECT count(Serial_Number_Book_Copy)
                      From borrow_book
                      WHERE Email='%s' AND Borrow_End_Date >= '%s' ;""" % (member_mail, today_dt()))
    count = cursor.fetchone()[0]
    return count


def extend_rent_date(sn_book_copy, member_mail, start_date):
    # The function returns and updates borrow end date in DB based on reader's borrow book data
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    cursor.execute("""SELECT Borrow_End_Date 
                    FROM borrow_book 
                    WHERE Serial_Number_Book_Copy='%s' and Email='%s' and Borrow_Start_Date='%s' """ %
                    (sn_book_copy, member_mail, start_date))
    rent_end_date = cursor.fetchone()[0]
    con.commit()
    extended_rent_date = rent_end_date + timedelta(days=7)
    cursor.execute("""UPDATE borrow_book SET Borrow_End_Date='%s' WHERE Serial_Number_Book_Copy='%s' and
                        Email='%s' and Borrow_Start_Date='%s'"""
                   % (extended_rent_date, sn_book_copy, member_mail, start_date))
    con.commit()
    cursor.execute("""SELECT Borrow_End_Date 
            FROM borrow_book 
            WHERE Serial_Number_Book_Copy='%s' AND Email='%s' and Borrow_Start_Date='%s' ;""" % (sn_book_copy, member_mail, start_date))
    extend_date = cursor.fetchone()[0]
    con.commit()
    cursor.close()
    return extend_date

def update_borrow_extension_request_date(sn_book_copy,member_mail,start_date,extend_request_date):
    #When a reader extends his borrow of a certain copy, the function updates his borrow extension request date to be current date
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    cursor.execute("""UPDATE borrow_book SET Borrow_Extend_Request_Date='%s' WHERE Serial_Number_Book_Copy='%s' and
                            Email='%s' and Borrow_Start_Date='%s'"""
                   % (extend_request_date, sn_book_copy, member_mail, start_date))
    con.commit()
    cursor.close()


def check_if_book_is_ordered(sn_book_copy):  #Check in DB if the requested copy is in status "ordered" or "borrowed"
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    cursor.execute("""SELECT Book_Status FROM book_copy WHERE Serial_Number_Book_Copy='%s'""" % sn_book_copy)
    if cursor.fetchone()[0] == "borrowed":
        return False
    return True


def daily_borrow_update(): #Function that updates status for all of copies in branches to "available" if their borrow is over
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    today_date=date.today()
    cursor.execute("""SELECT borrow_book.Serial_Number_Book_Copy
                    FROM borrow_book JOIN book_copy
                    ON borrow_book.Serial_Number_Book_Copy = book_copy.Serial_Number_Book_Copy
                    WHERE book_copy.Book_Status = "borrowed" 
                    GROUP BY Serial_Number_Book_Copy
                    HAVING MAX(Borrow_End_Date) < '%s';""" % today_date)
    copies=cursor.fetchall()
    con.commit()
    for (copy,) in copies:
        cursor.execute("""UPDATE book_copy
                        SET Book_Status="available"
                        WHERE Serial_Number_Book_Copy='%s';""" % copy)
        con.commit()


def daily_order_update(): #Function that updates status for all of copies in branches to "available" if their order is over
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    today_date= date.today()
    cursor.execute("""SELECT order_book.Serial_Number_Book_Copy
                    FROM order_book JOIN book_copy
                    ON order_book.Serial_Number_Book_Copy = book_copy.Serial_Number_Book_Copy
                    WHERE book_copy.Book_Status = "ordered"
                    GROUP BY Serial_Number_Book_Copy
                    HAVING MAX(Final_Collection_Date) < '%s';""" % today_date)
    copies=cursor.fetchall()
    con.commit()
    for (copy,) in copies:
        cursor.execute("""UPDATE book_copy
                        SET Book_Status="available"
                        WHERE Serial_Number_Book_Copy='%s';""" % copy)
        con.commit()


def check_if_reader_search(): #Check if input email is in reader DB and returns an answer about it
    if session.get("email"):
        email = session.get("email")
        con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
        # get the cursor object
        cursor = con.cursor()
        cursor.execute("xxxx;")
        cursor.execute("SELECT Email FROM reader ")
        readers_emails = cursor.fetchall()
        cursor.close()
        con.close()
        for (reader_email,) in readers_emails:
            if email == reader_email:
                return "reader exists"
        return "not exists"
    else:
        return "not exists"

def make_ordered_books_list(reader_email): #Extract all data about a reader's order history from DB
    today_date = date.today()
    con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
    # get the cursor object
    cursor = con.cursor()
    cursor.execute("xxxx;")
    cursor.execute("""SELECT Book_Name, Start_Collection_Date, Final_Collection_Date, Branch_Name
                    from order_book join book_copy on order_book.Serial_Number_Book_Copy = book_copy.Serial_Number_Book_Copy
                    JOIN book on book_copy.Serial_Number_Book = book.Serial_Number_Book
                    Join books_exist_in_branch ON order_book.Serial_Number_Book_Copy = books_exist_in_branch.Serial_Number_Book_Copy
                    WHERE Email = '%s' and Start_Collection_Date <= '%s' and Final_Collection_Date >= '%s';"""
                        % (reader_email, today_date, today_date))
    wait_for_you = cursor.fetchall()
    cursor.execute("""SELECT Book_Name, Start_Collection_Date, Branch_Name
                FROM order_book JOIN book_copy ON order_book.Serial_Number_Book_Copy = book_copy.Serial_Number_Book_Copy
                JOIN book ON book_copy.Serial_Number_Book = book.Serial_Number_Book
                JOIN books_exist_in_branch ON order_book.Serial_Number_Book_Copy = books_exist_in_branch.Serial_Number_Book_Copy
                WHERE Email = '%s' and Start_Collection_Date > '%s';""" % (reader_email, today_date))
    still_not_return = cursor.fetchall()
    return [wait_for_you, still_not_return]


def today_dt(): #Returns today date
    date_0 = date.today()
    return date_0


def rent_default_date(): #Return a date that is 14 days later than current date
    next_14 = date.today() + timedelta(days=14)
    return next_14

def final_order_collection_date(borrow_end_date): #Returns a date that is 3 days later than current date
    next_3 = borrow_end_date + timedelta(days=3)
    return next_3

