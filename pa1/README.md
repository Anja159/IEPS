
  

### Instructions

  

## DB setup:

  

1. Run docker-compose up
    Creds:
    - username: user
    - password: SecretPassword

2. Connect to DB via pgAdmin


  
or

  

2. Connect to DB via cmd

  

- ``docker exec -it postgresql-ieps bash``: Opens an interactive shell inside the postgresql-ieps Docker container,
- ``psql -h localhost -p 5432 -U user user``: Connects to a PostgreSQL database named user on the local machine using the username user,
- ``\c user``: Switches the connection to another database named user within the psql interface,
- ``SELECT * FROM page``: Retrieves all data from the table named page in the database

