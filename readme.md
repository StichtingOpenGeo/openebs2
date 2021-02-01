OpenEBS
=======

Tool for posting KV15 messages

*Requirements*
- PostgreSQL (several SQL scripts that use specific functionality
- Postgis 2.0 (for map functions)
- Python 2.7 (not tested on 3.x)
- Dependencies in requirements.txt

*How to install*

1. Add a PostgreSQL database and enter the connection details in ```openebs2/local_settings.py```. Also specify any overrides of settings.py you'd like

1. In your new database, execute the command "CREATE EXTENSION postgis"

1. Run ```python manage.py syncdb```

1. Run ```python manage.py migrate```

~~1. Run ```python manage.py import_json lines/``` where lines is a folder containing JSON output of the script ```kv1/scripts/patternizer.py``` (run on RID)~~

1. Run ```python manage.py import_html lines/``` where lines is a folder containing HTML line data

1. Since there's a lot of them, we import some data directly into the database. Use the steps in ```kv1/scripts/import_rid.sql``` to do so

1. Run ```python manage.py runserver``` enter the admin by the browser http://127.0.0.1:8000/admin/auth/user/1/ and set the agency for the first user.


*Upgrade*
Tip: to upgrade permissions do ```python manage.py syncdb --all```

Additional functionality
-----------------------

*Batch cancel & restore of trips*
To facilitate batch cancelling of trips, console commands for processing files of the following format: (including a header row)
````
privatecode,validdate
ARR:1011:1001,2018-01-04
````
Each trip in the file will be searched for and if found, cancelled.

To use:
1. Login to the server and make sure you are using the correct python (openebs virtualenv must be activated)

1. Setup the file with trips you need

1. Run `python manage.py batch_cancel file.csv`

Additionally, cancelled trips may be recovered from a file of the same format. Each trip in the file will be searched for and if found, restored.
Use the command `python manage.py batch_restore file.csv`
