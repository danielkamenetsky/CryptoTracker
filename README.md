# Transaction Tracker

A Django application for tracking cryptocurrency transactions and portfolio performance with Kafka integration.

## Video Demonstration (Loom)

Want to see the application in action without setting it up yourself? Watch a quick video walkthrough below. This is a great option if you're having trouble with the setup steps or just want a quick preview:

[Video Walkthrough](https://www.loom.com/share/bfa98368d6164e0186f83339202a1953?sid=43663764-b179-4c8e-a5f4-b66e983d4b81)

## Running with Docker (Recommended)

The easiest and recommended way to run this application locally is using Docker and Docker Compose. This ensures all services (web app, database, Redis, Kafka, Zookeeper, price updater) are set up correctly.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (Usually included with Docker Desktop)

### Quick Start

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-link>
    cd CryptoTracker
    ```

2.  **Build and Start:**
    _(The first time you run this, it might take a few minutes to download images and build the application container.)_

    ```bash
    docker compose up --build
    ```

    _(For subsequent runs, you can just use `docker compose up`)_

3.  **Apply Migrations (First time setup):**
    Wait for the initial `docker compose up` logs to settle (especially the database). Then, open a **new terminal window** in the same project directory and run:

    ```bash
    docker compose exec web python manage.py migrate
    ```

    _(You only need to do this the first time or when database models change)._

4.  **Access the application:**
    Once the containers are running (you'll see logs from various services like `web-1`, `db-1`, `kafka-broker-1`, etc.) and you see the message `web-1 | Starting development server at http://0.0.0.0:8000/`, you can access the application in your browser:
    - **Main application:** http://localhost:8000/
    - **Admin interface:** http://localhost:8000/admin/ (You might need to create a superuser first, see below)

### Common Docker Commands

- **Start services in background:** `docker compose up -d`
- **Stop services:** `docker compose down` (use `docker compose down -v` to also remove volumes like the database data)
- **View logs:** `docker compose logs` (or `docker compose logs -f` to follow)
- **View logs for a specific service:** `docker compose logs web`
- **Run a command inside a container (e.g., create superuser):**
  ```bash
  docker compose exec web python manage.py createsuperuser
  ```
- **Rebuild an image:** `docker compose build web`

---

## Manual Installation (Alternative)

If you cannot use Docker, you can run the application manually, but you will need to install and manage PostgreSQL, Redis, Kafka, and Zookeeper separately.

### Prerequisites

- Python 3.9+ and Pip
- [PostgreSQL](https://www.postgresql.org/download/)
- [Redis](https://redis.io/docs/getting-started/installation/)
- [Kafka and Zookeeper](https://kafka.apache.org/quickstart) (This is the most complex part to set up manually)

### Setup Steps

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-link>
    cd transaction-tracker
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up PostgreSQL:**

    - Ensure your PostgreSQL server is running.
    - Create a database and a user for the application.
    - Set the `DATABASE_URL` environment variable. Example format:
      ```bash
      export DATABASE_URL="postgres://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DB_NAME"
      ```
      _(Or configure the `DATABASES` setting in `transaction_tracker/settings.py` directly, though using environment variables is recommended)._

5.  **Set up Redis:**

    - Ensure your Redis server is running (usually on `localhost:6379`).
    - If Redis is running on a different host/port, set the `REDIS_HOST` and `REDIS_PORT` environment variables.

6.  **Set up Kafka & Zookeeper:**

    - Ensure Zookeeper and Kafka brokers are running.
    - If Kafka is not on `localhost:9092`, set the `KAFKA_BOOTSTRAP_SERVERS` environment variable.

7.  **Apply database migrations:**

    ```bash
    python manage.py migrate
    ```

8.  **Create a superuser (for admin access):**

    ```bash
    python manage.py createsuperuser
    ```

9.  **Run the Django development server:**

    ```bash
    python manage.py runserver
    ```

    The application will be available at http://127.0.0.1:8000/.

10. **Run the Price Updater Service:**
    In a **separate terminal** (with the virtual environment activated and environment variables set), run:
    ```bash
    python manage.py update_prices
    ```

## Technologies Used

- Django: Backend framework
- PostgreSQL: Database
- Python: Core programming language
- HTML & JavaScript: Frontend structure and interactivity
- Tailwind CSS: Styling framework for a responsive design
