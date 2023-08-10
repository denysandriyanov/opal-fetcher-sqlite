FROM alpine:latest

RUN apk add --no-cache sqlite

# Copy the init_db.sql file into the Docker image
COPY sqlite_data/init_db.sql /init_db.sql

# Run the SQLite initialization script
RUN sqlite3 opal.db < /init_db.sql
