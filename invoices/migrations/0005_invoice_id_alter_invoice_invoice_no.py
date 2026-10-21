
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0004_invoice_invoice_number_alter_invoiceitem_uom'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='invoice',
                    name='invoice_no',
                    field=models.PositiveIntegerField(
                        editable=False,
                        unique=True,
                    ),
                ),
                migrations.AddField(
                    model_name='invoice',
                    name='id',
                    field=models.AutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),
            ],
        ),
    ]
