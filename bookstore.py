import psycopg2
import random
from datetime import date, timedelta

# connect to database
# note that Bookstore database will need to be created in Postgres and the password will need to be changed to your master password
# make a note for the TAs that they do not enter too long values for INT types
conn = psycopg2.connect("dbname=Bookstore user=postgres password=WuQinFang-0418")

# Run initial ddl statements to define the database and set up triggers and functions for the database
def initialize():
    commands = [
        """
        CREATE TABLE IF NOT EXISTS Publisher (
            pubID INT PRIMARY KEY,
            bankAcct INT NOT NULL,
            email VARCHAR(50) NOT NULL,
            phone CHAR(12),
            address VARCHAR(80)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Book (
            isbn INT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            price NUMERIC(5,2) NOT NULL,
            stock INT NOT NULL CHECK(stock >= 0),
            royalty NUMERIC(3,2) NOT NULL CHECK(royalty > 0 AND royalty < 1),
            numPages INT NOT NULL,
            publisher INT,
            FOREIGN KEY(publisher) REFERENCES Publisher(pubID) 
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Book_Genre (
            isbn INT,
            genre VARCHAR(20),
            PRIMARY KEY(isbn, genre),
            FOREIGN KEY(isbn) REFERENCES Book(isbn)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Users (
            uid VARCHAR(30) PRIMARY KEY,
            fName VARCHAR(30) NOT NULL,
            lName VARCHAR(30) NOT NULL,
            billing VARCHAR(80),
            shipping VARCHAR(80)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Author (
            authorID INT PRIMARY KEY,
            fName VARCHAR(30) NOT NULL,
            lName VARCHAR(30) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Author_Of (
            authorID INT,
            isbn INT,
            PRIMARY KEY(authorID, isbn),
            FOREIGN KEY(authorID) REFERENCES Author(authorID),
            FOREIGN KEY(isbn) REFERENCES Book(isbn)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Has_In_Cart (
            isbn INT,
            uid VARCHAR(30),
            PRIMARY KEY(isbn, uid),
            quantity INT NOT NULL CHECK(quantity > 0),
            FOREIGN KEY(uid) REFERENCES Users(uid),
            FOREIGN KEY(isbn) REFERENCES Book(isbn)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Orders (
            oNumber INT PRIMARY KEY,
            rDate DATE NOT NULL,
            eShipDate DATE NOT NULL,
            aShipDate DATE,
            status VARCHAR(20),
            uid VARCHAR(30),
            shippingAddress VARCHAR(80) NOT NULL,
            billingAddress VARCHAR(80) NOT NULL,
            FOREIGN KEY(uid) REFERENCES Users(uid)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Contains (
            isbn INT,
            oNumber INT,
            PRIMARY KEY(isbn, oNumber),
            quantity INT NOT NULL CHECK(quantity > 0),
            FOREIGN KEY(oNumber) REFERENCES Orders(oNumber),
            FOREIGN KEY(isbn) REFERENCES Book(isbn)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Purchases (
            pNum INT PRIMARY KEY,
            pDate Date NOT NULL,
            isbn INT NOT NULL,
            quantity INT NOT NULL CHECK(quantity > 0),
            purchasePrice NUMERIC(5,2) NOT NULL,
            FOREIGN KEY(isbn) REFERENCES Book(isbn)
        )
        """,
        """
        CREATE OR REPLACE FUNCTION nextPurchaseNum()
        returns INT
        language plpgsql
        AS 
        $$
        DECLARE
            selected_pNum Purchases.pNum%type;
        BEGIN
            SELECT pNum FROM Purchases 
            INTO selected_pNum
            ORDER BY pNum DESC 
            LIMIT 1;

            IF FOUND
            THEN 
                RETURN selected_pNum + 1;
            ELSE
                RETURN 1;
            END IF;
            RETURN NULL;
        END;
        $$
        """,
        """
        CREATE OR REPLACE FUNCTION restock()
        returns TRIGGER
        language plpgsql
        AS 
        $$
        BEGIN
            IF NEW.stock < 10
            THEN 
                UPDATE Book
                SET stock = NEW.stock + (
                    SELECT sum(quantity) FROM Contains, Orders
                    WHERE Contains.oNumber = Orders.oNumber AND Contains.isbn = NEW.isbn AND Orders.rDate > CURRENT_DATE - 30
                )
                WHERE Book.isbn = NEW.isbn;

                INSERT INTO Purchases VALUES (nextPurchaseNum(), CURRENT_DATE, NEW.isbn, (
                    SELECT sum(quantity) FROM Contains, Orders
                    WHERE Contains.oNumber = Orders.oNumber AND Contains.isbn = NEW.isbn AND Orders.rDate > CURRENT_DATE - 30
                ), NEW.price * 0.01 * (
                    SELECT floor(random() * 16 + 75)
                ));
            END IF;
            RETURN NULL;
        END;
        $$
        """,
        """
        CREATE OR REPLACE TRIGGER lowStock
        AFTER UPDATE OF stock ON Book 
        FOR EACH ROW
        EXECUTE PROCEDURE restock()
        """
    ]
    
    cursor = conn.cursor()
    for command in commands:
        cursor.execute(command)
    cursor.close()
    conn.commit()

