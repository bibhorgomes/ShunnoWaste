import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="shunnowaste_db",
    )
    # host="localhost", user="jobairhossain_alteruse", passwd="alterUSE@123", database="jobairhossain_alteruse_db"

    return connection
