#!/bin/bash
# A couple of lines and stops for import_rid, so the smoke test has data to show.
set -euo pipefail

dir="$1"
mkdir -p "$dir"

cat > "$dir/openebs_lines.csv" <<'EOF'
bison_id,publiccode,name
HTM:1,1,Scheveningen Noorderstrand - Delft Tanthof
HTM:9,9,Scheveningen Noorderstrand - Den Haag Vrederust
EOF

cat > "$dir/openebs_stops.csv" <<'EOF'
operator_id,name,latitude,longitude,timingpointcode,quaycoderef
HTM:3100,Den Haag Centraal,52.080887,4.324971,31001000,
HTM:3200,Den Haag Hollands Spoor,52.069637,4.322389,31002000,
EOF
