"""
patternizer5 -- render per-line stop patterns to HTML tables.

Fixed 2026-09-06 (NeTEx migration broke the split_part offsets; produced 0 files):
  - operator_id is NL:ARR:... -> operator is segment 2, not 1 (WHERE matched nothing)
  - dataownercode now from operator_id; line.bison_id is NULL for NS
  - stoppoint.bison_id is still 2-part -> segment 1, coalesced (NULL||'|'||x is NULL)
  - mkdir OUTDIR; try/except per operator; close files on the single-direction paths
  - directiontype no longer assumed to be 1/2; stopline() warns instead of raising
  - py3: dropped codecs, unshadowed `list`, utf-8 on output files
  - WPD/ZTM/MLN kept in the list but flagged dormant: 0 rows is not an error

Usage:  python3 patternizer5.py [-v] [OPERATOR ...]
"""

import psycopg2
import psycopg2.extras
import operator
import os
import sys
import traceback
from collections import OrderedDict

OUTDIR = '/tmp/openebs_lines'
VERBOSE = False


def log(msg):
    """Per-line progress detail; only shown with -v."""
    if VERBOSE:
        print(msg, flush=True)


def warn(msg):
    """Anomalies; always shown."""
    print(msg, flush=True)


STATS = {'files': 0, 'collisions': 0, 'empty_pattern': [], 'errors': []}

def exists(rows, key, value):
    for row in rows:
        if key in row and row[key] == value:
            return True
    return False

def position(rows, key, value):
    i = 0
    for row in rows:
        if key in row and row[key] == value:
            return i
        i += 1
    return -1

def order(rows):
    for s in rows:
        if s['linkorder'] == 1:
            pos = position(rows, 'userstopcodeend', s['userstopcodebegin'])
            for x in rows:
                if set(x['patterncodes']) == set(s['patterncodes']):
                    x['linkorder'] += pos
    rows.sort(key=operator.itemgetter('linkorder'))


def filter_noboarding(rows):
    new_list = []
    o = 0
    i = 0
    p = None
    while i < len(rows):
        s = rows[i]
        if s['pstop']:
            # Laatste nuttige van de lijst kunnen we negeren, omdat nameend dan al bij de vorige zit
            if i == (len(rows) - 1) and s['nameend'].startswith('KAR'):
                i += 1

            elif i == (len(rows) - 1) or rows[i + 1]['pstop']:
                t = dict(s)
                o += 1
                t['linkorder'] = o
                new_list.append(t)
                i += 1
            else:
                while i < (len(rows) - 1):
                    i += 1
                    n = rows[i]
                    if n['pstop']:
                        o += 1
                        new_list.append({'direction': s['direction'], 'dataownercode': s['dataownercode'], 'lineplanningnumber': s['lineplanningnumber'], 'userstopcodebegin': s['userstopcodebegin'], 'namebegin': s['namebegin'], 'userstopcodeend': n['userstopcodebegin'], 'nameend': n['namebegin'], 'linkorder': o, 'destcodes': s['destcodes'], 'patterncodes': s['patterncodes'], 'pstop': n['pstop']})
                        break

        # Omdat we van de "naar" halte geen timingpoint status hebben, is dit nogal een hack
        elif i == (len(rows) - 1) and not s['nameend'].startswith('KAR'):
            n = s
            s = p
            new_list.append({'direction': s['direction'], 'dataownercode': s['dataownercode'],
                             'lineplanningnumber': s['lineplanningnumber'], 'userstopcodebegin': s['userstopcodebegin'],
                             'namebegin': s['namebegin'], 'userstopcodeend': n['userstopcodeend'],
                             'nameend': n['nameend'], 'linkorder': o, 'destcodes': s['destcodes'],
                             'patterncodes': s['patterncodes'], 'pstop': s['pstop']})
            i += 1
        else:
            i += 1

        p = s

    return new_list

dummies = set([])

