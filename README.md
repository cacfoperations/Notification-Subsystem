
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission.
* The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details
provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.

## NS - Notification Subsystem
Notification Subsystem is a part of the Device Identification, Registration and Blocking (DIRBS) System.
The main purpose of DNS is to facilitate the notifications among users and subsystems.

### Documentation

### Frontend Application Repo

### Directory & Files structure
This repository contains code for **DNS** part of the **DIRBS**. Based on Django's MVT model, it contains below structure;

* ``device_notification_subsystem/settings`` -- The main settings.py file which contains the definition of all project related apps and their initiations   
* ``device_notification_subsystem/urls`` -- Urls.py contains URLs of all the apps and route to their related urls.py in its respective apps directory
* ``device_notification_subsystem/celery`` -- A file, contains the definition of Celery-App to be used in all celery workers & related queues
* ``dns_app/management`` -- Directory to hold modules for CLI commands
* ``dns_app/common`` -- Contains the modules common to all apps 
* ``dns_app/migrations`` -- This Directory contains the DB migration files. These files have details regarding Db models and changes recently occurred in DB Models  
* ``dns_app/apps`` -- A module that contains the name of the app
* ``dns_app/admin`` -- A module that registers the models whose details you want to be available on Django-Admin Panel 
* ``dns_app/models`` -- The main module that contains all the DB Models
* ``dns_app/views`` -- The Core module which contains all the ViewSets
* ``dns_app/urls`` -- Urls.py contains all APIs' URLs & their related functions/classes/ViewSets in views.py
* ``dns_app/tests`` -- Unit test scripts and Data
* ``dns_app/tasks`` -- A module that contains all the celery related tasks
* ``dns_app/documents`` -- A module that contains all the translations of Django DB-Models to Elasticsearch indices and documents 
* ``dns_app/paginations`` -- Module defines all the custom Paginations used by ModelViewSet in views.py
* ``dns_app/serializers`` -- Contains ModelSerializers for all the Django DB-Models


### Prerequisites
In order to run a development environment, [Python 3.6 or higher](https://www.python.org/download/releases/3.0/) and
[Postgresql10](https://www.postgresql.org/about/news/1786/) are assumed to be already installed.

We also assume that this repo is cloned from Github onto the local computer, it is assumed that
all commands mentioned in this guide are run from root directory of the project and inside
```virtual environment```

On Windows, we assume that a Bash like shell is available (i.e Bash under Cygwin), with GNU make installed.

### Starting a dev environment
The easiest and quickest way to get started is to use local-only environment (i.e everything runs locally, including
Postgresql Server). To setup the local environment, follow the section below:

### Setting up local dev environment
For setting up a local dev environment we assume that the ```prerequisites``` are met already. To setup a local
environment:
* Create database using Postgresql (Name and credentials should be same as in [settings.py](device_notification_subsystem/settings.py))
* Create virtual environment using **virtualenv** and activate it:

To install Virtual Environment Wrapper
```bash
pip install virtualenvwrapper-win
```
To Create Virtual Environment
```bash
mkvirtualenv dns_env
```
To Activate Virtual Environment
```bash
workon dns_env
  or
source dns_env/bin/activate
```
To install Django
```bash
pip install django
```
Go to directory where you want to create the DNS Project
```bash
django-admin startproject notification_subsystem
```
To create app within the project
```bash
python manage.py startapp dns_app
```
To install required libraries via requirements.txt
```bash
pip install -r requirements.txt
```
Open settings.py in project directory and add below apps in **INSTALLED_APPS** List.

    INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'dns_app',
            'django_celery_results',
            'django_celery_beat',
            'rest_framework',
            'django_elasticsearch_dsl',
        ]

In the same settings.py file include database settings in "DATABASES" dictionary

    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'dns_db',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'HOST': 'localhost',
                'PORT': '5432'
            }
        }

Few more settings are required in the same file regarding Celery, Elasticsearch and Email. These settings can be done at the end of the file

    CELERY_RESULT_BACKEND = 'dns-db'
    CELERY_CACHE_BACKEND = 'django-cache'

	EMAIL_HOST = 'abc.org'
	EMAIL_PORT = 123
	EMAIL_HOST_USER = 'abc@xyz.org'
	EMAIL_HOST_PASSWORD = 'password'
	EMAIL_USE_TLS = False
	EMAIL_USE_SSL = True

	result_backend = 'rpc://'
	result_persistent = False

	CACHE = {
	    'default': {
	        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
	        'LOCATION': 'cachedb'
	    }
	}

	ELASTICSEARCH_DSL={
	    'default': {
	        'hosts': 'http://xxx.xxx.xxx.xxx:9200'
	    },
	}

	try:
	    with open('config.yml', 'r') as yaml_file:
	        global_config = yaml.safe_load(yaml_file)
	except Exception as e:
	    sys.exit(1)

	conf = global_config['global']

To perform DB migrations 
```bash
python manage.py makemigrations
```
To migrate the DB
```bash
python manage.py migrate
```
To create super users
```bash
python manage.py createsuperuser
```
To create and link Elasticsearch indices with Django Models
```bash
python manage.py search_index --rebuild
```
To start the server
```bash
python manage.py runserver 
```
Now we need to establish 12 Celery workers with 12 dedicated queues.

One default queue with default worker
```bash
celery -A device_notification_subsystem worker -l info -n worker@dns
```
Ten queues are required for bulk SMS campaigns. Queue names must be same as mentioned below. Worker names & Concurrences can vary as per your design. 
```bash
1. celery -A device_notification_subsystem worker -l info -Q que1 -n worker1@dns -c 1
2. celery -A device_notification_subsystem worker -l info -Q que2 -n worker2@dns -c 1
3. celery -A device_notification_subsystem worker -l info -Q que3 -n worker3@dns -c 1
4. celery -A device_notification_subsystem worker -l info -Q que4 -n worker4@dns -c 1
5. celery -A device_notification_subsystem worker -l info -Q que5 -n worker5@dns -c 1
6. celery -A device_notification_subsystem worker -l info -Q que6 -n worker6@dns -c 1
7. celery -A device_notification_subsystem worker -l info -Q que7 -n worker7@dns -c 1
8. celery -A device_notification_subsystem worker -l info -Q que8 -n worker8@dns -c 1
9. celery -A device_notification_subsystem worker -l info -Q que9 -n worker9@dns -c 1
10. celery -A device_notification_subsystem worker -l info -Q que10 -n worker10@dns -c 1
```
One more queue is required for email campaigns
```bash
celery -A device_notification_subsystem worker -l info -Q email_que -n emailworker@dns -c 1
```

### CLI Commands
Two CLI commands are configured to update two Django models. They can also be run as Crob Jobs.

To update UniqueMsisdn Model
```bash
python manage.py update_unique_msisdns
```
to update UniqueEmail Model
```bash
python manage.py update_unique_emails
```
