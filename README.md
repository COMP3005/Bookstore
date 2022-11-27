# Bookstore README
A COMP3005 project by Nazeeha Harun (101139836) and Evan Li (101188718)

**Overview:**<br />
This project is intended to simulate the basic features of a Bookstore database through a Python command line interface. We have used the "psycopg2" library to connect Python to PostgreSQL and execute queries from within our program. 

**SQL files:**<br />
These files have been included per the assignment requirements. However, the files are not used in the program in any way as we have opted to call SQL queries from within the code. Thus, the SQL files submitted will be copies of the queries which can be found in our code.

**Running the code:**<br />
In order to run the code, you will need a Python 3.10 interpreter and a PGAdmin account. Additionally, you will need to have the "psycopg2" library installed on your device - this can be done by using "pip3 install psycopg2" in your command line. You will also need to update the password on line 8 to reflect your own PGAdmin master password.<br /><br />
Please note that you will need to manually create the "Bookstore" database in PostgreSQL prior to running this program. Additionally, the initialization function provides ONLY DDL STATEMENTS, so you must use the program to add data to the tables.<br /><br />
Upon verifying that you have met all the above requirements, the code can be run in the terminal using "python bookstore.py". You will be asked to "log in" to the system as either an admin or an existing user, or create a new user. Please follow the comments in the code for how to log in as desired.<br />
To login as admin, you need the username "admin" and password "4dmin!".
Otherwise, create a new user by typing in "new" as the username and then follow the prompts. Once you are done creating a new user, you will be able to use your selected
username for the subsequent logins.


**Notes on Implementation Assumptions:**<br />
For the most part, only basic error checking has been provided in the code. We are assuming that the user/admin enters information in the exact formats requested and will not enter invalid data types or information that exceeds the size limits on our columns.<br /><br />
In terms of the expenditure vs revenue report, we didn't count payments of royalties to publishers as an expense, but rather deducted these from revenue. In other words, the revenue earned from the sale of one book was (1 - royalty) * price.<br /><br />
A book cannot be deleted if a user has already ordered it, as this would destroy the existing order records. However, it may be deleted if the user has it in their cart, in which case it is simply removed from the cart.
