# Library-web
An academic team project that includes Python,SQL, CSS, and HTML.
For the code to run, you have to fill in the "connect to the database" lines.
it looks like:
#connect to the database
con = mdb.connect(host = "xxxx", user = "xxxx", passwd= "xxxx")
#get the cursor object
cursor = con.cursor()
cursor.execute("xxxx;")

Some functions that the project includes are:
1. Sign in (as a librarian or member).
2. Login (as a librarian or member)
3. Searching for a book
4. Adding a copy or book (if you are a librarian)
5. Borrow a book.
6. Making a future order for the book
7. Showing a list of history's borrowings and orders

The most SQL code you can see is in functions and classes in Python files.
In the template folder, there is HTML code, and in the static folder, there is CSS code.
