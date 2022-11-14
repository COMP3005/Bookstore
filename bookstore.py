import psycopg2

# connect to database
# note that Bookstore database will need to be created in Postgres and the password will need to be changed to your master password
conn = psycopg2.connect("dbname=Bookstore user=postgres password=WuQinFang-0418")

def initialize():
    #all initial ddl and dml statements to create the database
    commands = [
        """
        CREATE TABLE IF NOT EXISTS Users (
            uid VARCHAR(30) PRIMARY KEY,
            fName VARCHAR(30) NOT NULL,
            lName VARCHAR(30) NOT NULL,
            billing VARCHAR(80),
            shipping VARCHAR(80)
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
    if (username == "admin"):
        print("Successfully signed in as Admin!")


    else:
        select = "SELECT fName, lName FROM Users WHERE uid = %s"
        cursor = conn.cursor()
        cursor.execute(select, (username,))
        nameTuple = cursor.fetchone()
        fullName = nameTuple[0] + " " + nameTuple[1] 

        print("Successfully signed in as: {}".format(fullName))

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

if __name__ == "__main__":
    initialize()
    main()