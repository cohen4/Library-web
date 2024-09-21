This academic team project utilizes Python, SQL, CSS, and HTML. To run the code, you will need to complete the "connect to the database" section, which looks like this:
Connect to the database
con = mdb.connect(host="xxxx", user="xxxx", passwd="xxxx")
get the cursor object
cursor = con.cursor()
cursor.execute("xxxx;")

Key functionalities of the project include:
  1.Sign in as a librarian or member.
  2.Log in as a librarian or member.
  3.Search for a book.
  4.Add a copy of a book (librarians only).
  5.Borrow a book from a specific branch.
  6.Place a future order for a book if it is currently borrowed by another member.
  7.View a history of borrowings and orders (members only).
The majority of the SQL code can be found within the functions and classes in the Python files. The HTML code is located in the template folder, while the CSS code is stored in the static folder.
