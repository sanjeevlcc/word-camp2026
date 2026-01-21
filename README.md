# word-camp2026


# 🚀 WordPress Deployment via Docker CLI

This document contains the specific one-liner commands to launch isolated WordPress and MySQL environments. By using this "Containerized" approach, each service stays in its own "bowl," preventing library conflicts on your laptop.

## 🛠️ Deployment Scripts

### 1. WordPress Instance 1 (Standard Network)
[cite_start]This script creates a custom bridge network named `wpnet` to allow the WordPress container to communicate with the MySQL container by name[cite: 73, 82, 84].

```bash
# Create a dedicated network
docker network create wpnet && \

# Launch the Database (MySQL 5.7)
docker run -d --name wp-mysql --network wpnet \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=wordpress \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wp123 \
  mysql:5.7 && \

# Wait for DB initialization (Crucial for connection)
sleep 20 && \

# Launch WordPress linked to the DB on Port 8080
docker run -d --name wordpress --network wpnet \
  -p 8080:80 \
  -e WORDPRESS_DB_HOST=wp-mysql:3306 \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wp123 \
  -e WORDPRESS_DB_NAME=wordpress \
  wordpress







### 2. WordPress Instance 2 (Secondary Port)
Use this script to launch a second independent instance on port 9090. This creates a separate database container to avoid naming conflicts on your system.

```bash
# Launch the second Database
docker run -d --name wp-mysql-2 \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=wordpress \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wp123 \
  mysql:5.7 && \

# Wait for DB initialization
sleep 20 && \

# Launch second WordPress instance on Port 9090
docker run -d --name wordpress-9090 \
  -p 9090:80 \
  -e WORDPRESS_DB_HOST=wp-mysql-2:3306 \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wp123 \
  -e WORDPRESS_DB_NAME=wordpress \
  wordpress