def main():
    # authentication
    # will change the system based on whether you are logged in as a user or an admin
    # Admin login info - Username: admin, Password: 4dmin!
    # User login info - Username: any valid username in the database. Use "new" to create a new user
    username = login()

    if (username == "admin"):
        print("Successfully signed in as Admin!")

        selection = adminMenu()
        while (selection != "0"):
            # Admin adds a new book
            if (selection == "1"):
                print("Adding book")
                attributes = input("Enter the book details in the following format: isbn,name,price,stock,royalty,numPages,publisherID \n") #assuming everything is entered in the correct format
                genres = input("Enter the genre(s) of this new book separated by commas: genre1,genre2...\n")
                authors = input("Enter the author id(s) of this new book separated by commas (must be existing authors): authorID1,authorID2...\n") #assuming we only enter author IDs of authors who already exist
                print("**************************************************************************************************************")
                attributesList = attributes.split(",")
                genresList = genres.split(",")
                authorList = authors.split(",")
                addBook(attributesList)
                addGenres(attributesList[0], genresList)
                addAuthorOf(attributesList[0], authorList)
            # Admin removes a book
            elif (selection == "2"):
                print("Removing book")
                deleteISBN = input("Enter the isbn of the book you want to remove: ")
                print("**************************************************************************************************************")
                deleteBook(deleteISBN) 
            # Admin adds new authors
            elif (selection == "3"):
                print("Adding authors")
                authInfo = input("Please enter the following author information: authorID,firstName,lastName\n")
                authList = authInfo.split(",")
                addAuthor(authList)
                print("**************************************************************************************************************")   
            # Admin view reports option
            elif (selection == "4"):
                reportNumber, timeRange = adminSearchMenu()
                if (reportNumber == "1"):
                    revenueExpenditureReport(timeRange)
                elif (reportNumber == "2"):
                    genreReport(timeRange)
                elif (reportNumber == "3"):
                    authorReport(timeRange)

            # Select a new menu option
            selection = adminMenu()  
            if (selection == "0"):
                print("Logging out...\n")
                break

    else:
        select = "SELECT fName, lName FROM Users WHERE uid = %s"
        cursor = conn.cursor()
        cursor.execute(select, (username,))
        nameTuple = cursor.fetchone()
        fullName = nameTuple[0] + " " + nameTuple[1] 
        cursor.close()

        print("Successfully signed in as: {}".format(fullName))
        selection = userMenu()
        while (selection != "0"):
            # User searches books by filters
            if (selection == "1"):
                print("Searching")
                search,filter = userSearchMenu()
                # The corresponding search function is called 
                if (search == "1"):
                    searchByGenre(filter)
                elif (search == "6"):
                    searchBooks()  
                elif (search == "2"):
                    searchByTitle(filter)
                elif (search == "3"):
                    searchByISBN(filter)
                elif (search == "4"):
                    searchByAuthor(filter)
                elif (search == "5"):
                    searchByMaxPrice(filter) 
                    
            # User adds books to cart
            if (selection == "2"):
                isbn = input("Please enter the isbn of the books you want to order from the list above in comma separated format: isbn1,isbn2... \n") #assuming everything is entered in the correct format
                quantity = input("Please enter the quantity of the books you want to order in the order of the isbns you entered: quantity1,quantity2... \n") #assuming everything is entered in the correct format
                print("**************************************************************************************************************") 
                isbnList = isbn.split(",")
                quantityList = quantity.split(",")
                addToCart(username,isbnList,quantityList)
            # User views their cart
            elif (selection == "3"):  
                print("**************************************************************************************************************")  
                displayCart(username)
            # User checks out / places an order
            elif (selection == "4"):
                shippingAddress = input("Please enter your shipping address: ")  
                billingAddress = input("Please enter your billing address: ")  
                print("**************************************************************************************************************")  
                placeOrder(username, shippingAddress, billingAddress)
            # User tracks their orders
            elif (selection == "5"):
                print("**************************************************************************************************************") 
                displayOrders(username)
            # User checks details of a specific order    
            elif (selection == "6"):
                oNum = input("Please enter the order number of the order you want to view: ")
                print("**************************************************************************************************************") 
                viewOrder(oNum,username)    
            # Select a new menu option
            selection = userMenu()
            if (selection == "0"):
                print("Logging out...")
                break
    return 0

