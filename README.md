
---

# Azure Backup Vaults & Veeam Host Monitoring

This project is designed to monitor and log events from Veeam hosts and Azure Backup Vaults.

## Features

- **Data Upload Endpoint:** A Flask-based API that accepts JSON data and stores it in a MariaDB database.
- **Per-Host Tables:** Automatically creates a new table for each host or Backup Vault and logs all restore points.
- **Unsuccessful Tasks Logging (WIP):** Extracts and logs all events with statuses other than "Success" into a separate table called `unsuccessful_tasks`.
- **Periodic Job (WIP):** A planned job (separate script) that will run every 4 hours to remove duplicates and insert new failed or warning events into the `unsuccessful_tasks` table.
- **Custom Filters (WIP):** Allows filtering by client or hostname to count the number of non-successful events within a specific time frame.

### Planned Enhancements

- Implement a separate Python job that runs every 4 hours to manage the `unsuccessful_tasks` table.
- Improve filtering options and allow users to query unsuccessful tasks by date, host, or client.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to fork the repository and submit pull requests. If you encounter any issues, please open an issue on the GitHub repository.

---
