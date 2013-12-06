
COPY line (operator_id, publiccode, name) TO '/tmp/lines.csv' WITH CSV HEADER;
COPY stoppoint (operator_id, name, latitude, longitude) TO '/tmp/stops.csv' WITH CSV HEADER;
COPY (SELECT 
j.privatecode as journey_id,
p_pt.pointorder as stop_sequence,
s_pt.operator_id as userstopcode,
departuretime+totaldrivetime as arrival_time,
departuretime+totaldrivetime+stopwaittime as departure_time,
iswaitpoint as timepoint
FROM servicejourney as j JOIN journeypattern as p on (j.journeypatternref = p.id)
                         JOIN pointinjourneypattern as p_pt on (p_pt.journeypatternref = p.id)
                         JOIN pointintimedemandgroup as t_pt on (j.timedemandgroupref = t_pt.timedemandgroupref AND p_pt.pointorder = t_pt.pointorder)
                         JOIN scheduledstoppoint as s_pt ON (s_pt.id = pointref)
WHERE j.privatecode like 'HTM:%'
ORDER BY journey_id, stop_sequence
) TO '/tmp/journey_stops.csv' WITH CSV HEADER;

COPY (SELECT privatecode, validdate
FROM servicejourney 
JOIN availabilityconditionday USING (availabilityconditionref) 
WHERE privatecode like 'HTM:%' and isavailable = true and validdate > 'yesterday')
TO '/tmp/journey_dates.csv' WITH CSV HEADER;