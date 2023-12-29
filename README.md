# Library Service API
### Service for online management system for book borrowings


###### The system optimizes the work of library administrators and makes the service much more user-friendly.

### Users Service
- **CRUD Functionality:** Successfully implemented Create, Read, Update, and Delete functionality for the Users Service.
- **JWT Support:** Added JWT support for secure authentication.

### Books Service
- **CRUD Functionality:** Implemented Create, Read, Update, and Delete functionality for the Books Service.
- **JWT Token Authentication:** Integrated JWT token authentication from the Users Service.
- **Permissions:** Only admin users can perform create, update, and delete operations on books. All users, even those not authenticated, can list books.


### Borrowings Service
- **Create Borrowing Endpoint:** Implemented the creation of borrowings with validation for book inventory and user attachment.
- **Filtering:** Added filtering options for the Borrowings List endpoint, ensuring non-admin users can see only their borrowings.
- **Return Borrowing Functionality:** Implemented the ability to return borrowings, ensuring it cannot be done twice, and updating the book inventory accordingly.

### ModHeader Integration
**Chrome Extension Compatibility:**
Improved user experience during work with the `ModHeader` Chrome extension by changing the default `Authorization` header for JWT authentication to a custom `Authorize` header.

### API Documentation
- Spectacular Integration.
- **Redoc UI:** Utilize Redoc for clean and readable API documentation at `/api/doc/redoc/`.
- **Swagger UI:** Access the Swagger UI for interactive API documentation at `/api/doc/swagger/`.
- **Schema Endpoint:** The API schema is available at `/api/schema/`.


## Usage

1. Clone the repository.
2. Set up environment variables using `.env.sample` as a guide.
3. Run the application.


## Installation using GitHub

Install PostgresSQL and create db

```shell
git clone https://github.com/lobodInI/Library-Service-API
cd Library-Service-API

python -m venv venv
pip install -r requirements.txt

set DB_HOST=<your db hostname>
set DB_NAME=<your db name>
set DB_USER=<your db username>
set DB_PASSWORD=<your db user password>
set SECRET_KEY=<your django secret key>
set DEBUG=<your debug value>

python manage.py migrate
python manage.py runserver
```
## Run with docker

Docker should be installed
```angular2html
docker-compose build
docker-compose up
```

## Getting access
- create a user via **/api/user/register**
- get access token via **/api/user/token**