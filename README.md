# word-camp2026

## 📚 Resources
* **Project Files & Assets:** [Google Drive Folder](https://drive.google.com/drive/folders/183I_chrMV2J-zyh_jzg7e4OH82KrVJtv?usp=drive_link)

---

# 🚀 WordPress Deployment via Docker CLI

This document contains the specific one-liner commands to launch isolated WordPress and MySQL environments. By using this "Containerized" approach, each service stays in its own "bowl," preventing library conflicts on your laptop.

## 🛠️ Deployment Scripts

### 1. WordPress Instance 1 
This script creates a default  bridge  to allow the WordPress container to communicate with the MySQL container by name.

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








---

### 2. WordPress Instance 2

This script creates a default  bridge  to allow the WordPress container to communicate with its dedicated MySQL container by name, ensuring full isolation from Instance 2.

```bash
# Start Database 2
docker run -d --name wp-db-2 \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=db2 \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wp123 \
  mysql:5.7

# Wait for DB to initialize
sleep 20

# Start WordPress 2 linked to wp-db-2
docker run -d --name wordpress-2 \
  --link wp-db-2:mysql \
  -p 9090:80 \
  -e WORDPRESS_DB_HOST=mysql \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wp123 \
  -e WORDPRESS_DB_NAME=db2 \
  wordpress













---

### 2. WordPress Instance 3

This script creates a custom bridge network named `wp-net-3` to allow the WordPress container to communicate with its dedicated MySQL container by name, ensuring full isolation from Instance  1 and 2.

```bash
# Create a dedicated network for WP3 isolation
docker network create wp-net-3

# Start Database 3 on the new network
docker run -d --name wp-db-3 \
  --network wp-net-3 \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=db3 \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wp123 \
  mysql:5.7


# Wait for DB to initialize
sleep 20


# Start WordPress 3 on the same network
# Note: We use the container name 'wp-db-3' as the host address
docker run -d --name wordpress-3 \
  --network wp-net-3 \
  -p 9095:80 \
  -e WORDPRESS_DB_HOST=wp-db-3 \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wp123 \
  -e WORDPRESS_DB_NAME=db3 \
  wordpress


