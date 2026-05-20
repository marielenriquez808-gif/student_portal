import gzip
import shutil
import os
from datetime import datetime
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backup the database to JSON.gz and SQLite copy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--label', type=str, default='',
            help='Optional label appended to backup filename',
        )

    def handle(self, *args, **options):
        backup_dir = Path(getattr(settings, 'BACKUP_DIR', Path(settings.BASE_DIR) / 'backups'))
        max_files = int(getattr(settings, 'BACKUP_MAX_FILES', 30))
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        label = f"_{options['label']}" if options.get('label') else ''
        stem = f'backup_{timestamp}{label}'

        # ── JSON.gz backup via dumpdata ──────────────────────────────────────
        json_path = backup_dir / f'{stem}.json.gz'
        buf = StringIO()
        call_command(
            'dumpdata',
            'accounts', 'enrollment', 'grades', 'attendance',
            'schedules', 'announcements',
            '--natural-primary', '--natural-foreign',
            '--indent=2',
            stdout=buf,
        )
        raw = buf.getvalue().encode('utf-8')
        with gzip.open(str(json_path), 'wb') as gz:
            gz.write(raw)
        self.stdout.write(f'  JSON.gz  -> {json_path.name}  ({len(raw):,} bytes)')

        # ── SQLite binary copy ────────────────────────────────────────────────
        db_name = settings.DATABASES['default']['NAME']
        db_path = Path(str(db_name))
        if db_path.suffix in ('.sqlite3', '.db', '.sqlite') and db_path.exists():
            sqlite_path = backup_dir / f'{stem}.sqlite3'
            shutil.copy2(str(db_path), str(sqlite_path))
            self.stdout.write(f'  SQLite   -> {sqlite_path.name}')

        # ── Rotate old backups ────────────────────────────────────────────────
        self._rotate(backup_dir, 'backup_*.json.gz', max_files)
        self._rotate(backup_dir, 'backup_*.sqlite3', max_files)

        self.stdout.write(self.style.SUCCESS(f'Backup complete: {stem}'))

    def _rotate(self, backup_dir, pattern, max_files):
        files = sorted(backup_dir.glob(pattern))
        while len(files) > max_files:
            oldest = files.pop(0)
            oldest.unlink()
            self.stdout.write(f'  Removed  -> {oldest.name}')
