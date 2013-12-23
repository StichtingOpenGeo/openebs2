\COPY line (operator_id, publiccode, name) TO '/tmp/openebs_lines.csv' WITH CSV HEADER;
\COPY stoppoint (operator_id, name, latitude, longitude) TO '/tmp/openebs_stops.csv' WITH CSV HEADER;
COPY (SELECT DISTINCT j.privatecode as journey_id, j.departuretime as base_departure_time, p.directiontype as direction
 FROM servicejourney as j JOIN journeypattern as p on (j.journeypatternref = p.id)
 WHERE j.privatecode like 'HTM:%' ORDER BY direction, journey_id) TO '/tmp/openebs_journeys.csv' WITH CSV HEADER;
\COPY (
SELECT privatecode, validdate
FROM servicejourney
JOIN availabilityconditionday USING (availabilityconditionref)
WHERE privatecode like 'HTM:%' and isavailable = true and validdate >= 'yesterday'
ORDER BY privatecode)
TO '/tmp/openebs_journey_dates.csv' WITH CSV HEADER;