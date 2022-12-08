	CREATE TABLE IF NOT EXISTS Publisher (
            pubID INT PRIMARY KEY,
            bankAcct INT NOT NULL,
            email VARCHAR(50) NOT NULL,
            phone CHAR(12),
            address VARCHAR(80)
        );
        CREATE TABLE IF NOT EXISTS Book (
            isbn INT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            price NUMERIC(5,2) NOT NULL,
            stock INT NOT NULL CHECK(stock >= 0),
            royalty NUMERIC(3,2) NOT NULL CHECK(royalty > 0 AND royalty <= 0.1),
            numPages INT NOT NULL,
            publisher INT,
            FOREIGN KEY(publisher) REFERENCES Publisher(pubID) 
        );
        CREATE TABLE IF NOT EXISTS Book_Genre (
            isbn INT,
            genre VARCHAR(20),
            PRIMARY KEY(isbn, genre),
            FOREIGN KEY(isbn) REFERENCES Book(isbn)
        );
        CREATE TABLE IF NOT EXISTS Users (
            uid VARCHAR(30) PRIMARY KEY,
            fName VARCHAR(30) NOT NULL,
            lName VARCHAR(30) NOT NULL,
            billing VARCHAR(80),
            shipping VARCHAR(80)
        );
        CREATE TABLE IF NOT EXISTS Author (
            authorID INT PRIMARY KEY,
            fName VARCHAR(30) NOT NULL,
            lName VARCHAR(30) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Author_Of (
            authorID INT,
            isbn INT,
            PRIMARY KEY(authorID, isbn),
            FOREIGN KEY(authorID) REFERENCES Author(authorID),
            FOREIGN KEY(isbn) REFERENCES Book(isbn)
        );
        CREATE TABLE IF NOT EXISTS Has_In_Cart (
            isbn INT,
            uid VARCHAR(30),
            PRIMARY KEY(isbn, uid),
            quantity INT NOT NULL CHECK(quantity > 0),
            FOREIGN KEY(uid) REFERENCES Users(uid),
            FOREIGN KEY(isbn) REFERENCES Book(isbn)
        );
        CREATE TABLE IF NOT EXISTS Orders (
            oNumber INT PRIMARY KEY,
            rDate DATE NOT NULL,
            eShipDate DATE NOT NULL,
            aShipDate DATE,
            status VARCHAR(20),
            uid VARCHAR(30),
            shippingAddress VARCHAR(80),
            billingAddress VARCHAR(80),
            FOREIGN KEY(uid) REFERENCES Users(uid)
        );
        CREATE TABLE IF NOT EXISTS Contains (
            isbn INT,
            oNumber INT,
            PRIMARY KEY(isbn, oNumber),
            quantity INT NOT NULL CHECK(quantity > 0),
            FOREIGN KEY(oNumber) REFERENCES Orders(oNumber),
            FOREIGN KEY(isbn) REFERENCES Book(isbn)
        );
	CREATE TABLE IF NOT EXISTS Purchases (
            pNum INT PRIMARY KEY,
            pDate Date NOT NULL,
            isbn INT NOT NULL,
            quantity INT NOT NULL CHECK(quantity > 0),
            purchasePrice NUMERIC(5,2) NOT NULL
        );