# Login and Authentication
def login():
    username = input("Enter your username: ")
    while (not usernameValid(username)):
        print("**************************************************************************************************************")
        print("Invalid Username - Please try again or use \"new\" to create a new account")
        username = input("Enter your username: ")
    if (username == "admin"):
        password = input("Password: ")
        print("**************************************************************************************************************")
        while (not (password == "4dmin!")):
            print("Invalid password - Please try again")
            password = input("Password: ")
            print("**************************************************************************************************************")
    elif (username == "new"):
        print("Creating new account:")
        # assume user's input will not exceed the length value set for these attributes in our relation
        fName = input("Enter first name: ")
        lName = input("Enter last name: ")
        billing = input("Enter billing address: ")
        shipping = input("Enter shipping address: ")

        # allow the user to select a unique username
        uName = input("Enter your new username: ")
        while (usernameValid(uName)):
            print("Username taken - Please try again")
            uName = input("Enter your new username: ")
            print("**************************************************************************************************************")

        #insert the new user into the database 
        insert = "INSERT INTO Users VALUES (%s, %s, %s, %s, %s)"
        cursor = conn.cursor()
        cursor.execute(insert, (uName, fName, lName, billing, shipping))
        cursor.close()
        conn.commit()

        print("New user added successfully!")
        print("**************************************************************************************************************")
        username = uName
    
    return username

# Checks if username is either "admin", "new", or an existing uid in the Users relation
def usernameValid(username):
    select = "SELECT * FROM Users WHERE uid = %s"
    cursor = conn.cursor()
    cursor.execute(select, (username,))
    # "admin" and "new" are considered valid usernames even though they are not in the DB
    if (username == "admin" or username == "new"):
        cursor.close()
        return True
    
    # if the username (id) exists in the database, return true
    elif (cursor.rowcount == 1):
        cursor.close()
        return True
    
    # if the username (id) doesn't exist in the database, return false
    cursor.close()
    return False

#Admin functions
def adminMenu():
    print("0. Log out")
    print("1. Add book")
    print("2. Remove book")
    print("3. Add author")
    print("4. View Reports")
    selection = input("Select an option from the menu: ")
    print("**************************************************************************************************************")
    #error checking
    return selection

