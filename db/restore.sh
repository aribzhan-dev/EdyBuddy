DB_NAME="EdyBuddy"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$BASE_DIR/backup"

FILE="$1"

if [ -z "$FILE" ]; then
  echo "Backup file not specified"
  echo "Usage: ./db/restore.sh backup_YYYY-MM-DD_HH-MM.sql"
  exit 1
fi

FULL_PATH="$BACKUP_DIR/$FILE"

if [ ! -f "$FULL_PATH" ]; then
  echo "Backup file not found: $FULL_PATH"
  exit 1
fi

echo "DATABASE WILL BE DROPPED: $DB_NAME"
read -p "Type YES to continue: " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
  echo "Restore cancelled"
  exit 0
fi

dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < "$FULL_PATH"

echo "Restore completed successfully"