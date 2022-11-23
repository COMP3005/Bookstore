import psycopg2
import random
from datetime import date, timedelta

# connect to database
# note that Bookstore database will need to be created in Postgres and the password will need to be changed to your master password
# make a note for the TAs that they do not enter too long values for INT types
conn = psycopg2.connect("dbname=Bookstore user=postgres password=password")

def initialize():
    #all initial ddl and dml statements to create the database
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
        CREATE FUNCTION restock()
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
            END IF;
            RETURN NULL;
        END;
        $$
        """,
        """
        CREATE TRIGGER lowStock
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

    # display options menu 
    if (username == "admin"):
        print("Successfully signed in as Admin!")
        selection = adminMenu()
        while (selection != "0"):
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
            elif (selection == "2"):
                print("Removing book")
                deleteISBN = input("Enter the isbn of the book you want to remove: ")
                print("**************************************************************************************************************")
                deleteBook(deleteISBN) 
            elif (selection == "3"):
                print("Adding authors")
                authInfo = input("Please enter the following author information: authorID,firstName,lastName\n")
                authList = authInfo.split(",")
                addAuthor(authList)
                print("**************************************************************************************************************")   
            #View reports option
            elif (selection == "4"):
                reportNumber, timeRange = adminSearchMenu()
                if (reportNumber == "1"):
                    salesExpenditureReport(timeRange)
                elif (reportNumber == "2"):
                    genreReport(timeRange)
                elif (reportNumber == "3"):
                    authorReport(timeRange)

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
        selection = normalMenu()
        while (selection != "0"):
            #TODO: search books by feature
            if (selection == "1"):
                print("Searching")
            #Add books to cart
            if (selection == "2"):
                isbn = input("Please enter the isbn of the books you want to order from the list above in comma separated format: isbn1,isbn2... \n") #assuming everything is entered in the correct format
                quantity = input("Please enter the quantity of the books you want to order in the order of the isbns you entered: quantity1,quantity2... \n") #assuming everything is entered in the correct format
                print("**************************************************************************************************************") 
                isbnList = isbn.split(",")
                quantityList = quantity.split(",")
                addToCart(username,isbnList,quantityList)
            #Display Cart
            elif (selection == "3"):  
                print("**************************************************************************************************************")  
                displayCart(username)
            #Check Out / Place Order
            elif (selection == "4"):  
                print("**************************************************************************************************************")  
                placeOrder(username)
            #Track Order
            elif (selection == "5"):
                print("**************************************************************************************************************") 
                displayOrders(username)
            elif (selection == "6"):
                oNum = input("Please enter the order number of the order you want to view: ")
                print("**************************************************************************************************************") 
                viewOrder(oNum,username)    

            selection = normalMenu()
            if (selection == "0"):
                print("Logging out...")
                break
    
    return 0

#Login and Authentication
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
    #check if publisher exists
    if (findPublisher(attributeList[6])) is None:
        addPublisher(attributeList[6])
            
    #adding books to the bookstore database
    if (findBook(attributeList[0])) is None:
        insert = "INSERT INTO Book VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor = conn.cursor()
        cursor.execute(insert, (attributeList[0], attributeList[1], attributeList[2], attributeList[3], attributeList[4], attributeList[5], attributeList[6]))
        #TODO: add records to the authorOf and genres tables
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

    for i in range(len(genreList)):
        insert = "INSERT INTO Book_Genre VALUES (%s, %s)"
        cursor.execute(insert, (isbn, genreList[i]))

    cursor.close()
    conn.commit()

def deleteBook(deleteISBN):
    if (findBook(deleteISBN)) is None:
        print("No book with such ISBN exists, check the ISBN again")
        
    else:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Book WHERE isbn=%s", (deleteISBN,)) 
        #TODO: need to delete book from genres, authorOf, and all user carts
        print("The book with ISBN " + deleteISBN + " was successfully deleted")
        print("**************************************************************************************************************")
        cursor.close()
        conn.commit()
        
def addPublisher(pubID):
    #check if publisher exists
    print("Adding publisher")
    attributes = input("Enter the publisher details in the following format: bankAcct,email,phone,address \n") #assuming everything is entered in the correct format
    attributeList = attributes.split(",")
        
    #adding publisher to the bookstore database
    insert = "INSERT INTO Publisher VALUES (%s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    #cursor.execute(insert, (int(attributeList[0]), attributeList[1], float(attributeList[2]), int(attributeList[3]), float(attributeList[4]), int(attributeList[5]), int(attributeList[6])))
    cursor.execute(insert, (pubID, attributeList[0], attributeList[1], attributeList[2], attributeList[3]))
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
    if (author is None):
        insertAuthor = "INSERT INTO Author VALUES (%s, %s, %s)"
        cursor.execute(insertAuthor, (authList[0], authList[1], authList[2])) 
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

def salesExpenditureReport(timeRange):
    return

