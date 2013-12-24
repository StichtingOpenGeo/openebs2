create table if not exist tmp_jd (jid text, d date);
delete from tmp_jd ;
\copy tmp_jd from '/tmp/rid/openebs_journey_dates.csv' csv header ;
delete from kv1_kv1journeydate ;
insert into kv1_kv1journeydate (journey_id, date) select kv1_kv1journey.id, d from tmp_jd, kv1_kv1journey, kv1_kv1line where jid = kv1_kv1journey.dataownercode||':'||lineplanningnumber||':'||journeynumber and kv1_kv1journey.line_id = kv1_kv1line.id;
