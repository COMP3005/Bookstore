import psycopg2
import random
from datetime import date, timedelta

# connect to database
# note that Bookstore database will need to be created in Postgres and the password will need to be changed to your master password
# make a note for the TAs that they do not enter too long values for INT types
conn = psycopg2.connect("dbname=Bookstore user=postgres password=nazeeha")

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
    username = input("Enter your username: ")
    while (not usernameValid(username)):
        print("****************************************")
        print("Invalid Username - Please try again or use \"new\" to create a new account")
        username = input("Enter your username: ")
    if (username == "admin"):
        password = input("Password: ")
        print("****************************************")
        while (not (password == "4dmin!")):
            print("Invalid password - Please try again")
            password = input("Password: ")
            print("****************************************")
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
            print("****************************************")

        #insert the new user into the database 
        insert = "INSERT INTO Users VALUES (%s, %s, %s, %s, %s)"
        cursor = conn.cursor()
        cursor.execute(insert, (uName, fName, lName, billing, shipping))
        cursor.close()
        conn.commit()

        print("New user added successfully!")
        print("****************************************")
        username = uName

    # display options menu 
    #note for Evan - we want to keep displaying menu until logout
    if (username == "admin"):
        print("Successfully signed in as Admin!")
        selection = adminMenu()
        if (selection == "0"):
            print("Logging out...")
            exit()
        elif (selection == "1"):
            print("Adding book")
            attributes = input("Enter the book details in the following format: isbn,name,price,stock,royalty,numPages,publisherID \n") #assuming everything is entered in the correct format
            attributesList = attributes.split(",")
            addBook(attributesList)
        elif (selection == "2"):
            print("Removing book")
            deleteISBN = input("Enter the isbn of the book you want to remove: isbn\n")
            deleteISBN = str(deleteISBN)
            deleteBook(deleteISBN)   

    else:
        select = "SELECT fName, lName FROM Users WHERE uid = %s"
        cursor = conn.cursor()
        cursor.execute(select, (username,))
        nameTuple = cursor.fetchone()
        fullName = nameTuple[0] + " " + nameTuple[1] 

        print("Successfully signed in as: {}".format(fullName))
        selection = normalMenu()
        if (selection == "0"):
            print("Logging out...")
            exit()
        elif (selection == "2"):
            print("Displaying books...")
            displayBooks()
            isbn = input("Please enter the isbn of the books you want to order from the list above in comma separated format: isbn1,isbn2 \n") #assuming everything is entered in the correct format
            quantity = input("Please enter the quantity of the books you want to order in the order of the isbns you entered: quantity1, quantity2 \n") #assuming everything is entered in the correct format
            isbnList = isbn.split(",")
            quantityList = quantity.split(",")
            addToCart(username,isbnList,quantityList)
        elif (selection == "3"):   
            print("Tracking your orders...")
            #note for Evan - just displaying the orders for this user from order table??
            displayOrder(username)
        cursor.close()
    
    return 0

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


def normalMenu():
    print("0. Log out")
    print("1. Search books")
    print("2. Order Books")
    print("3. Track Orders")
    selection = input("Select an option from the menu: ")
    #error checking
    return selection

def adminMenu():
    print("0. Log out")
    print("1. Add book")
    print("2. Remove book")
    selection = input("Select an option from the menu: ")
    #error checking
    return selection

def addBook(attributeList):
    #check if publisher exists
    if (findPublisher(attributeList[6])) is None:
        addPublisher(attributeList[6])
            
    #adding books to the bookstore database
    if (findBook(attributeList[0])) is None:
        insert = "INSERT INTO Book VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor = conn.cursor()
        cursor.execute(insert, (attributeList[0], attributeList[1], attributeList[2], attributeList[3], attributeList[4], attributeList[5], attributeList[6]))
        print("The following book has been successfully added:")
        selectBook = "select * from Book where isbn=%s"
        cursor.execute(selectBook, (attributeList[0],))
        bookRecords = cursor.fetchall();
        for i in bookRecords:
            print("**************************************************************************************************************")
            print("ISBN:", i[0], "Name: ", i[1], "Price: ", i[2], "Stock: ", i[3], "Royalty: ", i[4], "NumPages: ", i[5], "Publisher: ", i[6]) 
            print("**************************************************************************************************************")
        """"
        authID = input("Please enter the authIDs of this book in comma-separated format: authID1,authID2 \n") #assuming everything is entered in the correct format
        authIDList = authID.split(",")
        addAuthor(attributeList[0],authIDList) 
        """
        cursor.close()
        conn.commit()
        
        
    else:
        print("A book with this ISBN already exists in the database")
        

def deleteBook(deleteISBN):
    if (findBook(deleteISBN)) is None:
        print("No book with such ISBN exists, check the ISBN again")
        
    else:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Book WHERE isbn=%s", (deleteISBN,)) # not deleting the publisher cause that publisher might have other books
        print("The book with ISBN: " + deleteISBN +" has been deleted successfully")
        print("Remaining books in the bookstore:")
        displayBooks()
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
    selectPublisher = "select * from Publisher where pubID=%s"
    cursor.execute(selectPublisher, (pubID,))
    publisherRecords = cursor.fetchall();
    print("The following publisher has been added successfully ...")
    for i in publisherRecords:
        print("**************************************************************************************************************")
        print("PubID:", i[0], "BankAcct: ", i[1], "Email: ", i[2], "Phone: ", i[3], "Address: ", i[4]) 
        print("**************************************************************************************************************")
        
    cursor.close()
    conn.commit()