def genreReport(timeRange):
    query = """
        SELECT genre, SUM(quantity) AS totalQuantity, SUM(revenue) AS totalRevenue FROM (
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
        print("Genre: {} | Num Books Sold: {} | Total Revenue: {} | Average Revenue per Book: {}".format(genreInfo[0], genreInfo[1], genreInfo[2], genreInfo[2] / genreInfo[1])) 
    print("**************************************************************************************************************") 

    cursor.close()

def authorReport(timeRange):
    query = """
        SELECT ByAuthor.authorID, SUM(quantity) AS totalQuantity, SUM(revenue) AS totalRevenue FROM (
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
        print("Author ID: {} | Num Books Sold: {} | Total Revenue: {} | Average Revenue per Book: {}".format(authorInfo[0], authorInfo[1], authorInfo[2], authorInfo[2] / authorInfo[1])) 
    print("**************************************************************************************************************") 

    cursor.close()

#User functions
def normalMenu():
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

def addToCart(username,isbnList,quantityList):
    #assuming correct isbn that exists in the database has been entered. ---- error checking?
    #assuming the same user will not order the same book again.
    cursor = conn.cursor()
    for i in range (len(isbnList)):
        book = findBook(isbnList[i])
        if (book[3] < int(quantityList[i])):
            print("Sorry, there are only " + str(book[3]) + "of the following book in stock - " + book[1] +"  with isbn: " + str(book[0]))
        else:    
            insert = "INSERT INTO Has_In_Cart VALUES (%s, %s, %s)"
            cursor.execute(insert, (isbnList[i], username, quantityList[i]))
       
    cursor.close()
    conn.commit() 

def displayCart(username):
    cursor = conn.cursor()
    selectQuery = "SELECT * FROM Has_In_Cart WHERE uid=%s"
    cursor.execute(selectQuery, (username,))
    cartRecords = cursor.fetchall()
    if (len(cartRecords)):
        print("Your cart currently looks like: ")
        for i in cartRecords:
            print("ISBN: {} | Quantity: {}".format(i[0], i[2])) 
        print("**********************************************************************************************")
    cursor.close()
    conn.commit()

def placeOrder(username):
    oNum = assignOrderNumber()

    #assuming actual ship date is before expected ship date
    receiveDate = date.today()
    actualTemp = receiveDate + timedelta(days=30)
    aShipDate = receiveDate + (actualTemp - receiveDate) *random.random()
    expectedTemp = aShipDate + timedelta(days=10)
    eShipDate = aShipDate + (expectedTemp - aShipDate) *random.random()
    status = "Order confirmed" #come back to this if time permits

    cursor = conn.cursor()
    selectQuery = "SELECT * FROM Has_In_Cart WHERE uid=%s"
    cursor.execute(selectQuery, (username,))
    cart = cursor.fetchall()

    insert = "INSERT INTO Orders VALUES (%s, %s, %s, %s, %s, %s)"
    insertContains = "INSERT INTO Contains VALUES (%s, %s, %s)"
    updateBook = """UPDATE Book
                    SET stock = %s
                    WHERE isbn = %s"""

    if (cart is None):
        print("Cannot place order - no items in your cart")
    else:
        cursor.execute(insert, (oNum, receiveDate, eShipDate, aShipDate, status, username))
        for item in cart:
            book = findBook(item[0])
            newStock = book[3]-item[2]
            cursor.execute(insertContains, (item[0], oNum, item[2]))
            cursor.execute(updateBook, (newStock, item[0]))

        #if the user orders then this should clear their cart
        cursor.execute("DELETE FROM Has_In_Cart WHERE uid=%s", (username,)) 

    cursor.close()
    conn.commit() 

def displayOrders(username):
    cursor = conn.cursor()
    selectQuery = "SELECT * FROM Orders WHERE uid=%s"
    cursor.execute(selectQuery, (username,))
    orderRecords = cursor.fetchall()
    if (len(orderRecords) == 0):
        print("You currently have no active orders") 
    else:  
        print("Here are all your active orders:")     
        for i in orderRecords:
            print("oNum: {} | Received Date: {} | Expected Ship Date: {} | Actual Ship Date: {} | Status: {}".format(i[0], i[1], i[2], i[3], i[4])) 
        print("**********************************************************************************************")
    cursor.close()

def viewOrder(oNum,username):   
    cursor = conn.cursor()
    selectQuery = "SELECT * FROM Orders WHERE uid=%s AND oNumber=%s"
    cursor.execute(selectQuery, (username,oNum))
    order = cursor.fetchone()
    if order is None:
        print("You do not have an order with the order number you entered, please try again.")
    else:
        print("oNum: {} | Received Date: {} | Expected Ship Date: {} | Actual Ship Date: {} | Status: {}".format(order[0], order[1], order[2], order[3], order[4])) 
        print("**********************************************************************************************")
        printOrderDetails(oNum)   

#TODO: Add search filters
def searchBooks(): 
    cursor = conn.cursor()
    selectQuery = "SELECT * FROM Book"
    cursor.execute(selectQuery)
    bookRecords = cursor.fetchall()
    for i in bookRecords:
        print("**********************************************************************************************")
        print("ISBN: {} | Name: {} | Price: {} | Stock: {} | NumPages: {} | Publisher: {}".format(i[0], i[1], i[2], i[3], i[5], i[6])) 
        print("**********************************************************************************************")

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
    
    # if a publisher exists, then we return all the attributes of that publisher, otherwise return None.
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
