import psycopg2

# Connection parameters
conn_params = {
    "host": "ep-nameless-forest-a4upu4jj.us-east-1.aws.neon.tech",
    "port": 5432,
    "database": "verceldb",
    "user": "default",
    "password": "I6v0XghdjVAW"
}

# Connect to the database
conn = psycopg2.connect(**conn_params)

# Create a cursor
cur = conn.cursor()

# Example query
cur.execute("SELECT recommendation FROM users;")
rows = cur.fetchall()
for row in rows:
    print(row)

# Close cursor and connection
cur.close()
conn.close()