def stopline(heen,weer,namekey_heen,codekey_heen,namekey_weer=None,codekey_weer=None):
    if heen is not None:
        if heen['dataownercode']+'|'+heen[codekey_heen] in dummies:
            warn('    !! stopline() called with dummy heen: %s|%s (%s)'
                  % (heen['dataownercode'], heen[codekey_heen], codekey_heen))
            return ''
    if weer is not None and codekey_weer in weer:
        if weer['dataownercode']+'|'+weer[codekey_weer] in dummies:
            warn('    !! stopline() called with dummy weer: %s|%s (%s)'
                  % (weer['dataownercode'], weer[codekey_weer], codekey_weer))
            return ''
    if namekey_weer is None:
        namekey_weer = namekey_heen
    if codekey_weer is None:
        codekey_weer = codekey_heen
    if heen is not None and weer is not None:
        return '<tr><td class="left"><button type="button" onclick="patternSelectStop(this)" class="btn btn-primary btn-mini btn-stop" id="%(userstopcode1)s">%(name1)s</button></td><td><button class="btn btn-success btn-mini" onclick="patternSelectRow(this);"><i class="icon-resize-horizontal icon-white"></i></td><td class="right"><button type="button" onclick="patternSelectStop(this)" class="btn btn-primary btn-mini btn-stop" id="%(userstopcode2)s">%(name2)s</button></td></tr>\n' % {'userstopcode1' : heen['dataownercode']+'_'+heen[codekey_heen], 'name1': heen[namekey_heen], 'userstopcode2' : weer['dataownercode']+'_'+weer[codekey_weer], 'name2' : weer[namekey_weer]}
    elif heen is not None and weer is None:
        return '<tr><td class="left"><button type="button" class="btn btn-primary btn-mini btn-stop" onclick="patternSelectStop(this)" id="%(userstopcode1)s">%(name1)s</button></td><td></td><td></td></tr>\n'%{'userstopcode1' : heen['dataownercode']+'_'+heen[codekey_heen], 'name1' : heen[namekey_heen]}
    elif heen is None and weer is not None:
        return '<tr><td></td><td></td><td class="right"><button type="button" onclick="patternSelectStop(this)" class="btn btn-primary btn-mini btn-stop" id="%(userstopcode2)s">%(name2)s</button></td></tr>\n'%{'userstopcode2' : weer['dataownercode']+'_'+weer[codekey_weer], 'name2' : weer[namekey_weer]}
    # both None: original fell off the end and returned None -> f.write(None) TypeError
    warn('    !! stopline(None, None) -- nothing to write')
    return ''

def stopkey(row,stopkey):
    return row['dataownercode'] + '|' + row[stopkey]

class StopAreaMap(dict):
    """Returns None for unknown keys instead of raising, and counts the misses."""
    def __init__(self):
        super().__init__()
        self.misses = 0
        self.sample = []
    def __missing__(self, key):
        self.misses += 1
        if len(self.sample) < 5:
            self.sample.append(key)
        return None

def stoparea_equals(stoparea1,stoparea2):
    if stoparea1 is None or stoparea2 is None:
        return False
    return (stoparea1 == stoparea2)