def adminSearchMenu():
    print("1. Sales vs Expenditures")
    print("2. Sales per Genre")
    print("3. Sales per Author")
    option = input("Select an option from the menu: ")
    timeRange = input("Please specify the number of days from today which the report should include: ")
    print("**************************************************************************************************************")
    #error checking
    return option, int(timeRange)

def addBook(attributeList):
    # check if publisher exists
    if (findPublisher(attributeList[6])) is None:
        addPublisher(attributeList[6])
            
    # adding books to the bookstore database
    if (findBook(attributeList[0])) is None:
        insert = "INSERT INTO Book VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor = conn.cursor()
        cursor.execute(insert, (attributeList[0], attributeList[1], attributeList[2], attributeList[3], attributeList[4], attributeList[5], attributeList[6]))
        selectBook = "SELECT * FROM Book WHERE isbn=%s"
        cursor.execute(selectBook, (attributeList[0],))
        bookRecords = cursor.fetchone()

        print("The following book has been successfully added:")
        print("ISBN: {} | Name: {} | Price: {} | Stock: {} | Royalty: {} | NumPages: {} | Publisher: {}".format(bookRecords[0], bookRecords[1], bookRecords[2], bookRecords[3], bookRecords[4], bookRecords[5], bookRecords[6])) 
        print("**************************************************************************************************************")

        cursor.close()
        conn.commit()
           
    else:
        print("A book with this ISBN already exists in the database")

def addGenres(isbn, genreList):
    cursor = conn.cursor()

    # Add genres of the book specified by the ISBN
    for i in range(len(genreList)):
        insert = "INSERT INTO Book_Genre VALUES (%s, %s)"
        cursor.execute(insert, (isbn, genreList[i]))

    cursor.close()
    conn.commit()

def deleteBook(deleteISBN):
    # Assume that the admin does not delete a book that has already been ordered by a user
    if (findBook(deleteISBN)) is None:
        print("No book with such ISBN exists, check the ISBN again")
        
    # Deleting a book from the bookstore also means that the book has to be deleted from a user's cart and from the Author_Of and Book_Genre relation   
    else:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Has_In_Cart WHERE isbn=%s", (deleteISBN,))
        cursor.execute("DELETE FROM Author_Of WHERE isbn=%s", (deleteISBN,))
        cursor.execute("DELETE FROM Book_Genre WHERE isbn=%s", (deleteISBN,))
        cursor.execute("DELETE FROM Book WHERE isbn=%s", (deleteISBN,)) 
        print("The book with ISBN " + deleteISBN + " was successfully deleted")
        print("**************************************************************************************************************")
        cursor.close()
        conn.commit()
        
def addPublisher(pubID):
    # check if publisher exists
    print("Adding publisher")
    attributes = input("Enter the publisher details in the following format: bankAcct,email,phone,address \n") #assuming everything is entered in the correct format
    attributeList = attributes.split(",")
        
    # adding publisher to the bookstore database
    insert = "INSERT INTO Publisher VALUES (%s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(insert, (pubID, attributeList[0], attributeList[1], attributeList[2], attributeList[3]))

    # get information of the publisher that was just added
    selectPublisher = "SELECT * FROM Publisher where pubID=%s"
    cursor.execute(selectPublisher, (pubID,))
    publisherRecords = cursor.fetchone()

    print("The following publisher has been successfully added:") 
    print("PubID: {} | BankAcct: {} | Email: {} | Phone: {} | Address {}".format(publisherRecords[0], publisherRecords[1], publisherRecords[2], publisherRecords[3], publisherRecords[4])) 
    print("**************************************************************************************************************")
        
    cursor.close()
    conn.commit()

