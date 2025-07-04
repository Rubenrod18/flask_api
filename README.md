# Flask Api

Flask-api is a small API project for creating users and files (Microsoft Word and PDF). These files contain data about users registered in the project.

---

## 🛠️ Local Environment Installation

To set up locally, follow these steps:

### 1. Copy `.env.example` to `.env` and `.env.test`

- Create `.env` and `.env.test` files from the provided `.env.example` and update the necessary environment variables.

### 2. Create a Database User in SQL Docker Container

Ensure that your Docker container for `sql` is set up by running the following:

```bash
make local.build && make local.start
```

Next, connect to the SQL container:

```bash
docker exec -it flask_api__mysql bash
mysql -u root -p
```

In the MySQL shell, run the following commands to create a database, a user and grant privileges:

```sql
CREATE DATABASE flask_api;
CREATE USER 'user'@'%' IDENTIFIED BY 'newpassword';
GRANT ALL PRIVILEGES ON *.* TO 'user'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

You can stop the Docker app now: `make local.stop`.

### 3. Add the hostname in your hosts file, for example:

```bash
[...]
127.0.0.1 flask-api.local
[...]
```

### 4. Build and Run the Application

Once the database is set up, proceed to build and run the application with:

```bash
make local.start
cd src
make migrate
make seed
```

This will start the Flask application with the appropriate database setup.

---


## Application Layer Components

The application follows some of the ideas of Domain Driven Design arquitecture:

![Application Layer Components Diagram](docs/app_layer_components.png)

1. **Serializer**: Converts data structures (often Python objects) to formats suitable for responses (e.g., JSON) and vice versa. Responsible for validating and transforming input/output data. Acts as a bridge between the endpoint (request/response) and the service layer, handling both serialization and deserialization.

2. **Service**: Contains the application’s use-case-specific logic. Handles requests from endpoints, manages workflow, and orchestrates interactions between repositories.

3. **Repository**: Abstracts data persistence and retrieval. Responsible solely for executing database queries and data manipulation. Provides an interface to interact with database models, isolating data access and keeping business logic out of the persistence layer.

4. **Database Model**: Defines the structure of the data as Python classes (typically using an ORM), mapping objects to database tables. Handles schema definition, relationships, and direct interaction with the database.

5. **File Storage**: Responsible for saving, retrieving, and deleting files. Provides an interface for file operations such as uploading, downloading, copying, and deleting files. Interacts exclusively with the Service layer, keeping file-handling logic separate from business and data access logic. Only for local environment.

6. **Provider**: Responsible for external communication with others services such as Google Drive, AWS, Azure, etc.


## Component Interaction Diagram

The following diagram illustrates the main components and their interactions within the application architecture:

![Component Interaction Diagram](docs/component_interaction_diagram.png)

### Main Interactions

1. **Request Flow**:
   - Users make requests via the API Layer.
   - The API passes validated data to the Service Layer.
   - The Service Layer interacts with the Repository Layer for data operations and may trigger background tasks or file storage as needed.

2. **Task Processing**:
   - The Service Layer can enqueue tasks to the Task Queue, which are processed asynchronously.

3. **Persistence**:
   - Data flows from the Service Layer to the Repository Layer, which communicates with the Database.

4. **File Storage**:
   - The Service Layer handles file uploads/downloads via the Storage component or the Provider.


---

## 📄 License

This project is licensed under the MIT License.

---

## 📢 Contributing

We welcome contributions! Feel free to submit issues, feature requests, or pull requests to improve `flask_api`.
