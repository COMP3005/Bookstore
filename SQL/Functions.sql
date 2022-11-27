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
            END IF;
            RETURN NULL;
        END;
        $$