def addAuthor(authList):  
    cursor = conn.cursor()    
    author = findAuthor(authList[0])  

    # Add a new author to the database if the author does not already exist
    if (author is None):
        insertAuthor = "INSERT INTO Author VALUES (%s, %s, %s)"
        cursor.execute(insertAuthor, (authList[0], authList[1], authList[2])) 

        # Get the information of the author that was just added
        selectAuthor = "SELECT * FROM Author where authorID=%s"
        cursor.execute(selectAuthor, (authList[0],))
        authorRecords = cursor.fetchone()

        print("The following author has been successfully added:") 
        print("AuthorID: {} | First Name: {} | Last Name: {}".format(authorRecords[0], authorRecords[1], authorRecords[2]))
        print("**************************************************************************************************************")
    else:
        print("The author you are trying to add already exists")  

    cursor.close()
    conn.commit()

def revenueExpenditureReport(timeRange):
    revenueQuery = """
        SELECT ROUND(SUM(revenue), 2) AS totalRevenue FROM (
            SELECT (quantity * price * (1 - royalty)) AS revenue FROM Orders, Contains, Book
            WHERE Contains.isbn = Book.isbn AND Orders.oNumber = Contains.oNumber AND Orders.rDate > CURRENT_DATE - %s
        ) AS Revenues
    """
    expenditureQuery = """
        SELECT SUM(expenditure) AS totalExpenditure FROM (
            SELECT (quantity * purchasePrice) AS expenditure FROM Purchases
            WHERE Purchases.pDate > CURRENT_DATE - %s
        ) AS Expenditures
    """

    cursor = conn.cursor()
    cursor.execute(revenueQuery, (timeRange,))
    revenue = cursor.fetchone()[0]
    cursor.execute(expenditureQuery, (timeRange,))
    expenditure = cursor.fetchone()[0] + (100 * timeRange) #We assume that the bookstore has a daily fixed operations cost of $100

    print("Revenue vs Expenditure Report:")
    print("Revenue in the last {} days: ${} | Expenditure in the last {} days: ${}".format(timeRange, revenue, timeRange, expenditure))
    print("**************************************************************************************************************") 

    cursor.close()

def genreReport(timeRange):

    # Get information on sales per genre within a given time period denoted by the timeRange, e.g. 30 days
    query = """
        SELECT genre, SUM(quantity) AS totalQuantity, ROUND(SUM(revenue), 2) AS totalRevenue FROM (
            SELECT *, (quantity * price * (1 - royalty)) AS revenue FROM Orders, Contains, Book, Book_Genre
            WHERE Contains.isbn = Book.isbn AND Book_Genre.isbn = Book.isbn AND Orders.oNumber = Contains.oNumber AND Orders.rDate > CURRENT_DATE - %s
        ) AS ByGenre
        GROUP BY genre
    """

    cursor = conn.cursor()
    cursor.execute(query, (timeRange,))
    report = cursor.fetchall()
    
    print("Sales by Genre Report:")
    for genreInfo in report:
        print("Genre: {} | Num Books Sold: {} | Total Revenue: ${} | Average Revenue per Book: ${}".format(genreInfo[0], genreInfo[1], genreInfo[2], round(genreInfo[2] / genreInfo[1], 2))) 
    print("**************************************************************************************************************") 

    cursor.close()

def authorReport(timeRange):
    # Get information on sales per author within a given time period denoted by the timeRange, e.g. 30 days
    query = """
        SELECT ByAuthor.authorID, SUM(quantity) AS totalQuantity, ROUND(SUM(revenue), 2) AS totalRevenue FROM (
            SELECT *, (quantity * price * (1 - royalty)) AS revenue FROM Orders, Contains, Book, Author_Of
            WHERE Contains.isbn = Book.isbn AND Author_Of.isbn = Book.isbn AND Orders.oNumber = Contains.oNumber AND Orders.rDate > CURRENT_DATE - %s
        ) AS ByAuthor
        GROUP BY authorID
    """

    cursor = conn.cursor()
    cursor.execute(query, (timeRange,))
    report = cursor.fetchall()
    
    print("Sales by Author Report:")
    for authorInfo in report:
        print("Author ID: {} | Num Books Sold: {} | Total Revenue: ${} | Average Revenue per Book: ${}".format(authorInfo[0], authorInfo[1], authorInfo[2], round(authorInfo[2] / authorInfo[1], 2))) 
    print("**************************************************************************************************************") 

    cursor.close()

