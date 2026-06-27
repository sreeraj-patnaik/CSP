from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
        ('villages', '0001_initial'),
        ('visits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldvisit',
            name='villages',
            field=models.ManyToManyField(
                blank=True,
                help_text='Villages visited on this day (select multiple if needed)',
                related_name='visits_m2m',
                to='villages.village',
            ),
        ),
        migrations.AddField(
            model_name='fieldvisit',
            name='team_members',
            field=models.ManyToManyField(
                blank=True,
                help_text='Team members who attended this visit',
                related_name='field_visits',
                to='team.teammember',
            ),
        ),
        migrations.RemoveField(
            model_name='fieldvisit',
            name='village',
        ),
        # Now rename visits_m2m to visits (related_name)
        migrations.AlterField(
            model_name='fieldvisit',
            name='villages',
            field=models.ManyToManyField(
                blank=True,
                help_text='Villages visited on this day (select multiple if needed)',
                related_name='visits',
                to='villages.village',
            ),
        ),
    ]
