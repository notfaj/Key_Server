# Key Server

This is an open-source key server built with Flask. It allows the generation, validation, and management of keys associated with products, including activation limits and expiration dates. The server includes functionality for logging requests, machine ID validation, and role-based access control for administrative actions.

## Features

- **Generate Keys**: Admins and users can generate keys with a defined expiration and machine usage limit.
- **Activate/Validate Keys**: Keys are validated by machine ID, preventing unauthorized use across multiple machines.
- **Manage Expiration Dates**: Admins can update the expiration date for all keys associated with a specific product ID.
- **Request Logging**: All key generation, validation, and management actions are logged, including IP addresses.
- **Role-Based Access Control**: Admins have full control over keys, while users have limited access.
- **Retrieve Logs and Keys**: Admins can retrieve request logs and keys data files.
- **Edit Keys**: Admins can edit key details such as expiration, machine limits, and activation status.
- **Serve Files for PKI Validation**: Serve specific files from the `.well-known/pki-validation` directory.

## Installation

### Prerequisites

- Python 3.9 or higher
- Flask 2.x
- A `.env` file for environment variables
