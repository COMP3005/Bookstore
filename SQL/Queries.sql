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
    
    INSERT INTO Orders VALUES (1, '2022-11-28', '2022-12-16', '2022-12-14', 'Order confirmed', 'user1', '123 abc road', '123 abc road');
    
    INSERT INTO Contains VALUES (123,1,3);    
    
    INSERT INTO Author_Of VALUES (1, 123);

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
    -- Also used by the user to search for books by ISBN
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
    
    -- From the new table, calculate the total number of books sold by summing each value in the quantity column
    -- From the new table, calculate the total revenue by summing each value of the revenue column
    -- We group these two values by genre in order to get this information per genre
    SELECT genre, SUM(quantity) AS totalQuantity, ROUND(SUM(revenue), 2) AS totalRevenue FROM (
        -- Join Orders, Contains, Book and Book_Genre to get information about the revenue of each book sold
        -- Calculated using each row (tuple) in Contains and Book by taking into account quantity, price and royalty
        -- The result for each row is outputted in a new column titled revenue
        -- Orders column is joined to check the date of the sale
        -- Book_Genre is joined to include the genres to group by later
        SELECT *, (quantity * price * (1 - royalty)) AS revenue FROM Orders, Contains, Book, Book_Genre
        WHERE Contains.isbn = Book.isbn AND Book_Genre.isbn = Book.isbn AND Orders.oNumber = Contains.oNumber AND Orders.rDate > CURRENT_DATE - 30
    ) AS ByGenre
    GROUP BY genre;
    
    -- From the new table, calculate the total number of books sold by summing each value in the quantity column
    -- From the new table, calculate the total revenue by summing each value of the revenue column
    -- We group these two values by author ID in order to get this information per author
    SELECT ByAuthor.authorID, SUM(quantity) AS totalQuantity, ROUND(SUM(revenue), 2) AS totalRevenue FROM (
        -- Join Orders, Contains, Book and Author_Of to get information about the revenue of each book sold
        -- Calculated using each row (tuple) in Contains and Book by taking into account quantity, price and royalty
        -- The result for each row is outputted in a new column titled revenue
        -- Orders column is joined to check the date of the sale
        -- Author_Of is joined to include the author IDs to group by later
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
    
    -- Select all books from the new table where the author's full name matches the search term
    SELECT * FROM (
        -- Join Book, Author and Author_Of to combine book and author information
        -- Also adds a new column containing the author's full name
        SELECT *, fName || ' ' || lName AS fullName FROM Book, Author_of, Author
        WHERE Book.isbn = Author_Of.isbn AND Author_Of.authorID = Author.authorID
    ) AS AuthorInfo                                     
    WHERE fullName = 'JK Rowling';
    
    -- Selects all books that cost less than or equal to the amount provided
    SELECT * FROM Book
    WHERE price <= 600;
    
    -- Selects the current largest order number from the Orders table
    -- Used to assign order numbers for new orders
    SELECT oNumber FROM Orders 
    ORDER BY oNumber DESC 
    LIMIT 1;
    
    -- Select all rows in Contains that belong to the given order number
    -- Used to gather the details of a specific order to print to the user
    SELECT * FROM Contains WHERE oNumber=1