#User functions
def userMenu():
    print("0. Log out")
    print("1. Search books")
    print("2. Add Books to Cart")
    print("3. Display Cart")
    print("4. Check Out")
    print("5. Track Orders")
    print("6. View Order Details")
    selection = input("Select an option from the menu: ")
    #error checking
    return selection

def userSearchMenu():
    print("1. Search by book genre")
    print("2. Search by book title")
    print("3. Search by book ISBN")
    print("4. Search by author name (Enter full name)")
    print("5. Search by maximum price")
    print("6. Search all books (no filter)")
    option = input("Select an option from the menu: ")
    if not (option == "6"):
        filter = input("Enter search value: ")
        if (option == "2"):
            filter = "%" + filter + "%"
    else:
        filter = ""
    print("**************************************************************************************************************")
    return option, filter

def addToCart(username,isbnList,quantityList):
    # Assuming correct isbn that exists in the database has been entered.
    # Assuming the same user will not order the same book again.
    cursor = conn.cursor()

    # Add books specified by the ISBN to the user's cart if there are enough in the stock.
    # Otherwise, don't let the user add any books to their cart.
    for i in range (len(isbnList)):
        book = findBook(isbnList[i])
        if (book[3] < int(quantityList[i])):
            print("Sorry, there are only " + str(book[3]) + " of the following book in stock - " + book[1] +"  with isbn: " + str(book[0]))
        else:    
            insert = "INSERT INTO Has_In_Cart VALUES (%s, %s, %s)"
            cursor.execute(insert, (isbnList[i], username, quantityList[i]))
       
    cursor.close()
    conn.commit() 

def displayCart(username):
    cursor = conn.cursor()

    # Get the cart details of the user specified by username
    selectQuery = "SELECT * FROM Has_In_Cart WHERE uid=%s"
    cursor.execute(selectQuery, (username,))
    cartRecords = cursor.fetchall()

    if (len(cartRecords)):
        print("Your cart currently looks like: ")
        for i in cartRecords:
            print("ISBN: {} | Quantity: {}".format(i[0], i[2])) 
        print("**************************************************************************************************************")
    cursor.close()
    conn.commit()

def placeOrder(username, shippingAddress, billingAddress):
    oNum = assignOrderNumber()

    # get the current date and use it as the receive date
    receiveDate = date.today() 
    # Actual ship date is generated randomly based on current date and has to be within 30 days of the receive date. 
    # Actual ship date is greater than current date.
    actualTemp = receiveDate + timedelta(days=30) 
    aShipDate = receiveDate + (actualTemp - receiveDate) *random.random()
    # Expected ship date is generated randomly based on actual ship date and has to be within 10 days of the actual ship date. 
    # Expected ship date is greater than current date. 
    # Assuming actual ship date is before expected ship date.
    expectedTemp = aShipDate + timedelta(days=10)
    eShipDate = aShipDate + (expectedTemp - aShipDate) *random.random()
    status = "Order confirmed" 

    cursor = conn.cursor()
    selectQuery = "SELECT * FROM Has_In_Cart WHERE uid=%s"
    cursor.execute(selectQuery, (username,))
    cart = cursor.fetchall()

    # Order everything that is present in the user's cart.
    insert = "INSERT INTO Orders VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    insertContains = "INSERT INTO Contains VALUES (%s, %s, %s)"
    updateBook = """UPDATE Book
                    SET stock = %s
                    WHERE isbn = %s"""

    if (cart is None):
        print("Cannot place order - no items in your cart")

    # Update the stock based on the quantities ordered by the user of that particular book    
    else:
        cursor.execute(insert, (oNum, receiveDate, eShipDate, aShipDate, status, username, shippingAddress, billingAddress))
        for item in cart:
            book = findBook(item[0])
            newStock = book[3]-item[2]
            cursor.execute(insertContains, (item[0], oNum, item[2]))
            cursor.execute(updateBook, (newStock, item[0]))

        # The cart is cleared once the user places an order
        cursor.execute("DELETE FROM Has_In_Cart WHERE uid=%s", (username,)) 

    cursor.close()
    conn.commit() 

