#!/bin/bash

# Bot Creator Platform Database Setup Script
# This script sets up MariaDB database for the Bot Creator Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"3306"}
DB_USER=${DB_USER:-"botcreator"}
DB_PASSWORD=${DB_PASSWORD:-"botcreator123"}
DB_NAME=${DB_NAME:-"botcreator"}
ROOT_PASSWORD=${ROOT_PASSWORD:-""}

echo -e "${BLUE}=== Bot Creator Platform Database Setup ===${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if MariaDB/MySQL is running
check_database_service() {
    print_status "Checking if MariaDB/MySQL service is running..."
    
    if systemctl is-active --quiet mariadb; then
        print_status "MariaDB service is running"
        DB_SERVICE="mariadb"
    elif systemctl is-active --quiet mysql; then
        print_status "MySQL service is running"
        DB_SERVICE="mysql"
    else
        print_error "Neither MariaDB nor MySQL service is running"
        print_status "Starting MariaDB service..."
        sudo systemctl start mariadb || sudo systemctl start mysql
        sleep 3
    fi
}

# Install MariaDB if not present
install_mariadb() {
    if ! command -v mysql &> /dev/null && ! command -v mariadb &> /dev/null; then
        print_status "Installing MariaDB..."
        sudo apt update
        sudo apt install -y mariadb-server mariadb-client
        sudo systemctl enable mariadb
        sudo systemctl start mariadb
        sleep 3
    else
        print_status "MariaDB/MySQL is already installed"
    fi
}

# Secure MariaDB installation
secure_mariadb() {
    print_status "Securing MariaDB installation..."
    
    # Create a temporary SQL file for secure installation
    cat > /tmp/secure_mariadb.sql << EOF
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
FLUSH PRIVILEGES;
EOF
    
    # Run secure installation
    sudo mysql < /tmp/secure_mariadb.sql
    rm /tmp/secure_mariadb.sql
    
    print_status "MariaDB secured successfully"
}

# Create database user
create_database_user() {
    print_status "Creating database user and database..."
    
    # Create SQL commands
    cat > /tmp/create_user.sql << EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';

GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'%';

FLUSH PRIVILEGES;
EOF
    
    # Execute as root
    if [ -n "$ROOT_PASSWORD" ]; then
        mysql -u root -p"$ROOT_PASSWORD" < /tmp/create_user.sql
    else
        sudo mysql < /tmp/create_user.sql
    fi
    
    rm /tmp/create_user.sql
    print_status "Database user and database created successfully"
}

# Initialize database schema
initialize_database() {
    print_status "Initializing database schema..."
    
    # Run the initialization script
    mysql -u "$DB_USER" -p"$DB_PASSWORD" -h "$DB_HOST" -P "$DB_PORT" "$DB_NAME" < database/init_database.sql
    
    print_status "Database schema initialized successfully"
}

# Test database connection
test_connection() {
    print_status "Testing database connection..."
    
    if mysql -u "$DB_USER" -p"$DB_PASSWORD" -h "$DB_HOST" -P "$DB_PORT" "$DB_NAME" -e "SELECT 1;" > /dev/null 2>&1; then
        print_status "Database connection successful!"
    else
        print_error "Database connection failed!"
        exit 1
    fi
}

# Create .env file
create_env_file() {
    print_status "Creating .env file..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_status ".env file created from .env.example"
        print_warning "Please review and update the .env file with your specific configuration"
    else
        print_status ".env file already exists"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}Starting database setup...${NC}"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # Install MariaDB if needed
    install_mariadb
    
    # Check database service
    check_database_service
    
    # Secure MariaDB
    secure_mariadb
    
    # Create database user
    create_database_user
    
    # Initialize database
    initialize_database
    
    # Test connection
    test_connection
    
    # Create .env file
    create_env_file
    
    echo ""
    echo -e "${GREEN}=== Database setup completed successfully! ===${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Review the .env file and update if needed"
    echo "2. Install Python dependencies: pip install -r requirements.txt"
    echo "3. Run the application: python3 app.py"
    echo ""
    echo -e "${BLUE}Database connection details:${NC}"
    echo "Host: $DB_HOST"
    echo "Port: $DB_PORT"
    echo "Database: $DB_NAME"
    echo "User: $DB_USER"
    echo "Password: $DB_PASSWORD"
    echo ""
}

# Run main function
main "$@"