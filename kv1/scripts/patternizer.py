"""
Make line patterns out of line stop patterns (there & back again)
Runs straight on the RID database

This version adjusted to use _ as seperator instead of | because that's what OpenEBS expects
The output is HTML files - they're used by OpenEBS1 and considered legacy. Issue exists to move away from it

"""

import psycopg2
import psycopg2.extras

def indexofterugorder(stops,terugorder):
    for i in range(len(stops)):
        if stops[i]['terugorder'] is None:
            continue
        if stops[i]['terugorder']-terugorder == -1:
            return i
    for i in range(len(stops)-1):
        if stops[i]['terugorder'] < terugorder and  (stops[i+1]['terugorder'] is None or stops[i+1]['terugorder'] >= terugorder):
            return i
    for stop in stops:
        print stop
    raise Exception('test')
    if terugorder <= 1:
        return len(stops)-1
    else:
        return 0

conn = psycopg2.connect("dbname='ridprod'")
cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
cur.execute("""
SELECT l.operator_id FROM line as l JOIN operator as o ON (operatorref = o.id) WHERE o.operator_id not like 'IFF:%' and l.operator_id not like
'AVV:%'
""")
rows = cur.fetchall()

for row in rows:
    operator_id = row['operator_id']
    key = operator_id.replace(':','_')
    print key
    f = open(key+'.html','w')
    f.write("""
<table class="lijn">
  <tr>
    <th class="left">
      <button class="btn btn-success btn-mini" onclick="patternSelect(0);">
        <i class="icon-arrow-down icon-white">
      </i>
    </th>
      <th>
        <button class="btn btn-success btn-mini" onclick="patternSelect(2);">
          <i class="icon-resize-horizontal icon-white">
        </i>
      </th>
        <th class="right">
          <button class="btn btn-success btn-mini" onclick="patternSelect(1);">
            <i class="icon-arrow-up icon-white">
          </i>
        </th>
      </tr>
""")
    cur.execute("""
SELECT
heen.pointorder as heenorder,
terug.pointorder as terugorder,
heen.stoparearef as heenstoparearef,
replace(heen.operator_id,':','_') as heenstopid,
heen.name as heennaam,
terug.stoparearef as terugstopararef,
replace(terug.operator_id,':','_') as terugstopid,
terug.name as terugnaam
FROM
(SELECT
line_id,sp.stoparearef,pointorder,sp.operator_id,sp.name, journeypatterns,min(pointorder) OVER (PARTITION BY line_id) as minpointorder
FROM
(SELECT
l.operator_id as line_id,sp.operator_id,max(jpt.pointorder) as pointorder,array_agg(j.id) as journeypatterns
FROM line as l JOIN route as r ON (r.lineref = l.id)
               JOIN journeypattern as j ON (j.routeref = r.id)
               JOIN pointinjourneypattern as jpt ON (jpt.journeypatternref = j.id)
               JOIN scheduledstoppoint AS sp ON (jpt.pointref = sp.id)
WHERE l.operator_id = %s and j.directiontype = '1'
GROUP BY line_id,sp.operator_id
ORDER BY pointorder) as y JOIN stoppoint AS sp USING (operator_id)
ORDER BY pointorder) as heen
FULL OUTER JOIN
(SELECT
line_id,sp.stoparearef,pointorder,sp.operator_id,sp.name, journeypatterns,max(pointorder) OVER (PARTITION BY line_id) as maxpointorder
FROM (
SELECT
l.operator_id as line_id,sp.operator_id,max(jpt.pointorder) as pointorder,array_agg(j.id) as journeypatterns
FROM line as l JOIN route as r ON (r.lineref = l.id)
               JOIN journeypattern as j ON (j.routeref = r.id)
               JOIN pointinjourneypattern as jpt ON (jpt.journeypatternref = j.id)
               JOIN scheduledstoppoint AS sp ON (jpt.pointref = sp.id)
WHERE l.operator_id = %s and j.directiontype = '2'
GROUP BY line_id,sp.operator_id
ORDER BY pointorder DESC) as y JOIN stoppoint AS sp USING (operator_id)
ORDER BY pointorder DESC) as terug ON (heen.stoparearef = terug.stoparearef)""",[operator_id]*2)
    stops = list(cur.fetchall())
    geen_heen = True
    for stop in stops:
        if stop['heenorder'] is not None:
            geen_heen = False
    if geen_heen:
        stops = sorted(stops, key=lambda k: k['terugorder'])
    else:
        count_emptystops = 0
        first_heenempty = -1
        for i in range(len(stops)):
            if stops[i]['heenorder'] is None:
                count_emptystops += 1
                if first_heenempty == -1:
                    first_heenempty = i
        if count_emptystops == 1 and stops[-1]['terugorder'] == 1:
            pass
        elif count_emptystops > 0:
            stops[first_heenempty:] = sorted(stops[first_heenempty:], key=lambda k: k['terugorder'], reverse=True)
            reverse_sequental = True
            last_pointorder = -1
            for stop in reversed(stops):
                if stop['terugorder'] < last_pointorder:
                    reverse_sequental = False
                last_pointorder = stop['terugorder']
            if not reverse_sequental:
                while stops[-1]['heenorder'] is None:
                    i = indexofterugorder(stops,stops[-1]['terugorder'])
                    stops.insert(i,stops[-1])
                    del(stops[-1])
    for stop in stops:
        if stop['heenorder'] is None and stop['terugorder'] is not None:
            f.write("""
<tr><td></td><td></td><td class="right">
     <button type="button" onclick="patternSelectStop(this)" class="btn btn-primary btn-mini btn-stop"
         id="%(terugstopid)s">%(terugnaam)s</button></td></tr>\n""" % stop)
        elif stop['heenorder'] is not None and stop['terugorder'] is None:
            f.write("""
<tr><td class="left">
    <button type="button" class="btn btn-primary btn-mini btn-stop" onclick="patternSelectStop(this)" id="%(heenstopid)s">%(heennaam)s
    </button>
</td><td></td><td></td></tr>\n""" % stop)
        else:
            f.write("""
<tr>
    <td class="left">
       <button type="button" onclick="patternSelectStop(this)" class="btn btn-primary btn-mini btn-stop" id="%(heenstopid)s">%(heennaam)s</button></td><td><button class="btn btn-success btn-mini" onclick="patternSelectRow(this);"><i class="icon-resize-horizontal icon-white"></i></td>
    <td class="right">
       <button type="button" onclick="patternSelectStop(this)" class="btn btn-primary btn-mini btn-stop" id="%(terugstopid)s">%(terugnaam)s</button>
    </td></tr>\n""" %stop)
    f.write("\n</table>")
    f.close()