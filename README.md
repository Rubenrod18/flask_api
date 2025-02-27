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
docker exec -it flask_api_db bash
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

## 📄 License

This project is licensed under the MIT License.

---

## 📢 Contributing

We welcome contributions! Feel free to submit issues, feature requests, or pull requests to improve `flask_api`.

---

## Learning more

See the [documentation][documentation] for more details.


[documentation]: https://flask-api.readthedocs.io/en/latest/
