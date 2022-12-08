# Bookstore README
A COMP3005 project by Nazeeha Harun (101139836) and Evan Li (101188718)

**Overview:**<br />
This project is intended to simulate the basic features of a Bookstore database through a Python command line interface. We have used the "psycopg2" library to connect Python to PostgreSQL and execute queries from within our program. 

**SQL files:**<br />
These files have been included per the assignment requirements. However, the files are not used in the program in any way as we have opted to call SQL queries from within the code. Thus, the SQL files submitted will be copies of the queries which can be found in our code.

**Running the code:**<br />
In order to run the code, you will need a Python 3.10 interpreter and a PGAdmin account. Additionally, you will need to have the "psycopg2" library installed on your device - this can be done by using "pip3 install psycopg2" in your command line. **You will also need to update the password on line 9 in bookstore.py** to reflect your own PGAdmin master password.<br /><br />
Please note that you will need to manually create the "Bookstore" database in PostgreSQL prior to running this program. Additionally, the initialization function provides ONLY DDL STATEMENTS, so **you must use the program to add data to the tables**.<br /><br />
Upon verifying that you have met all the above requirements, the code can be run in the terminal using "python bookstore.py". You will be asked to "log in" to the system as either an admin or an existing user, or create a new user as specified below. <br />
- To log in as admin, you need the username "admin" and password "4dmin!".<br />
- To create a new user (and add them to the Users relation), type "new" as the username then follow the prompts for creating a new user. You need to follow this step the first time you run the program and want to log in as a regular customer because the Users relation does not have any uid to begin with. Once you create a new user, it will be added to the Users relation.
- For any subsequent log in as a regular user, you can enter the user's username. The username must exist as a UID inside the Users relation.<br />

<br />You should now be able to use the menu corresponding to the user that you logged in as. Use the numbers before the option you want to select to interact with the menu, then follow the resulting prompts to use that menu option.

**Notes on Implementation Assumptions:**<br />
For the most part, only basic error checking has been provided in the code. We are assuming that the user/admin enters information in the exact formats requested and will not enter invalid data types or information that exceeds the size limits on our columns.<br /><br />
A book cannot be deleted if a user has already ordered it, as this would destroy the existing order records. However, it may be deleted if the user has it in their cart, in which case it is simply removed from the cart.<br /><br />
In terms of the expenditure vs revenue report, we didn't count payments of royalties to publishers as an expense, but rather deducted these from revenue. In other words, the revenue earned from the sale of one book was (1 - royalty) * price.<br /><br />
We assume that during restocking the bookstore buys books in bulk from the publisher at a price of 75-90% of the sale price (randomly generated). We also limit the book royalty to 0.1 or 10% such that any purchase and sale of books is profitable for the bookstore (the purchase price + royalty does not exceed 100%)<br /><br />
The ISBN in the Purchases table is intentionally not made a foreign key in order to allow books to be deleted from the Bookstore. Additionally, since the Purchases relation is only used to calculate costs, no additional information on books is needed. We assume that a new book cannot share an ISBN with one that was deleted from the Bookstore, since the deleted book still exists in the world, and is just no longer sold at this Bookstore. Therefore, ISBN will still be unique and may be used in the primary key.
