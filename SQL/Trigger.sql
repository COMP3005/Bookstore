        CREATE OR REPLACE TRIGGER lowStock
        AFTER UPDATE OF stock ON Book 
        FOR EACH ROW
        EXECUTE PROCEDURE restock()