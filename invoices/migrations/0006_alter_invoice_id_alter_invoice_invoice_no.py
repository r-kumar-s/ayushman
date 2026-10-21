
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0005_invoice_id_alter_invoice_invoice_no'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='invoice',
                    name='id',
                    field=models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                migrations.AlterField(
                    model_name='invoice',
                    name='invoice_no',
                    field=models.PositiveIntegerField(
                        blank=True,
                        editable=False,
                        null=True,
                    ),
                ),
            ],
        ),
    ]
