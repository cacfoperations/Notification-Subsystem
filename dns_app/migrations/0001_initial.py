# Generated by Django 3.1.4 on 2021-03-31 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('email_to', models.EmailField(max_length=500)),
                ('email_from', models.EmailField(max_length=500)),
                ('imei', models.CharField(blank=True, max_length=50, null=True)),
                ('subsystem', models.CharField(max_length=100)),
                ('filename', models.CharField(blank=True, max_length=200, null=True)),
                ('email_delivered', models.DateTimeField(auto_now_add=True, null=True)),
                ('campaign_id', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sms',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('sms_to', models.CharField(max_length=50)),
                ('sms_from', models.CharField(max_length=50)),
                ('imei', models.CharField(blank=True, max_length=50, null=True)),
                ('subsystem', models.CharField(max_length=100)),
                ('filename', models.CharField(blank=True, max_length=200, null=True)),
                ('sms_delivered', models.DateTimeField(auto_now_add=True, null=True)),
                ('operator', models.CharField(max_length=100)),
                ('campaign_id', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UniqueEmail',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=50)),
                ('email_received', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UniqueMsisdn',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('msisdn', models.CharField(max_length=50)),
                ('msisdn_received', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SmsContent',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('sms_content', models.TextField()),
                ('sms', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sms_contents', to='dns_app.sms')),
            ],
        ),
        migrations.CreateModel(
            name='EmailContent',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('email_subject', models.TextField()),
                ('email_content', models.TextField()),
                ('email', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dns_app.email')),
            ],
        ),
    ]
