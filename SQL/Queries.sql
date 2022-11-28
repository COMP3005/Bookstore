-- Note that the queries below will likely not match the queries seen in the code
-- This is because our code uses variables to execute the queries
-- In this file we have changed the variables to some reaonable mock values

-- INSERT OPERATIONS

    INSERT INTO Users VALUES ('user1', 'John', 'Doe', '123 abc road', '123 abc road');

    INSERT INTO Book VALUES (123, 'A Book Title', 500, 100, 0.05, 750, 1);

    INSERT INTO Book_Genre VALUES (123, 'Fiction');
    
    INSERT INTO Publisher VALUES (1, 123456, 'n.h@gmail.com', '123-456-7890', '456 def road');
    
    INSERT INTO Author VALUES (1, 'JK', 'Rowling');
    
    INSERT INTO Has_In_Cart VALUES (123, 'user1', 3);
    
    INSERT INTO Orders VALUES (1, 2022-11-28, 2022-12-16, 2022-12-14, 'Order confirmed', 'user1', '123 abc road', '123 abc road');
    
    INSERT INTO Contains VALUES (123,1,3);    

-- UPDATE OPERATIONS
    
    -- The stock of the book specified by the ISBN is updated based on the number of that particular book sold.
    -- The stock dropping below 10 is separately handled by trigger functions which are explained in Trigger.sql and Functions.sql.
    UPDATE Book
    SET stock = 11
    WHERE isbn = 123;

-- DELETE OPERATIONS

    -- The 4 operations below are used together to remove a book from the database altogether
    -- A book should only be removed if it has yet to be ordered
    DELETE FROM Has_In_Cart WHERE isbn=123;

    DELETE FROM Author_Of WHERE isbn=123;

    DELETE FROM Book_Genre WHERE isbn=123;

    DELETE FROM Book WHERE isbn=123;
    
    --Once the user specified by the uid places an order, all items in their cart are deleted
    DELETE FROM Has_In_Cart WHERE uid='user1';

-- SELECT OPERATIONS

    -- Selects the full name of users based on a UID
    -- Used to tell the user who they have logged in as
    SELECT fName, lName FROM Users WHERE uid = 'user1';

    -- Selects all data for the book matching the given ISBN
    SELECT * FROM Book WHERE isbn=123;
    
    -- Selects all data for the publisher matching the given pubID
    SELECT * FROM Publisher where pubID=1;
    
    -- Selects all data for the author matching the given authorID
    SELECT * FROM Author where authorID=1;
    
    -- From the new table, calculate the total revenue by summing each value of the revenue column
    -- This produces the total revenue over the past length of time specified
    SELECT ROUND(SUM(revenue), 2) AS totalRevenue FROM (
        -- Join Orders, Contains and Book to get information about the revenue of each book sold
        -- Calculated using each row (tuple) in Contains and Book by taking into account quantity, price and royalty
        -- The result for each row is outputted in a new column titled revenue
        -- Orders column is joined to check the date of the sale
        SELECT (quantity * price * (1 - royalty)) AS revenue FROM Orders, Contains, Book
        WHERE Contains.isbn = Book.isbn AND Orders.oNumber = Contains.oNumber AND Orders.rDate > CURRENT_DATE - 30
    ) AS Revenues;
    
    -- From the new table, calculate the total expenditure by summing each value of the expenditure column
    -- This produces the total variable expenditure over the past length of time specified
    -- Note that expenditure in the program also includes a fixed daily expenditure of $100
    SELECT SUM(expenditure) AS totalExpenditure FROM (
        -- Calculates the expenditure of each purchase of books from the publisher
        -- The result for each row is stored in a column named expenditure
        SELECT (quantity * purchasePrice) AS expenditure FROM Purchases
        WHERE Purchases.pDate > CURRENT_DATE - 30
    ) AS Expenditures;
    
    SELECT genre, SUM(quantity) AS totalQuantity, ROUND(SUM(revenue), 2) AS totalRevenue FROM (
    SELECT *, (quantity * price * (1 - royalty)) AS revenue FROM Orders, Contains, Book, Book_Genre
    WHERE Contains.isbn = Book.isbn AND Book_Genre.isbn = Book.isbn AND Orders.oNumber = Contains.oNumber AND Orders.rDate > CURRENT_DATE - 30
    ) AS ByGenre
    GROUP BY genre;
    
    SELECT ByAuthor.authorID, SUM(quantity) AS totalQuantity, ROUND(SUM(revenue), 2) AS totalRevenue FROM (
    SELECT *, (quantity * price * (1 - royalty)) AS revenue FROM Orders, Contains, Book, Author_Of
    WHERE Contains.isbn = Book.isbn AND Author_Of.isbn = Book.isbn AND Orders.oNumber = Contains.oNumber AND Orders.rDate > CURRENT_DATE - 30
    ) AS ByAuthor
    GROUP BY authorID;
    
    -- Selects all data for the cart matching the given uid
    SELECT * FROM Has_In_Cart WHERE uid='user1';
    
    -- Selects all data for all the orders that are placed by the user matching the given uid
    SELECT * FROM Orders WHERE uid='user1';
    
    -- Selects all data of an order specified by the order number that are placed by the user matching the given uid
    SELECT * FROM Orders WHERE uid='user1' AND oNumber=1;
    
    -- Selects all data for all the books in the database
    SELECT * FROM Book;
    
    -- Selects all data for all the books that are of the specified genre after doing a natural join using ISBN
    SELECT * FROM Book_Genre, Book
    WHERE Book_Genre.isbn = Book.isbn AND Book_Genre.genre='Fiction';
    
    -- Selects all data for all the books whose titles are an approximate match to the name specified
    -- Approximate match means that the search term is contained anywhere in the title
    SELECT * FROM Book
    WHERE name LIKE '%A Book Title%';
    
    
    