def addAuthor(isbn,authIDList):  
    cursor = conn.cursor()    
    for i in range(len(authIDList)):
        author = findAuthor(authIDList[i])  
        if (author is None):
            authFName = input("Please enter the first name of this author with authID: " + str(authIDList[i]))
            authLName = input("Please enter the last name of this author with authID: " + str(authIDList[i]))
            print("Inserting into authors table...")
            insertAuthor = "INSERT INTO Author VALUES (%s, %s, %s)"
            cursor.execute(insertAuthor, (authIDList[i], authFName, authLName,))
                
        insert = "INSERT INTO Author_Of VALUES (%s, %s)"
        cursor.execute(insert, (isbn, authIDList[i]))
          

    cursor.close()
    conn.commit()

def displayBooks():
    
    cursor = conn.cursor()
    selectQuery = "select * from Book"
    cursor.execute(selectQuery)
    bookRecords = cursor.fetchall()
    for i in bookRecords:
        print("**********************************************************************************************")
        print("ISBN:", i[0], "Name: ", i[1], "Price: ", i[2], "Stock: ", i[3], "Royalty: ", i[4], "NumPages: ", i[5], "Publisher: ", i[6]) 
        print("**********************************************************************************************")

def addToCart(username,isbnList,quantityList):

    #assuming correct isbn that exists in the database has been entered. ---- error checking?
    #assuming the same user will not order the same book again. isbn and uid are pk in cart
    cursor = conn.cursor()
    for i in range (len(isbnList)):
        book = findBook(isbnList[i])
        if (book[3] < int(quantityList[i])): #Evan: does this have to be a sql func or trigger? what if the user orders 6 books and there are 5 in stock, do we let them take 5? or none at all?
            #should line 337 logic be implemented here or in order "The user can add as many books as they like to the cart?"
            print("Sorry, there are only " + str(book[3]) + "remaining " + book[1] +" book with isbn: " + str(book[0]) + ". So this book could not be added to cart")
        else:    
            insert = "INSERT INTO Has_In_Cart VALUES (%s, %s, %s)"
            cursor.execute(insert, (isbnList[i], username, quantityList[i]))
    
    selectQuery = "select * from Has_In_Cart"
    cursor.execute(selectQuery)
    cartRecords = cursor.fetchall();
    if (len(cartRecords)>0):
        print("Your cart currently looks like: ")
        for i in cartRecords:
            print("**********************************************************************************************")
            print("ISBN: ", i[0], "UID:", i[1], "Quantity: ", i[2]) 
            print("**********************************************************************************************") 

        print("Are you ready to checkout?")
        checkout = input("Please enter Y to proceed to checkout \n") 
        #note for Evan - do we add a feature to go back and modify the cart?
        #only registered users should be able to checkout.... but only registered users are allowed to look at the book store so should this be an extra feature?
        if (checkout=="Y" or checkout =="y"):
            #Note for Evan - doing nth with shipping and billing address?
            #each isbn order has it's own order number even if it's from the same user
            shippingAddress = input("Please enter your shipping address: ")
            billingAddress = input("Please enter your billing address: ")
            for i in cartRecords:
                placeOrder(i[0],i[1],i[2])  
        print("Congratulations, your order has been successfully placed!")           
    cursor.close()
    conn.commit() 
    #do we display the books in book database to show update in stock?  
    return

def placeOrder(isbn,username,quantity):
    oID = ''
    number = [0,1,2,3,4,5,6,7,8,9]
    for i in range(4):
        oID +=str(random.choice(number))

    #assuming actual ship date is before expected ship date
    receiveDate = date.today()
    actualTemp = receiveDate + timedelta(days=30)
    aShipDate = receiveDate + (actualTemp - receiveDate) *random.random()
    expectedTemp = aShipDate + timedelta(days=10)
    eShipDate = aShipDate + (expectedTemp - aShipDate) *random.random()
    status = "Order confirmed" #Evan: do we hard code this?
    insert = "INSERT INTO Orders VALUES (%s, %s, %s, %s, %s, %s)"
    insertContains = "INSERT INTO Contains VALUES (%s, %s, %s)"
    book = findBook(isbn)
    newStock = book[3]-quantity
    #check if this newStock is < threshold value and if it is then automatically place order for more
    updateBook = """UPDATE Book
                    SET stock = %s
                    WHERE isbn = %s"""
    cursor = conn.cursor()
    cursor.execute(insert, (oID, receiveDate, eShipDate, aShipDate, status, username))
    cursor.execute(insertContains, (isbn, oID, quantity))
    cursor.execute(updateBook, (newStock,isbn))
    cursor.close()
    conn.commit()     

def displayOrder(username):
    cursor = conn.cursor()
    selectQuery = "select * from Orders where uid=%s"
    cursor.execute(selectQuery, (username,))
    orderRecords = cursor.fetchall();
    if(len(orderRecords)==0):
        print("You currently have no orders") 
    else:       
        for i in orderRecords:
            print("**********************************************************************************************")
            print("oNum:", i[0], "Receive Date: ", i[1], "eShipDate: ", i[2], "aShipDate: ", i[3], "Status: ", i[4], "UID: ", i[5]) 
            print("**********************************************************************************************")


if __name__ == "__main__":
    initialize()
    main()
