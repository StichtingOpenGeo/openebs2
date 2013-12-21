OpenEBS
=======

Tool for posting KV15 messages

*Requirements*
- PostgreSQL
- Postgis 2.0
- Dependencies in requirements.txt

*How to install*

1. Add a PostgreSQL database and enter the connection details in ```openebs2/local_settings.py```

1. In your new database, execute the command "CREATE EXTENSION postgis"

1. Run ```python manage.py syncdb```

1. Run ```python manage.py migrate```

1. Run ```python manage.py import_html lines/``` where lines is a folder containing HTML-based line data from OpenEBS1

1. Run ```python manage.py import_rid path_to_export/``` where path_to_export/ contains the CSV files exported from RID with the file kv1\export_rid.sql

1. Run ```python manage.py runserver``` enter the admin by the browser http://127.0.0.1:8000/admin/auth/user/1/ and set the agency for the first user.


*Upgrade*
Tip: to upgrade permissions do ./manage.py syncdb --all
