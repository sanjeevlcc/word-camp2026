# word-camp2026

## 📚 Resources
* **Project Files & Assets:** [Google Drive Folder](https://drive.google.com/drive/folders/183I_chrMV2J-zyh_jzg7e4OH82KrVJtv?usp=drive_link)

---

# 🚀 WordPress Deployment via Docker CLI

This document contains the specific one-liner commands to launch isolated WordPress and MySQL environments. By using this "Containerized" approach, each service stays in its own "bowl," preventing library conflicts on your laptop.

## 🛠️ Deployment Scripts

### 1. WordPress Instance 1 (Standard Network)
This script creates a custom bridge network named `wpnet` to allow the WordPress container to communicate with the MySQL container by name.

```bash

# Start Database 1
docker run -d --name wp-db-1 \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=db1 \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wp123 \
  mysql:5.7



# Wait for DB to initialize
sleep 20



# Start WordPress 1 linked to wp-db-1
docker run -d --name wordpress-1 \
  --link wp-db-1:mysql \
  -p 8080:80 \
  -e WORDPRESS_DB_HOST=mysql \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wp123 \
  -e WORDPRESS_DB_NAME=db1 \
  wordpress






### 2. WordPress Instance 2 (Standard Network)

This script creates a custom bridge network named `wpnet-2` to allow the WordPress container to communicate with its dedicated MySQL container by name, ensuring full isolation from Instance 1.

```bash
# Create a dedicated network for Instance 2
docker network create wpnet-2 && \

# Launch the Database (MySQL 5.7)
docker run -d --name wp-mysql-2 --network wpnet-2 \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=wordpress \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wp123 \
  mysql:5.7 && \

# Wait for DB initialization (Crucial for connection)
sleep 20 && \

# Launch WordPress on Port 9090
docker run -d --name wordpress-2 --network wpnet-2 \
  -p 9090:80 \
  -e WORDPRESS_DB_HOST=wp-mysql-2:3306 \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wp123 \
  -e WORDPRESS_DB_NAME=wordpress \
  wordpress






