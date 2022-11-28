-- creates a trigger which executes the restock() function
-- each time any book in the Book relation has its stock updated
CREATE OR REPLACE TRIGGER lowStock
AFTER UPDATE OF stock ON Book 
FOR EACH ROW
EXECUTE PROCEDURE restock();