def patternize(dataownercode):
    print('=== %s ===' % dataownercode, flush=True)
    stoparea = StopAreaMap()
    conn = psycopg2.connect("host='127.0.0.1' dbname='ridprod' user='thomas'")#"dbname='kv1%s'" % dataownercode.lower())
    log('  [db] connected')
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("select split_part(coalesce(bison_id,''),':',1) || '|' || privatecode as dummy from stoppoint where (id not in (SELECT DISTINCT id from pointinjourneypattern WHERE forboarding or foralighting))")
    for row in cur:
        dummies.add(row['dummy'])
    if len(dummies) == 0:
        cur.execute("select count(*) as n from stoppoint where (id not in (SELECT DISTINCT id from pointinjourneypattern WHERE forboarding or foralighting))")
        n = cur.fetchone()['n']
        log('  [db] dummies loaded: 0  (raw count of non-boarding stoppoints = %d)' % n)
        if n > 0:
            warn('  !! rows exist but key expression produced none -- check stoppoint.bison_id format')
    else:
        log('  [db] dummies loaded: %d' % len(dummies))
    cur.execute("select split_part(coalesce(s.bison_id,''),':',1) || '|' || s.privatecode as id,a.bison_id as userstopareacode, s.bison_id as raw from stoppoint s LEFT JOIN stoparea a ON (a.id = stoparearef)")
    nullids = 0
    for row in cur:
        if not row['raw']:
            nullids += 1
        stoparea[row['id']] = row['userstopareacode'] 
    log('  [db] stopareas loaded: %d (%d had NULL/empty bison_id -> key has no operator prefix)'
          % (len(stoparea), nullids))
    cur.execute("""
SELECT
jp.directiontype as direction,
split_part(jp.operator_id,':',2) as dataownercode,
l.privatecode as lineplanningnumber,
spf.privatecode as userstopcodebegin,
spf.name as namebegin,
spt.privatecode as userstopcodeend,
spt.name as nameend,
max(pointorder) as linkorder,
array_agg(distinct coalesce(dp.privatecode,dpvj.privatecode)) as destcodes,
array_agg(distinct jp.operator_id) as patterncodes,
jpp.forboarding or jpp.foralighting as pstop
FROM journeypattern jp JOIN route r ON (r.id = routeref)
                       JOIN line l ON (l.id = lineref)
                       JOIN pointinjourneypattern jpp ON (jp.id = journeypatternref)
                       JOIN stoppoint spf ON (spf.id = pointref)
                       JOIN stoppoint spt ON (spt.id = onwardpointref)
                       LEFT JOIN destinationdisplay dpvj ON (dpvj.id = jp.destinationdisplayref)
                       LEFT JOIN destinationdisplay dp ON (dp.id = jpp.destinationdisplayref)
WHERE spf.id != spt.id AND split_part(jp.operator_id,':',2) = %s AND deadrun = FALSE
GROUP BY lineplanningnumber,direction,dataownercode,userstopcodebegin,namebegin,userstopcodeend,nameend,jpp.forboarding or jpp.foralighting
order by lineplanningnumber,direction,linkorder;
""",[dataownercode])
    pattern = {}
    rows = cur.fetchall()
    log('  [db] main query returned %d rows for %r' % (len(rows), dataownercode))
    if len(rows) == 0:
        if dataownercode in DORMANT:
            log('  (0 rows -- %s is dormant, expected)' % dataownercode)
        else:
            warn('  !! ZERO ROWS -> no files written for %s.' % dataownercode)
            cur.execute("select distinct split_part(operator_id,':',2) as oc from journeypattern where deadrun = FALSE and split_part(operator_id,':',2) !~ '^[0-9]+$' order by 1")
            warn('  !! named operator codes present: %s' % [r['oc'] for r in cur.fetchall()])
        STATS['empty_pattern'].append(dataownercode)
    for row in rows:
        key = '_'.join([row['dataownercode'],row['lineplanningnumber']])
        if key not in pattern:
            pattern[key] = {row['direction'] : []}
        if row['direction'] not in pattern[key]:
            pattern[key][row['direction']] = []
        pattern[key][row['direction']].append(row)

    log('  [pattern] %d line keys built' % len(pattern))
    if not os.path.isdir(OUTDIR):
        warn('  !! output dir %s did not exist -- creating it' % OUTDIR)
        os.makedirs(OUTDIR, exist_ok=True)

    written_here = 0
    for key,item in pattern.items():
        before = {k: len(v) for k, v in item.items()}
        for k in list(item.keys()):
            item[k] = filter_noboarding(item[k])
        after = {k: len(v) for k, v in item.items()}
        log('  [key] %-16s directions=%s stops before=%s after filter_noboarding=%s'
              % (key, sorted(item.keys()), before, after))
        for k, n in after.items():
            if n == 0 and before[k] > 0:
                warn('    !! direction %s emptied by filter_noboarding (no pstop rows?)' % k)
        path = os.path.join(OUTDIR, key + '.html')
        if os.path.exists(path):
            warn('    !! COLLISION: %s already exists, overwriting' % path)
            STATS['collisions'] += 1

        # directiontype is not guaranteed to be 1/2 (WPD has 0). The branches below
        # assume keys 1 and 2 exist, so remap anything else onto them.
        extra = [d for d in item.keys() if d not in (1, 2)]
        if extra:
            warn('    !! non-standard directiontype(s) %s on %s' % (extra, key))
            for d in extra:
                if 1 not in item:
                    item[1] = item.pop(d)
                    warn('       remapped direction %s -> 1' % d)
                elif 2 not in item:
                    item[2] = item.pop(d)
                    warn('       remapped direction %s -> 2' % d)
                else:
                    dropped = item.pop(d)
                    warn('       DROPPED direction %s (%d stops, 1 and 2 both taken)'
                          % (d, len(dropped)))
        if not item:
            warn('    !! no usable directions, skipping %s' % key)
            continue

        f = open(path, 'w', encoding='utf-8')
        STATS['files'] += 1
        written_here += 1
        log('    -> opened %s' % path)
        f.write('<table class="lijn"><tr><th class="left"><button class="btn btn-success btn-mini" onclick="patternSelect(0);"><i class="icon-arrow-down icon-white"></i></th><th><button class="btn btn-success btn-mini" onclick="patternSelect(2);"><i class="icon-resize-horizontal icon-white"></i></th><th class="right"><button class="btn btn-success btn-mini" onclick="patternSelect(1);"><i class="icon-arrow-up icon-white"></i></th></tr>')
        if 2 not in item:
            log('    (one-direction line, only direction 1)')
            order(item[1])
            stop = None
            for stop in item[1]:
                if stopkey(stop,'userstopcodebegin') not in dummies:
                    f.write(stopline(stop,None,'namebegin','userstopcodebegin'))
            if stop is not None:
                f.write(stopline(stop,None,'nameend','userstopcodeend'))
            else:
                warn('    !! item[1] empty, nothing written')
            f.write('</table>')
            f.close()
            continue
        if 1 not in item:
            log('    (one-direction line, only direction 2)')
            order(item[2])
            stop = None
            for stop in reversed(item[2]):
                if stopkey(stop,'userstopcodeend') not in dummies:
                    f.write(stopline(stop,None,'nameend','userstopcodeend'))
            if stop is not None:
                f.write(stopline(stop,None,'namebegin','userstopcodebegin'))
            else:
                warn('    !! item[2] empty, nothing written')
            f.write('</table>')
            f.close()
            continue
        order(item[1])
        order(item[2])
        item[2] = list(reversed(item[2])) #userstopcodebegin/end wordt niet! omgedraaid.

        queue = OrderedDict()

        i,j = 0,0
        while i < len(item[1]) or j < len(item[2]):
            if i < len(item[1]) and stopkey(item[1][i],'userstopcodebegin') in dummies:
                i += 1
            if j < len(item[2]) and stopkey(item[2][j],'userstopcodeend') in dummies:
                j += 1
            inlen = (i < len(item[1]) and j < len(item[2]))
            if i < len(item[1]) or j < len(item[2]):
                if inlen:
                    stopkey_heen = stopkey(item[1][i],'userstopcodebegin')
                    stoparea_heen = stoparea[stopkey_heen]
                    stopkey_weer = stopkey(item[2][j],'userstopcodeend')
                    stoparea_weer = stoparea[stopkey_weer]
                if inlen and (item[1][i]['namebegin'] == item[2][j]['nameend'] or stoparea_equals(stoparea_heen,stoparea_weer)): #Haltenamen gelijk
                    if stopkey(item[1][i],'userstopcodebegin') not in dummies and stopkey(item[2][j],'userstopcodeend') not in dummies:
                        if i == 0 or stopkey(item[1][i],'userstopcodebegin') != stopkey(item[1][i-1],'userstopcodebegin'):
                            f.write(stopline(item[1][i],item[2][j],'namebegin','userstopcodebegin',namekey_weer='nameend',codekey_weer='userstopcodeend'))

                            if (i+1) < len(item[1]) and stopkey(item[1][i],'userstopcodeend') != stopkey(item[1][i+1],'userstopcodebegin'):
                                # append until done with this stoparea and if we do not see this item before that
                                queue[item[1][i]['userstopcodeend']] = stopline(item[1][i], item[2][j], 'nameend', 'userstopcodeend',
                                                 namekey_weer='namebegin', codekey_weer='userstopcodebegin')
                    i += 1
                    j += 1
                elif not inlen and i < len(item[1]): #Een van de patronen is afgewerkt
                    if stopkey(item[1][i],'userstopcodebegin') not in dummies:
                        f.write(stopline(item[1][i],None,'namebegin','userstopcodebegin'))
                    i += 1
                elif not inlen and j < len(item[2]):
                    if stopkey(item[2][j],'userstopcodeend') not in dummies:
                        f.write(stopline(None,item[2][j],'nameend','userstopcodeend'))
                    j += 1
                else:
                    pos = position(item[2][j:],'nameend',item[1][i]['namebegin'])
                    if i == len(item[1]) -1 or j == len(item[2]) - 1:
                        pos = max(pos,position(item[2][j:],'namebegin',item[1][i]['nameend']))
                    if pos == -1: #Heen bevat dit patroon niet, print halte in heen patroon
                        if stopkey(item[1][i],'userstopcodebegin') not in dummies:
                            f.write(stopline(item[1][i],None,'namebegin','userstopcodebegin'))
                        i += 1
                    else:    #Weer bevat dit patroon niet, print halte in weer patroon
                        if stopkey(item[2][j],'userstopcodeend') not in dummies:
                            f.write(stopline(None,item[2][j],'nameend','userstopcodeend'))
                        j += 1

            f.flush()

            if len(queue) > 0:
                if i < len(item[1]) or j < len(item[2]):
                    if (i < len(item[1]) and item[1][i]['userstopcodebegin'] in queue):
                        queue.clear()
                    
                    else:
                        heen = False
                        terug = False
                        if i < len(item[1]):
                            heen = True
                            stopkey_heen = stopkey(item[1][i],'userstopcodebegin')
                            stoparea_heen = stoparea[stopkey_heen]
                            stopkey_prev_heen = stopkey(item[1][i-1],'userstopcodebegin')
                            stoparea_prev_heen = stoparea[stopkey_prev_heen]
                        if j < len(item[2]):
                            terug = True
                            stopkey_weer = stopkey(item[2][j],'userstopcodeend')
                            stoparea_weer = stoparea[stopkey_weer]
                            stopkey_prev_weer = stopkey(item[2][j-1],'userstopcodeend')
                            stoparea_prev_weer = stoparea[stopkey_prev_weer]
    
                        if (heen and not stoparea_equals(stoparea_heen,stoparea_prev_heen)) or (terug and not stoparea_equals(stoparea_weer,stoparea_prev_weer)):
                            for q in queue.values():
                                f.write(q)
                            queue.clear()
    
                else:
                    for q in queue.values():
                        f.write(q)
                    queue.clear()

            f.flush()

            if i == len(item[1]) or j == len(item[2]): #niet elif want je wilt in de loop al einde kunnen afhandelen
               if i == len(item[1]) and j == len(item[2]): #case beide patronen zijn aan laatste toe
                   i += 1
                   j += 1
                   i1nameend = item[1][-1]['nameend']
                   i2namebegin = item[2][-1]['namebegin']
                   stopkey_heen = stopkey(item[1][-1], 'userstopcodebegin')
                   stoparea_heen = stoparea[stopkey_heen]
                   stopkey_weer = stopkey(item[2][-1], 'userstopcodeend')
                   stoparea_weer = stoparea[stopkey_weer]

                   if item[1][-1]['nameend'] == item[2][-1]['namebegin'] or stoparea_equals(stoparea_heen, stoparea_weer):
                       f.write(stopline(item[1][-1],item[2][-1],'nameend','userstopcodeend',namekey_weer='namebegin',codekey_weer='userstopcodebegin'))
                   else:
                       f.write(stopline(item[1][-1],None,'nameend','userstopcodeend'))
                       f.write(stopline(None,item[2][-1],'namebegin','userstopcodebegin'))
               if i == len(item[1]):
                   j -= 1
                   remaining = [x['namebegin'] for x in item[2][j:]]
                   remaining.append(item[2][-1]['nameend'])
                   if item[1][-1]['nameend'] in remaining:
                       while j < len(item[2]):
                           if item[1][-1]['nameend'] == item[2][j]['namebegin']:
                               f.write(stopline(item[1][-1], item[2][j], 'nameend', 'userstopcodeend',
                                                namekey_weer='namebegin', codekey_weer='userstopcodebegin'))
                           else:
                               f.write(stopline(None, item[2][j], 'namebegin', 'userstopcodebegin'))
                           j += 1
                   else:
                       f.write(stopline(item[1][-1],None,'nameend','userstopcodeend'))
                       i += 1
               elif j == len(item[2]):
                   f.flush()
                   i -= 1
                   remaining = [x['nameend'] for x in item[1][i:]]
                   remaining.append(item[1][-1]['namebegin'])
                   if item[2][-1]['namebegin'] in remaining:

                       while i < len(item[1]):
                           if item[2][-1]['namebegin'] == item[1][i]['nameend']:
                               f.write(stopline(item[1][i], item[2][-1], 'nameend', 'userstopcodeend',
                                                namekey_weer='namebegin', codekey_weer='userstopcodebegin'))
                           else:
                               f.write(stopline(item[1][i], None, 'nameend', 'userstopcodeend'))
                           i += 1

                           f.flush()
                   else:
                       f.write(stopline(None, item[2][-1], 'namebegin', 'userstopcodebegin'))
                       j += 1
        f.write('</table>')
        f.close()

    print('  %-8s %d rows, %d lines, %d files' % (dataownercode, len(rows), len(pattern), written_here), flush=True)
    if stoparea.misses:
        warn('  !! %d stoparea lookups missed. Sample keys not found: %s' % (stoparea.misses, stoparea.sample))
        warn('  !! (stoppoint.bison_id segment 1 + privatecode does not match dataownercode + privatecode)')


