CREATE TABLE IF NOT EXISTS tmp_js (privatecode character varying(255), dep_time integer, journey_duration integer, direction integer, availability integer);
DELETE FROM tmp_js;
\COPY tmp_js FROM '/tmp/rid/openebs_journeys.csv' CSV HEADER;
/* Insert new trips */
INSERT INTO kv1_kv1journey (dataownercode, line_id, journeynumber, scheduleref, direction, departuretime, arrivaltime)
SELECT split_part(privatecode,':',1), l.id, cast(split_part(privatecode,':',3) as integer), availability, direction, dep_time, dep_time+journey_duration
FROM tmp_js, kv1_kv1line l
WHERE l.dataownercode = split_part(privatecode,':',1) AND l.lineplanningnumber = split_part(privatecode,':',2)
AND NOT EXISTS (
    SELECT id FROM kv1_kv1journey WHERE dataownercode=split_part(privatecode,':',1) AND line_id=l.id AND journeynumber=cast(split_part(privatecode,':',3) as integer) AND scheduleref=availability
);
/* Note: need to still delete old trips (related to archiving) */

/* Insert journey dates - we don't link to these so just delete and reinsert */
CREATE TABLE IF NOT EXISTS tmp_jd (jid text, availability integer, d date);
DELETE FROM tmp_jd;
\copy tmp_jd from '/tmp/rid/openebs_journey_dates.csv' csv header;
delete from kv1_kv1journeydate ;
insert into kv1_kv1journeydate (journey_id, date)
select kv1_kv1journey.id, d from tmp_jd, kv1_kv1journey, kv1_kv1line
where jid = concat_ws(':', kv1_kv1journey.dataownercode, lineplanningnumber, journeynumber) and kv1_kv1journey.scheduleref = availability
and kv1_kv1journey.line_id = kv1_kv1line.id;
