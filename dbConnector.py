import mysql.connector
from MetaSingleton import MetaSingleton

MAX_ADDRESS = 5
HOST = "localhost"
USER = "flayb"
PASSWORD = "latias456"
DATABASE = "ETHBot"
AUTH_PLUGIN = "mysql_native_password"

# Database format for users:
# id, name, nbAddress

# Database format for addresses:
# id, ethAddress, currency

class DbConnector(metaclass=MetaSingleton):

    conn = None

    def init(self):
        global conn 
        conn = mysql.connector.connect(host=HOST,user=USER,password=PASSWORD, database=DATABASE, auth_plugin=AUTH_PLUGIN)

    def stopConnection(self):
        global conn
        conn.close()

    # Add ETH address to database with !eth add <ETH address> <currency>
    # return 0 if address not in database
    # return 1 if address in database and linked to user
    def addAddress(self, id, address, currency):
        global conn
        cursor = conn.cursor()
        # Get all addresses for user
        cursor.execute("SELECT * FROM ETHAddress WHERE id = %s", (id,))
        addresses = cursor.fetchall()

        # Check if address already exists
        for addressDB in addresses:
            if (addressDB[1] == address):
                return -1

        # Check if user already exists
        cursor.execute("SELECT * FROM Users WHERE name = %s", (id,))
        user = cursor.fetchall()
        if (len(user) == 0):
            cursor.execute("INSERT INTO Users (name, nbAddress) VALUES (%s, %s)", (id, MAX_ADDRESS))
            conn.commit()

        # Verify user has enough space to add address
        # Count number of addresses linked to user and compare with nbAddress
        cursor.execute("SELECT COUNT(*) FROM ETHAddress WHERE id = %s", (id,))
        addresses = cursor.fetchall()
        cursor.execute("SELECT nbAddress FROM Users WHERE name = %s", (id,))
        user = cursor.fetchall()
        print( " addresses " + str(addresses[0][0]) + " userNB " + str(user[0][0]))
        if (int(addresses[0][0]) >= int(user[0][0])):
            return -2
        
        # Add address to database
        cursor.execute("INSERT INTO ETHAddress (id, ethAddress, currency) VALUES (%s, %s, %s)", (id, address, currency))
        conn.commit()
        return 0

    # Get list of ETH addresses linked to user with !eth list
    def getAddresses(self, id):
        global conn
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ETHAddress WHERE id = %s", (id,))
        return cursor.fetchall()

    # Remove ETH address from database with !eth remove <ETH address>
    # return 1 if address not in database or not linked to user
    # return 0 if address in database and linked to user
    def removeAddress(self, id, address):
        global conn
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ETHAddress WHERE id = %s", (id,))
        addresses = cursor.fetchall()
        print(addresses)
        print ("address to delete : " + address)

        #Check if address already exists
        for addressDB in addresses:
            print(addressDB)
            if (addressDB[1] == address):
                cursor.execute("DELETE FROM ETHAddress WHERE id = %s AND ethAddress = %s", (id, address))
                conn.commit()
                return 0
        return 1