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


*Upgrade*
Tip: to upgrade permissions do ./manage.py syncdb --all