def displayOrders(username):
    cursor = conn.cursor()
    selectQuery = "SELECT * FROM Orders WHERE uid=%s"
    cursor.execute(selectQuery, (username,))
    orderRecords = cursor.fetchall()

    # Get the details of all orders placed by the user specified by username
    if (len(orderRecords) == 0):
        print("You currently have no active orders") 
    else:  
        print("Here are all your active orders:")     
        for i in orderRecords:
            print("oNum: {} | Received Date: {} | Expected Ship Date: {} | Actual Ship Date: {} | Status: {} | Shipping Address: {}".format(i[0], i[1], i[2], i[3], i[4], i[6])) 
        print("**************************************************************************************************************")
    cursor.close()

def viewOrder(oNum,username):   
    cursor = conn.cursor()
    selectQuery = "SELECT * FROM Orders WHERE uid=%s AND oNumber=%s"
    cursor.execute(selectQuery, (username,oNum))
    order = cursor.fetchone()
    
    # Get the details of a specific order for the user specified by username
    if order is None:
        print("You do not have an order with the order number you entered, please try again.")
    else:
        print("oNum: {} | Received Date: {} | Expected Ship Date: {} | Actual Ship Date: {} | Status: {} | Shipping Address: {}".format(order[0], order[1], order[2], order[3], order[4], order[6])) 
        print("**************************************************************************************************************")
        printOrderDetails(oNum)   

def searchBooks(): 
    cursor = conn.cursor()
    # Search books by no filters
    selectQuery = "SELECT * FROM Book"
    cursor.execute(selectQuery)
    bookRecords = cursor.fetchall()
    cursor.close()

    for i in bookRecords:
        print("ISBN: {} | Name: {} | Price: {} | Stock: {} | NumPages: {}".format(i[0], i[1], i[2], i[3], i[5])) 
    print("**************************************************************************************************************")
    
def searchByGenre(filter):
    cursor = conn.cursor()
    # Search books by genre
    selectQuery = """SELECT * FROM Book_Genre, Book
                   WHERE Book_Genre.isbn = Book.isbn AND Book_Genre.genre=%s"""
    cursor.execute(selectQuery, (filter,))
    bookRecords = cursor.fetchall()
    cursor.close()

    for i in bookRecords:
        print("ISBN: {} | Name: {} | Price: {} | Stock: {} | NumPages: {}".format(i[2], i[3], i[4], i[5], i[7])) 
    print("**************************************************************************************************************")

def searchByTitle(filter):
    cursor = conn.cursor()
    # Search books by book title
    # BONUS FEATURE:  approximate search for books, (will find any books that contains the filter in their title)
    selectQuery = """SELECT * FROM Book
                   WHERE name LIKE %s"""
    cursor.execute(selectQuery, (filter,))
    bookRecords = cursor.fetchall()
    cursor.close()

    for i in bookRecords:
        print("ISBN: {} | Name: {} | Price: {} | Stock: {} | NumPages: {}".format(i[0], i[1], i[2], i[3], i[5])) 
    print("**************************************************************************************************************") 

def searchByISBN(filter):
    cursor = conn.cursor()
    # Search books by book ISBN
    selectQuery = """SELECT * FROM Book
                   WHERE ISBN =  %s"""
    cursor.execute(selectQuery, (filter,))
    bookRecords = cursor.fetchall()
    cursor.close()

    for i in bookRecords:
        print("ISBN: {} | Name: {} | Price: {} | Stock: {} | NumPages: {}".format(i[0], i[1], i[2], i[3], i[5])) 
    print("**************************************************************************************************************") 

