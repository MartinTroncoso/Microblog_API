#!/bin/sh
set -e

echo "📡 Waiting for PostgreSQL to be ready..."

until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; do
  echo "⏳ Waiting for the database to be fully operational..."
  echo $DB_HOST,$DB_USER,$DB_NAME
  sleep 1
done

echo "✅ Database ready."

echo "⚙️ Applying migrations..."
python manage.py makemigrations
python manage.py migrate

echo "🚀 Initiating server with command: $@"
exec "$@"