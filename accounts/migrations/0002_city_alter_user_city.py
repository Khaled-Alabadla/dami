import django.db.models.deletion
from django.db import migrations, models


def seed_cities(apps, schema_editor):
    City = apps.get_model('accounts', 'City')
    for name in ('غزة', 'خانيونس', 'الوسطى'):
        City.objects.get_or_create(name=name)


def migrate_user_cities(apps, schema_editor):
    City = apps.get_model('accounts', 'City')
    User = apps.get_model('accounts', 'User')
    default_city = City.objects.first()
    for user in User.objects.all():
        old_name = user.city_old
        if old_name:
            city, _ = City.objects.get_or_create(name=old_name)
        else:
            city = default_city
        user.city = city
        user.save(update_fields=['city'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='اسم المدينة')),
            ],
            options={
                'verbose_name': 'مدينة',
                'verbose_name_plural': 'المدن',
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(seed_cities, migrations.RunPython.noop),
        migrations.RenameField(
            model_name='user',
            old_name='city',
            new_name='city_old',
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='users',
                to='accounts.city',
                verbose_name='المدينة',
            ),
        ),
        migrations.RunPython(migrate_user_cities, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='user',
            name='city_old',
        ),
        migrations.AlterField(
            model_name='user',
            name='city',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='users',
                to='accounts.city',
                verbose_name='المدينة',
            ),
        ),
    ]
