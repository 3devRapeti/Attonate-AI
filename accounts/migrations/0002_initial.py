# Placeholder — the real initial schema was consolidated into 0001_initial
# after a mount restriction made it impossible to delete/rename migration
# files during development. This file is kept only so the migration graph
# stays consistent; it performs no operations.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = []
