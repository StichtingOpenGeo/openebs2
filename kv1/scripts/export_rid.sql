﻿\COPY (SELECT operator_id, publiccode, name FROM line WHERE split_part(operator_id,':',1) in ('HTM','VTN','ARR','EBS', 'CXX', 'RET', 'GVB', 'QBUZZ', 'SYNTUS', 'WSF')) TO '/tmp/openebs_lines.csv' WITH CSV HEADER;
\COPY (SELECT operator_id, name, latitude, longitude, timingpointcode FROM stoppoint JOIN usertimingpoint u on operator_id = dataownercode||':'||userstopcode WHERE split_part(operator_id,':',1) in ('HTM','VTN','ARR','EBS', 'CXX', 'RET', 'GVB', 'QBUZZ', 'SYNTUS')) TO '/tmp/openebs_stops.csv' WITH CSV HEADER;
\COPY (SELECT DISTINCT ON (availabilityconditionref,j.privatecode) j.privatecode as journey_id, j.departuretime as base_departure_time, p.directiontype as direction, j.availabilityconditionref FROM servicejourney as j JOIN journeypattern as p on (j.journeypatternref = p.id) WHERE split_part(j.privatecode,':',1) in ('HTM','VTN','ARR','EBS', 'CXX', 'RET', 'GVB', 'QBUZZ', 'SYNTUS')) TO '/tmp/openebs_journeys.csv' WITH CSV HEADER;
\COPY (SELECT DISTINCT ON (privatecode, availabilityconditionref, validdate) privatecode, availabilityconditionref, validdate FROM servicejourney JOIN availabilityconditionday USING (availabilityconditionref) WHERE split_part(privatecode,':',1) in ('HTM','VTN','ARR','EBS', 'CXX', 'RET', 'GVB', 'QBUZZ', 'SYNTUS') and isavailable = true and validdate >= 'yesterday' and validdate <= LOCALTIMESTAMP + INTERVAL '1 week') TO '/tmp/openebs_journey_dates.csv' WITH CSV HEADER;
