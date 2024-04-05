
  

## Instructions


### Prerequisites
-  Install required Python libraries through pip:
```
pip install selenium
pip install psycopg2
pip install nb_conda
pip install requests
pip install pyopenssl
```
-  Install the Chrome web browser and download the Selenium Chrome driver that is compliant with your version. The version of the driver included in this repository is 123.0.6312.86.
They can be found at this link: https://googlechromelabs.github.io/chrome-for-testing/

### DB setup:

  

1. Run docker-compose up
    Credentials:
    - username: user
    - password: SecretPassword

2. Connect to DB via pgAdmin (Application)


  
or

  

2. Connect to DB via CLI (bash shell)

  

- ``docker exec -it postgresql-ieps bash``: Opens an interactive shell inside the postgresql-ieps Docker container,
- ``psql -h localhost -p 5432 -U user user``: Connects to a PostgreSQL database named user on the local machine using the username user,
- ``\c user``: Switches the connection to another database named user within the psql interface,
- ``SELECT * FROM page``: Retrieves all data from the table named page in the database

### Usage
In the project folder in CLI, move from the root folder to pa1/crawler, so you can start it with:

```
python crawler.py
```
The default is set to 16 threads.
