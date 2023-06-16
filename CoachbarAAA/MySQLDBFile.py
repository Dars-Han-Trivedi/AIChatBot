import mysql.connector

class MySQLDB:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            print("Connected to MySQL database.")
        except mysql.connector.Error as error:
            print(f"Failed to connect to MySQL database: {error}")

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully.")
        except mysql.connector.Error as error:
            print(f"Failed to execute query: {error}")

    def fetch_results(self):
        try:
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as error:
            print(f"Failed to fetch results: {error}")

    def close_connection(self):
        try:
            self.cursor.close()
            self.connection.close()
            print("Database connection closed.")
        except mysql.connector.Error as error:
            print(f"Failed to close database connection: {error}")

    def fetch_users(self):
        query = "SELECT * FROM CustomerService.users"
        result = self.execute_query(query)

        if result:
            return result["rows"]
        else:
            return None

    def fetch_user_by_id(self, user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        self.execute_query(query)
        columns = [column[0] for column in self.cursor.description]
        user = self.cursor.fetchone()

        if user:
            user_dict = dict(zip(columns, user))
            return user_dict
        else:
            return None