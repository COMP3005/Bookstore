-- creates a function that is used to automatically generate a new purchase number
-- this function queries the Purchases table for the current highest purchase number 
-- then returns this value +1 as a new purchase number to be used
CREATE OR REPLACE FUNCTION nextPurchaseNum()
returns INT
language plpgsql
AS 
$$
DECLARE
    selected_pNum Purchases.pNum%type;
BEGIN
    -- find the highest purchase number in Purchases 
    -- and store it in the variable selected_pNum
    SELECT pNum FROM Purchases 
    INTO selected_pNum
    ORDER BY pNum DESC 
    LIMIT 1;
    
    -- if an existing purchase number is found
    -- generate new purchase number by adding 1
    IF FOUND
    THEN 
        RETURN selected_pNum + 1;
    
    -- if there is no purchase number found (this is the first purchase)
    -- assign a purchase number of 1
    ELSE
        RETURN 1;
    END IF;
    RETURN NULL;
END;
$$

-- creates a function that restocks books if the stock falls under 10
-- this function is called by the "lowStock" trigger
CREATE OR REPLACE FUNCTION restock()
returns TRIGGER
language plpgsql
AS 
$$
BEGIN
    -- check if the stock of the updated book has fallen below 10
    IF NEW.stock < 10
    THEN 
        -- replenish the stock by the amount of this book ordered within the last month
        UPDATE Book
        SET stock = NEW.stock + (
            SELECT sum(quantity) FROM Contains, Orders
            WHERE Contains.oNumber = Orders.oNumber AND Contains.isbn = NEW.isbn AND Orders.rDate > CURRENT_DATE - 30
        )
        WHERE Book.isbn = NEW.isbn;
        
        -- order the amount of stock replenished from the publisher and store order information
        INSERT INTO Purchases VALUES (nextPurchaseNum(), CURRENT_DATE, NEW.isbn, (
            SELECT sum(quantity) FROM Contains, Orders
            WHERE Contains.oNumber = Orders.oNumber AND Contains.isbn = NEW.isbn AND Orders.rDate > CURRENT_DATE - 30
        ), NEW.price * 0.01 * (
            -- the price at which books are purchased from the publisher is 75-90% of the sale price
            -- this percentage is randomly generated and used to calculate the purchase price
            SELECT floor(random() * 16 + 75)
        ));
    END IF;
    RETURN NULL;
END;
$$