OPERATORS = ['KEOLIS','HTM','ARR','GVB','EBS','RET','CXX','QBUZZ',
             'WSF','TESO','DOEKSEN','OVCN',
             # dormant: absent from the feed as of 2026-09, kept so they are
             # picked up automatically if they return. 0 rows is not an error.
             'WPD','ZTM','MLN']
DORMANT = {'WPD','ZTM','MLN'}

argv = sys.argv[1:]
VERBOSE = bool({'-v', '--verbose'} & set(argv))
args = [a for a in argv if a not in ('-v', '--verbose')]
bad = [a for a in args if a.startswith('-')]
if bad:
    sys.exit('unknown option %s\nusage: %s [-v] [OPERATOR ...]'
             % (bad[0], os.path.basename(sys.argv[0])))
if args:
    OPERATORS = [a.upper() for a in args]

os.makedirs(OUTDIR, exist_ok=True)
print('output dir: %s (writable: %s)' % (OUTDIR, os.access(OUTDIR, os.W_OK)))

for oc in OPERATORS:
    try:
        patternize(oc)
    except Exception as e:
        STATS['errors'].append((oc, repr(e)))
        print('  XX %s FAILED: %r' % (oc, e))
        traceback.print_exc()

print('\n===== SUMMARY =====')
print('files opened:        %d' % STATS['files'])
print('filename collisions: %d' % STATS['collisions'])
written = sorted(os.listdir(OUTDIR)) if os.path.isdir(OUTDIR) else []
print('files now on disk:   %d' % len(written))
nonempty = [w for w in written if os.path.getsize(os.path.join(OUTDIR, w)) > 400]
print('files with content:  %d' % len(nonempty))
unexpected = [o for o in STATS['empty_pattern'] if o not in DORMANT]
print('operators with 0 rows: %s (unexpected: %s)'
      % (STATS['empty_pattern'] or 'none', unexpected or 'none'))
print('operators that errored: %s' % (STATS['errors'] or 'none'))
for w in written[:10]:
    print('   %8d  %s' % (os.path.getsize(os.path.join(OUTDIR, w)), w))
