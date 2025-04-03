# Transaction Tracker

A Django application for tracking cryptocurrency transactions and portfolio performance with Kafka integration.

## Running with Docker (Recommended)

The easiest way to run this application is using Docker and Docker Compose.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Quick Start

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/transaction-tracker.git
   cd transaction-tracker
   ```

2. Start the application:

   ```
   docker-compose up
   ```

3. Access the application:
   - Main application: http://localhost:8000/
   - Admin interface: http://localhost:8000/admin/

### Running in Background

To run the application in the background:

## Crypto Transaction Tracker

Crypto Transaction Manager is a web application that allows users to record, edit, delete, filter, and add cryptocurrency transactions. It provides an easy-to-use interface for managing your crypto transactions

## Features

- Record cryptocurrency transactions.
- Edit or delete existing transactions.
- Filter transactions based on date, coin, or transaction type.
- View a summary of all transactions.
- Responsive UI built with Tailwind CSS for a smooth user experience.

## Live Demo

The application is deployed on Heroku and can be accessed [here](https://magical-coin-tracker-e4f3fa405d71.herokuapp.com/).

## Installation

1. Clone the repository

   ```bash
   git clone <repository-link>

   ```

2. Navigate to the project directory

   ```bash
    cd <project-directory>

   ```

3. Set up the virtual environment

   ```bash
   python -m venv venv

   ```

4. Activate the virtual environment

   ```bash
    source venv/bin/activate

   ```

5. Install the dependencies

   ```bash
   pip install -r requirements.txt

   ```

6. Set up PostgreSQL database

- Ensure you have PostgreSQL installed and create a new database.
- Update the DATABASES setting in settings.py with your PostgreSQL credentials

7. Apply migrations

   ```bash
   python manage.py migrate

   ```

8. Run the development server
   ```bash
   python manage.py runserver
   ```

## Usage

1. Add Transaction

- Navigate to the "Add Transaction" page.
- Fill out the form with details such as the coin name, transaction type (buy/sell), amount, and date.
- Submit the form to add the transaction to your records.

2. Edit/Delete Transaction

- View your transaction list and click the "Edit" or "Delete" button next to any transaction to modify or remove it.

3. Filter Transactions

- Use the filter options (date, coin, transaction type) to refine the list of transactions and view specific data.

## Technologies Used

- Django: Backend framework
- PostgreSQL: Database
- Python: Core programming language
- HTML & JavaScript: Frontend structure and interactivity
- Tailwind CSS: Styling framework for a responsive design
