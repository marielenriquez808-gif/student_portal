import gzip
import os
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Restore database from a backup file (.json.gz or .sqlite3)'

    def add_arguments(self, parser):
        parser.add_argument('backup_file', type=str, help='Path to the backup file')
        parser.add_argument(
            '--yes', action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        backup_file = Path(options['backup_file'])
        if not backup_file.exists():
            raise CommandError(f'File not found: {backup_file}')

        if not options['yes']:
            self.stdout.write(self.style.WARNING(
                f'This will overwrite the current database with {backup_file.name}.\n'
                'Type "yes" to continue: '
            ), ending='')
            answer = input().strip().lower()
            if answer != 'yes':
                self.stdout.write('Aborted.')
                return

        if backup_file.suffix == '.gz' and backup_file.stem.endswith('.json'):
            self._restore_json_gz(backup_file)
        elif backup_file.suffix == '.sqlite3':
            self._restore_sqlite(backup_file)
        else:
            raise CommandError('Unsupported backup format. Use .json.gz or .sqlite3')

        self.stdout.write(self.style.SUCCESS(f'Restore complete from {backup_file.name}'))

    def _restore_json_gz(self, backup_file):
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.json')
        try:
            with gzip.open(str(backup_file), 'rb') as gz:
                data = gz.read()
            with os.fdopen(tmp_fd, 'wb') as tmp:
                tmp.write(data)
            call_command('loaddata', tmp_path, verbosity=1)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _restore_sqlite(self, backup_file):
        db_name = settings.DATABASES['default']['NAME']
        db_path = Path(str(db_name))
        shutil.copy2(str(backup_file), str(db_path))
        self.stdout.write(f'  SQLite file restored from {backup_file.name}')
