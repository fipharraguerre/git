
---

# Azure Backup Vaults & Host Monitoring

This project is designed to monitor and log events from hosts and Azure Backup Vaults. The main functionality includes logging all restore points and saving events that result in a status other than "Success". This allows tracking and analyzing the frequency of failed or warning states for different tasks over a set period.

## Features

- **Data Upload Endpoint:** A Flask-based API that accepts JSON data and stores it in a MariaDB database.
- **Per-Host Tables:** Automatically creates a new table for each host or Backup Vault and logs all restore points.
- **Unsuccessful Tasks Logging:** Extracts and logs all events with statuses other than "Success" into a separate table called `unsuccessful_tasks`.
- **Periodic Job:** A planned job (separate script) that will run every 4 hours to remove duplicates and insert new failed or warning events into the `unsuccessful_tasks` table.
- **Custom Filters:** Allows filtering by client or hostname to count the number of non-successful events within a specific time frame.

## Getting Started

### Prerequisites

- Python 3.10 or later
- MariaDB Server
- Flask
- `mariadb` Python package
- `re` (regular expressions) module

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/backup-monitoring.git
   cd backup-monitoring
   ```

2. Set up a virtual environment (optional but recommended):
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the MariaDB database:
   ```sql
   CREATE DATABASE VeeamReports;
   ```

5. Configure the database connection in `main-auth-sql.py`:
   ```python
   g.db = mariadb.connect(
       host="localhost",
       port=3306,
       user="youruser",
       password="yourpassword",
       database="VeeamReports"
   )
   ```

### Running the API

To run the API, use the following command:
```sh
python main-auth-sql.py
```

The API will be available at `http://localhost:5000`.

### API Endpoints

- **POST /upload:** Uploads JSON data containing restore points. Requires an `Authorization` header.

### Planned Enhancements

- Implement a separate Python job that runs every 4 hours to manage the `unsuccessful_tasks` table.
- Improve filtering options and allow users to query unsuccessful tasks by date, host, or client.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to fork the repository and submit pull requests. If you encounter any issues, please open an issue on the GitHub repository.

---