def searchByAuthor(filter):
    cursor = conn.cursor()
    # Search books by author's full name
    selectQuery = """SELECT * FROM (
                        SELECT *, fName || ' ' || lName AS fullName FROM Book, Author_of, Author
                        WHERE Book.isbn = Author_Of.isbn AND Author_Of.authorID = Author.authorID
                    ) AS AuthorInfo                                     
                   WHERE fullName =  %s"""
    cursor.execute(selectQuery, (filter,))
    bookRecords = cursor.fetchall()
    cursor.close()

    for i in bookRecords:
        print("ISBN: {} | Name: {} | Price: {} | Stock: {} | NumPages: {}".format(i[0], i[1], i[2], i[3], i[5])) 
    print("**************************************************************************************************************")  

def searchByMaxPrice(filter):
    cursor = conn.cursor()
    # Search for books less than or equal to the price provided
    selectQuery = """SELECT * FROM Book
                   WHERE price <=  %s"""
    cursor.execute(selectQuery, (filter,))
    bookRecords = cursor.fetchall()
    cursor.close()

    for i in bookRecords:
        print("ISBN: {} | Name: {} | Price: {} | Stock: {} | NumPages: {}".format(i[0], i[1], i[2], i[3], i[5])) 
    print("**************************************************************************************************************") 

#Helper functions
def findPublisher(pubID):
    pub = None
    select = "SELECT * FROM Publisher WHERE pubID = %s"
    cursor = conn.cursor()
    cursor.execute(select, (pubID,))
    
    # if a publisher exists, then we return all the attributes of that publisher, otherwise return None.
    if (cursor.rowcount == 1):
        pub = cursor.fetchone()

    cursor.close()
    return pub

def findAuthor(authID):
    auth = None
    select = "SELECT * FROM Author WHERE authorid = %s"
    cursor = conn.cursor()
    cursor.execute(select, (authID,))
    
    # if an author exists, then we return all the attributes of that author, otherwise return None.
    if (cursor.rowcount == 1):
        auth = cursor.fetchone()

    cursor.close()
    return auth    

def findBook(isbn):
    book = None
    select = "SELECT * FROM Book WHERE isbn = %s"
    cursor = conn.cursor()
    cursor.execute(select, (isbn,))
    
    # if a book exists, then we return all the attributes of that book, otherwise return None.
    if (cursor.rowcount == 1):
        book = cursor.fetchone()

    cursor.close()
    return book  

def addAuthorOf(isbn, authorList):
    cursor = conn.cursor() 
    for i in range(len(authorList)):
        insert = "INSERT INTO Author_Of VALUES (%s, %s)"
        cursor.execute(insert, (authorList[i], isbn))
    cursor.close()
    conn.commit()    

def assignOrderNumber():
    cursor = conn.cursor()
    # get the highest order number that exists in the database
    select = """SELECT oNumber FROM Orders 
                ORDER BY oNumber DESC 
                LIMIT 1"""
    cursor.execute(select)
    result = cursor.fetchone()
    cursor.close()

    #if there are no rows in the table, assign order number 1
    if (result is None):
        return 1
    #otherwise, add 1 to the highest order number and assign as the new order number
    else:
        return result[0] + 1    

def printOrderDetails(oNum):
    cursor = conn.cursor()
    selectQuery = "SELECT * FROM Contains WHERE oNumber=%s"
    cursor.execute(selectQuery, (oNum))
    orderRecords = cursor.fetchall() 
    for i in range(len(orderRecords)):
        book = findBook(orderRecords[i][0])
        print("ISBN: {} | Title: {} | Quantity: {}".format(book[0], book[1], orderRecords[i][1]))   
    print("**********************************************************************************************")               

if __name__ == "__main__":
    initialize()
    main()
