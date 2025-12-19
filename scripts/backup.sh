DB_NAME="EdyBuddy"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$BASE_DIR/backup"

DATE=$(date +"%Y-%m-%d_%H-%M")
FILE="$BACKUP_DIR/backup_$DATE.sql"


mkdir -p "$BACKUP_DIR"

pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME > "$FILE"

find "$BACKUP_DIR" -type f -name "*.sql" -mtime +7 -delete

echo "Backup created: $FILE"