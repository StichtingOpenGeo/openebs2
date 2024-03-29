/* LINE VARIABLES */
var cancelledLines = []; // list of cancelled lines from Ajax
var activeLine = null; // lineplanningnumber of current line
var currentLine = null; // publiclinenumber of current line
var stopLine = null; // line for which the stops are shown
var selectedLines = [];  // list of lineplanningnumbers of selected lines
var lijnList = [];  // list with publiclinenumbers of selected lines
var currentLineMeasures = null;

/* TRIP VARIABLES */
var cancelledJourneys = [];  // list of cancelled trip_ids from Ajax
var shortenedJourneys = [];  // list of shortened trip_ids from Ajax
var selectedTrips = [];  // list of selected trips_ids
var currentTrips = [];  // keeps trip_ids in memory until stop is clicked
var currentTripLabels = [];  // keeps trip_labels in memory until stop is clicked

/* Extra TRIP VARIABLES for 'alle ritten' */
var allTrips = []; // list of dicts with all trip measures of selected lines
var tripSelection = []; // temporary list of all trips of current line

/* STOP VARIABLES */
var selectedStops = []; // list of selected stops
var stopSelectionOfLine = {}; // dictionary with selected stops (values) per line (key)

var operating_day = null;

/* SELECTION + WRITING FUNCTIONS */
function changeOperatingDayTrips() {
    selectedTrips = [];
    cancelledJourneys = [];
    shortenedJourneys = [];
    clearAllTrips(0);
    clearAllStops();

    var operating_day_text = $("#id_operatingday option:selected").text();
    $("#operating_day_text").text(operating_day_text);
    getActiveLines();
}

function getActiveLines() {
    var operating_day = $("#id_operatingday").val();
    if (operating_day !== null) {
        $.ajax({ url: '/ritaanpassing/lijnen.json',
            data: {'operatingday': operating_day},
            success : saveLines
        });
    } else {
        cancelledLines = [];
        $('#trips thead').hide();
        $('#trips .help').addClass('hidden');
        $('#trips .geen_ritten').removeClass('hidden');
    }
}

function saveLines(data, status) {
    if (data.object) {
        cancelledLines = data.object;
    } else {
        cancelledLines = [];
    }
    getCancelledJourneys();
}

function getCancelledJourneys() {
     operating_day = $("#id_operatingday").val();
     $.ajax({ url: '/ritaanpassing/ritten.json',
            data: {'operatingday': operating_day},
            success : writeCancelledJourneys
     });
}

function writeCancelledJourneys(data, status) {
    if (data.object) {
        $.each(data.object, function (i, journey) {
            cancelledJourneys.push(journey.journey_id);
        });
    }
    getShortenedJourneys();
}

function getShortenedJourneys() {
     operating_day = $("#id_operatingday").val();
     $.ajax({ url: '/ritinkorting/ritten.json',
            data: {'operatingday': operating_day},
            success : writeShortenedJourneys
     });
}

function writeShortenedJourneys(data, status) {
    if (data.object) {
        $.each(data.object, function (i, journey) {
            shortenedJourneys.push(journey.journey_id);
        });
    }
    showTripsOnChange();
}

function showTripsOnChange() {
    if (activeLine !== null) {
        currentLineMeasures = cancelledLines.filter(l => l.id == activeLine || l.id === null);
        tripSelection = [];
        $.ajax({ url: '/line/'+activeLine+'/ritten',
         data: {'operatingday': operating_day},
            success : writeTrips
        });
    }
}

function writeTrips(data, status) {
    tripSelection = data.object.trips_1.concat(data.object.trips_2);

    var maxLen = Math.max(data.object.trips_1.length, data.object.trips_2.length);
    if (maxLen > 0) {
        $('#trips .tripRow').fadeOut(200).remove();
        $('#trips .help').addClass('hidden');
        $('#trips tbody .no_journeys').addClass('hidden');
        var tripRows = "";
        for (i = 0; i <= maxLen; i = i + 1) {
            a = null;
            b = null;
            if (i in data.object.trips_1)
                a = data.object.trips_1[i];
            if (i in data.object.trips_2)
                b = data.object.trips_2[i];
            if (a || b) {
                tripRows += renderTrip(a, b);
            }
        }
        $('#trips tbody').append(tripRows);
        $('#trips thead').fadeIn(200);
        $('#trips tbody').fadeIn(200);
        $("#all_journeys").removeAttr('disabled');
    } else {
        $('#trips thead').hide();
        $('.triprow').fadeOut(100).remove();
        $('#trips .geen_ritten').fadeIn(200);
        $('#all_journeys').attr('disabled','disabled');
    }
}

function renderTrip(trip_a, trip_b) {
    out = '<tr class="tripRow">';
    out += renderTripCell(trip_a);
    out += renderTripCell(trip_b);
    out += '</tr>';
    return out;
}

function renderTripCell(trip) {
    if (trip == null)
        return "<td>&nbsp;</td>";

    $('#trips td.warning').removeClass('warning');
    $('#trips td.line_warning').removeClass('line_warning');

    const currentTripMeasures = currentLineMeasures.filter(measure => {
        if (measure.begintime === null && measure.endtime === null) {
            return true;
        } else if (measure.begintime === null && measure.endtime > trip.departuretime) {
            return true;
        } else if (measure.begintime <= trip.departuretime && measure.endtime === null) {
            return true;
        } else if (measure.begintime <= trip.departuretime && measure.endtime >= trip.departuretime) {
            return true;
        }
    });

    if (currentTripMeasures.length > 0) {
        out = '<td class="trip line_warning" id="t'+trip.id+'">';
    } else if ($.inArray(trip.id, cancelledJourneys) != -1) {
        out = '<td class="trip warning" id="t'+trip.id+'">';
    } else if ($.inArray(trip.id, shortenedJourneys) != -1) {
        out = '<td class="trip notice" id="t'+trip.id+'">';
    } else if ($.inArray(trip.id+'-'+currentLine, selectedTrips) != -1) {
        out = '<td class="trip ui-selectee success" id="t'+trip.id+'">';
    } else {
        out = '<td class="trip" id="t'+trip.id+'">';
    }
    out += "<strong>Rit "+trip.journeynumber+"</strong>";
    out += "&nbsp;<small>Vertrek "+convertSecondsToTime(trip.departuretime)+"</small>";

    if (currentTripMeasures.length > 0) {
        if (currentTripMeasures.filter(l =>l.id === null).length > 0) {
            out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Vervoerder is opgeheven"></span>';
        } else if (currentTripMeasures.filter(l => l.id == activeLine).length > 0) {
        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Lijn is opgeheven"></span>';
        }
    } else if ($.inArray(trip.id, cancelledJourneys) != -1) {
        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Rit is opgeheven"></span>';
    } else if ($.inArray(trip.id, shortenedJourneys) != -1) {
        out += '<span class="glyphicon glyphicon-scissors pull-right" title="Rit is al ingekort"></span>';
    }
    out += "</td>";
    return out
}

function changeSearch(event) {
    if ($("#line_search").val().length > 0) {
        resetAll(false);
        $.ajax('/line/'+$("#line_search").val(), {
            success : writeList
        })
        $("#tripoverzicht tr td").removeClass('success');
    } else if ($("#haltelijn_search").val().length > 0) {
        resetAll(false);
        var term = encodeURIComponent($("#haltelijn_search").val());
        $.ajax({
            method: 'GET',
            url: '/stop',
            data: {
                search: term,
            },
            success : writeStopList
        });
    } else {
        resetAll(true);
    }
}

function writeList(data, status, item) {
    var validIds = [];
    if (data.object_list.length == 0) {
        $('.geen_lijn').removeClass('hidden');
    } else {
        $('.geen_lijn').addClass('hidden');
    }
    /* Add them all, as neccesary */
    $.each(data.object_list, function (i, line) {
        validIds.push('l'+line.pk);
        if (!$('#l'+line.pk).length) {
            if (line.publiclinenumber) { // not all lines with a lineplanningnumber has a publiclinenumber or headsign
                var out = '';
                var row = '';
                if (line.publiclinenumber != line.lineplanningnumber) {
                out += "<strong>"+line.publiclinenumber+"</strong>";
                out += " / ";
                out += "<small>"+line.lineplanningnumber+"</small>";
                    row = '<tr class="line" id="l'+line.pk+'"><td>'+out+'</td>';
                } else {
                    out += "<strong>"+line.publiclinenumber+"</strong>";
                    out += '<span class="hidden"><small>'+line.lineplanningnumber+'</small>'
                    row = '<tr class="line" id="l'+line.pk+'"><td>'+out+'</td>';
                }
                row += '<td>'+line.headsign+'</td></tr>';
                if (item == 1){
                    $(row).hide().appendTo('#rows2').fadeIn(200);

                } else {
                    $(row).hide().appendTo('#rows').fadeIn(200);
                }
            }
        }
    });

    /* Cleanup */
    if (item == 1){
        $('#rows2 .help').addClass('hidden');
        $("#rows2 .line").each(function(index) {
            if ($.inArray($(this).attr('id'), validIds) == -1) {
                $(this).fadeOut(200).remove();
            }
        });
        if ($('#rows2 .line').length === 0) {
            $('.geen_lijn').removeClass('hidden');
        }
    } else {
        $("#rows tr.line").each(function(index) {
            if ($.inArray($(this).attr('id'), validIds) == -1) {
                $(this).fadeOut(999).remove();
            }
        });
        if ($("#rows tr.line").length > 0) {
            $('#rows .help').addClass('hidden');
            $("#rows .geen_lijn").addClass("hidden");
        } else {
            if ($("#line_search")[0].value.length > 0) {
                $('#rows .help').addClass('hidden');
                $("#rows .geen_lijn").removeClass("hidden");
            } else if ($("#line_search")[0].value.length == 0) {
                $("#rows .geen_lijn").addClass("hidden");
                $('#rows .help').removeClass('hidden');
            }
        }
    }
}

function showTrips(event) {
    currentTrips = [];
    currentTripLabels = [];
    $("#rows tr.success").removeClass('success');
    $("#rows2 tr.success").removeClass('success');
    $(".suc-icon").remove();

    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    activeLine = $(this).attr('id').substring(1);

    showTripsOnChange();
    $('#line').val(activeLine);
    $(this).addClass('success');
    currentLine = $('#rows tr.success').find("small").text();

    // Show only selected line + button 'toon vorige'
    $("#rows tr.line:not(.success)").fadeOut(100);
    $("#rows2 tr.line:not(.success)").fadeOut(100);

    $("#shorten_buttons").css("display","block");
    $("#rittenoverzicht").css("display","block");

    if (stopSelectionOfLine[currentLine] !== undefined) {
        if (stopSelectionOfLine[currentLine].length != 0) {
            showStops();
            /*
            document.querySelector('#halteoverzicht').scrollIntoView( {
                behavior: 'smooth'
            });
            */
        }
    }
    if ($("tr.line").length == 0) {
        $("#rows .help").addClass("hidden");
        $("#rows .geen_lijn").removeClass("hidden");
    }
}

function selectTrip(event, ui) {
    if ($.inArray('Alle ritten', currentTripLabels) != -1
       || $('#rit-list span').text() == "Alle ritten "){
        clearAllTrips(1);
        clearAllStops();
        $('#div_id_begintime_part').addClass("hidden");
        $('#div_id_endtime_part').addClass('hidden');
    }

    var ritnr = $(ui.selected).attr('id').substring(1);
    if ($.inArray(parseInt(ritnr), cancelledJourneys) != -1 /* Note our array stores numbers, so convert */
       || $(ui.selected).hasClass("line_warning")) /* TODO: ritnr array selection faster than class selection? This disables trip that have been line cancelled. */
        return;

    var new_ritnr = ritnr+'-'+currentLine;
    var id = $.inArray(new_ritnr, selectedTrips);
    var index = $.inArray(new_ritnr, currentTrips);
    if (index == -1) { // not in current selection
        if (id == -1) {  // and not in active selection
            currentTrips.push(new_ritnr);
            $(ui.selected).addClass('success');
            currentTripLabels.push($(ui.selected).find("strong").text());
            $('#rit-list .help').hide();
            if (stopSelectionOfLine[currentLine] !== undefined){
                if (stopSelectionOfLine[currentLine].length != 0) {
                    writeSelectedJourneys();
                }
            }
        } else {
            removeTrip(new_ritnr);
        }
    } else {  // remove from current selection
        currentTrips.splice(index, 1);
        $(ui.selected).removeClass('success');
        var label_id = $.inArray($(ui.selected).find("strong").text(), currentTripLabels);
        currentTripLabels.splice(label_id, 1);
    }
    showStops();
    /*
    document.querySelector('#halteoverzicht').scrollIntoView({
        behavior: 'smooth'
    });
    */
}

function selectAllTrips() {
    currentTriplabels = [];
    currentTrips = [];
    $.each(tripSelection, function(i, trip) {
        currentTrips.push(trip.id+'-'+currentLine);
    });

    if ($('#rit-list span').text() != "Alle ritten ") {
        cancelledJourneys = [];
        clearAllTrips(0);
        clearAllStops();
        $('#rit-list .help').hide();

        currentTripLabels.push($("#all_journeys").text());
    }
    $('#div_id_begintime_part').removeClass('hidden');
    $('#div_id_endtime_part').removeClass('hidden');

    if ($('#id_begintime_part').val().length == 0 & $('#id_endtime_part').val().length == 0) {
        colorSelectedRange();
    } else {
        changeOfRange();
    }
    showStops();
    /*
    document.querySelector('#halteoverzicht').scrollIntoView({
        behavior: 'smooth'
    });
    */
}

function showStops() {
    if (stopLine === activeLine) {
        return;
    }
    $("#body_stops tr.help").hide(200);
    $.ajax('/line/'+activeLine+'/stops', {
        success : writeLine
    });
    stopLine = activeLine;
}

function writeLine(data, status) {
    $("#body_stops tr.stopRow").remove();
    var out = "";
    currentLine = $('#rows tr.success').find("small").text();
    $.each(data.object.stop_map, function (i, stop) {
        if (stop) {
            out += renderRow(stop);
        }
    });
    $('#body_stops').append(out);
}

function renderRow(row) {
    var out = '<tr class="stopRow">';
    if (row.left != null) {
        var id = 's'+row.left.id+'l';
        if ($.inArray('s'+row.left.id+'-'+currentLine, selectedStops) != -1) {
            out += '<td class="stop stop-left success" id="'+id+'">'+row.left.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;';
        } else {
            out += '<td class="stop stop-left" id="'+id+'">'+row.left.name;
            out += '</td>';
        }
    } else {
        out += '<td>&nbsp;</td>';
    }
    if (row.left != null && row.right != null) {
        out += '<td class="img text-center"><img class="stop-img stop-both" src="/static/img/stop-both.png"></td>';
    } else if (row.left != null) {
        out += '<td class="img text-center"><img class="stop-img stop-left" src="/static/img/stop-left.png"></td>';
    } else if (row.right != null) {
        out += '<td class="img text-center"><img class="stop-img stop-right" src="/static/img/stop-right.png"></td>';
    }
    if (row.right != null) {
        var id = 's'+row.right.id+'r';
        if ($.inArray('s'+row.right.id+'-'+currentLine, selectedStops) != -1) {
            out += '<td class="stop stop-right success" id="'+id+'">'+row.right.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;</td>';
        } else {
            out += '<td class="stop stop-right" id="'+id+'">'+row.right.name;
            out += '</td>';
        }
    } else {
        out += '<td>&nbsp;</td>';
    }
    out += '</tr>';
    return out
}

function selectStop(event, ui) {
    $('#halte-list .help').hide();
    if (doSelectStop(ui.selected)) {
        writeSelectedJourneys();
    }
}

function selectStopFromBall(obj) {
    $('#halte-list .help').hide();
    var did = false;
    var parent = $(this).parents('.stopRow');
    var left = $(parent).find(".stop-left");
    var right = $(parent).find(".stop-right");
    if (left.length) {
        x = doSelectStop(parent.find(".stop.stop-right"));
        did = true;
    }
    /* Check if left and right stops aren't accidentally equal */
    if (left.length && right.length && left.attr('id').slice(0, -1) != right.attr('id').slice(0, -1)) {
        x = doSelectStop(parent.find(".stop.stop-left"));
        did = true;
    }
    if (x != 'remove') {
        if (did) {
            writeSelectedJourneys();
        }
    }
}

function doSelectStop(obj) {
    /* Make sure to strip the 'l' or 'r' */
    var id = $(obj).attr('id').slice(0, -1);
    var index = $.inArray(id+'-'+currentLine, selectedStops);
    if (index == -1) {
        $("#"+id+"l, #"+id+"r").addClass('success');
        $("#"+id+"l, #"+id+"r").append('<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;');
        selectedStops.push(id+"-"+currentLine);
        if ($(obj).hasClass('stop-left')) {
            direction = "heen";
        } else {
            direction = "trg";
        }
        var delLink = '<span class="stop-remove glyphicon glyphicon-remove"></span>';
        $("#halte-list").append('<span class="stop-selection pull-left label label-primary" id="s'+id+'-'+currentLine+'">'+'Lijn ' +currentLine+': '+$(obj).text()+'('+direction+') '+delLink+ '</span>');
        stopDict(id.substring(1), currentLine);
        return true;
    } else {
        var current_selection = [];
            $.each($('.ui-selecting'), function(i, stop) {
                current_selection.push(stop.id.slice(1, -1));
            });
            if ($.inArray(id, current_selection) !== -1) {
                removeStop(id+'-'+currentLine, currentLine);
                return 'remove';
            }
    }
    return false;
}

/* write data to page */
function writeSelectedJourneys() {
    if (tripSelection.length) {
        var obj = {};
        obj[$('#rows .success').find('small').text()] = tripSelection;
        if (!allTrips.hasOwnProperty(obj)) {
            allTrips.push(obj);
        }
        tripSelection = [];
    }

    var new_ritnr = null;
    var dellink = '<span class="trip-remove glyphicon glyphicon-remove"></span>';
    if ($.inArray('Alle ritten', currentTripLabels) != -1) {
        new_ritnr = 'Alle ritten';
        $('#rit-list').append('<span id="st'+new_ritnr+'" class="pull-left trip-selection label label-danger">'+new_ritnr+' '+dellink+'</span>');
//        $.each(currentTrips, function(i, trip) {
        selectedTrips.push('Alle ritten');
//        });
        writeSelectedLines();
    } else if ($("#rit-list span").attr('id') == "stAlle ritten") {
//        $.each(currentTrips, function(i, trip) {
        selectedTrips.push('Alle ritten');
//        });
        writeSelectedLines();
    } else {
        $.each(currentTripLabels, function(i, label) {
            new_ritnr = currentTrips[i];
            $('#rit-list').append('<span id="st'+new_ritnr+'" class="pull-left trip-selection label label-danger">'+label+' '+dellink+'</span>');
            selectedTrips.push(new_ritnr);
        });
    }
    currentTripLabels = [];
    currentTrips = [];
    writeTripList();
}

function writeSelectedLines() {
    if ($.inArray(currentLine, lijnList) == -1) {
        var label = '';
        if ($('#rows tr.success').find("strong").text() === currentLine) {
            label += $('#rows tr.success').find("strong").text();
        } else {
            label += $('#rows tr.success').find("strong").text();
            label += ' (';
            label += currentLine;
            label += ')';
        }
        var dellink_line = '<span class="line-remove glyphicon glyphicon-remove"></span>';
        $('#lijn-list').append('<span id="st'+currentLine+'" class="pull-left line-selection label label-danger">'+label+' '+dellink_line+'</span>');
        lijnList.push(currentLine);
        $('.lijn-overzicht').css("display","block");
    }
    var id = $.inArray(activeLine, selectedLines);
    if (activeLine !== null && id == -1) {
        selectedLines.push(activeLine);
    }
    writeLineList();
}

/* Write data to the form fields */
function writeLineList() {
    var out = "";
    $.each(selectedLines, function(index, val) {
        out += val+',';
    });
    $("#lines").val(out.slice(0,-1));
}

function writeTripList() {
    var out = "";
    if (selectedTrips.length) {
        $.each(selectedTrips, function(index, val) {
            var new_trip = val.split("-")[0];
            out += new_trip+",";
        });
    }
    $("#journeys").val(out.slice(0,-1));
}

function stopDict(id, line) {
    var selectedStopsOfLine = [];
    // check if current active line has dictionary
    if (stopSelectionOfLine.hasOwnProperty(line)) {
        selectedStopsOfLine = stopSelectionOfLine[line];
        // check if current selected stop is already included
        if ($.inArray(id, selectedStopsOfLine) === -1) {
                selectedStopsOfLine.push(id);
                stopSelectionOfLine[line] = selectedStopsOfLine;
                writeOutputAsString(stopSelectionOfLine);
        }
    } else { /* create dict of line and add current stop to new list */
        selectedStopsOfLine.push(id);
        stopSelectionOfLine[line] = selectedStopsOfLine;
        writeOutputAsString(stopSelectionOfLine);
    }
}

function writeOutputAsString(data) {
    var out = "";
    $.each(data, function (line, stops) {
        out += line;
        out += ":";
        $.each(stops, function(i, stop) {
            out += stop;
            out += ",";
        });
        out += ";";
    });
    $("#haltes").val(out.slice(0, -1));
}

/* Remove line */
function removeLineFromX() {
    removeLine($(this).parent().attr('id').substring(2));
}

function removeLine(lijn) {
    var id = $.inArray(lijn, lijnList);

    if (id != -1) {
        $('#st'+lijn).remove();
        selectedLines.splice(id, 1);
        lijnList.splice(id, 1);
        writeLineList();
        removeStopsOfLine(lijn);
        removeJourneysOfLine(lijn);
    }
    if (selectedLines.length == 0) {
        $('.lijn-overzicht').css("display","none");
        clearAllTrips(1);
        clearAllStops();
    }
}

/* Remove trip */
function removeTripFromX(event, ui) {
    if ($('#rit-list span').text() == "Alle ritten ") {
        clearAllTrips(1);
        clearAllStops();
    } else {
        removeTrip($(this).parent().attr('id').substring(2));
    }
}

function removeTrip(ritnr) {
    var old_ritnr = ritnr.split('-')[0];
    var id = $.inArray(ritnr, selectedTrips);
    var index = $.inArray(ritnr, currentTrips);
    if (index != -1) { // remove if in current selection
        $('#t'+old_ritnr).removeClass('success');
        currentTrips.splice(index,1);
        var label_id = $.inArray($('#t'+ old_ritnr).find('strong').text(), currentTripLabels);
        if (label_id != -1) {
            currentTripLabels.splice(label_id, 1);
        }
    } else if (id != -1) { // remove if in active selection
        $('#t'+old_ritnr).removeClass('success');
        $('#st'+ritnr).remove();
        selectedTrips.splice(id, 1);
    }

    if (selectedTrips.length == 0) {
        $('#rit-list .help').show();
        clearAllStops();
    }
    writeTripList();

    if (selectedStops.length == 0) {
        $('#halte-list .help').show();
    } else {
        var lijn = ritnr.split('-')[1];
        var tripsOfLine = 0;
        $.each(selectedTrips, function (i, trip) {
            if (trip.split('-')[1] === lijn) {
                tripsOfLine += 1;
            }
        });
        if (tripsOfLine === 0) {
            removeStop('all', lijn);
        }
    }
}

/* Remove stop */
function removeStopFromX(event) {
    var lijn = $(this).parent().text().split(":")[0].split(" ")[1];
    var id = $(this).parent().attr('id').substring(1);
    removeStop(id, lijn);
}

function lineRemoveStop(event) {
    removeStop($(this).attr('id').slice(0, -1));
}

/* Do the actual work here */
function removeStop(id, lijn) {
    var stop_id = ''
    if (id != 'all') {
        var i = $.inArray(id, selectedStops);
        stop_id = id.split("-")[0];
        if (i != -1) {
            selectedStops.splice(i, 1);
            $("#s"+id).remove();
            $("#"+stop_id+"l, #"+stop_id+"r").removeClass('success');
            $("#"+stop_id+"l .stop-check, #"+stop_id+"r .stop-check").remove();

            if (selectedStops.length == 0) {
                $('#halte-list .help').show();

                // move selected trips back to currentTrip + currentTripLabels if currentLine
                if (lijn === currentLine) {
                    currentTrips = selectedTrips;
                    selectedTrips = [];
                    $.each(currentTrips, function(index, trip) {
                        var trip_id = '#t' +trip.split('-')[0];
                        currentTripLabels.push($(trip_id).find("strong").text());
                    });
                }
                $('#rit-list span').remove();
                writeTripList();
                clearAllStops();
            } else {
                removeStopFromDict(stop_id, lijn);

                /* if last stop of line (but other lines/journeys still selected) remove line */
                if (stopSelectionOfLine[lijn] === undefined) {
                    removeLine(lijn);
                 }
            }
        }
    } else {
        removeStopsOfLine(lijn);
    }
}

function removeStopsOfLine(lijn) {
    stop_id = 'all';
    for (var i = 0; i < selectedStops.length; i++) {
        if (selectedStops[i].split('-')[1] === lijn) {
            $("#s"+selectedStops[i]).remove();
            selectedStops.splice(i, 1);
            i--;
        }
    }
    if (lijn === currentLine) {
            $(".stop").removeClass("success");
            $(".stop span").removeClass("stop-check glyphicon glyphicon-ok-circle pull-right");
        }
        removeStopFromDict(stop_id, lijn);
}

function removeJourneysOfLine(lijn) {
    for (var i = 0; i < selectedTrips.length; i++) {
        if (selectedTrips[i].split('-')[1] === lijn) {
            if (lijn === currentLine) {
            currentTrips.push(selectedTrips[i]);
            currentTripLabels.push($("#st" +selectedTrips[i]).text());
            }
            $("#st"+selectedTrips[i]).remove();
            selectedTrips.splice(i, 1);
            i--;
        }
    }
    writeTripList();
}

function removeStopFromDict(id, linenr){
    var selection = stopSelectionOfLine[linenr];
    if (id != 'all') {
        var index = selection.indexOf(id.substring(1));
        if (index !== -1){
            selection.splice(index,1);
            stopSelectionOfLine[linenr] = selection;
            if (stopSelectionOfLine[linenr].length == 0) {
                    delete stopSelectionOfLine[linenr];
            }
        }
    } else {
        delete stopSelectionOfLine[linenr];
    }
    writeOutputAsString(stopSelectionOfLine);
}

/* clear-all functions */
function clearAllTrips(call) {
    if (call == 1) {
        allTrips = [];
        tripSelection = [];
        selectedTrips = [];
        currentTrips = [];
    }
    currentTripLabels = [];
    $('#rit-list span').remove();
    $('#rit-list .help').show();
    $('#div_id_begintime_part').addClass('hidden');
    $('#div_id_endtime_part').addClass('hidden');
    $('#tripoverzicht tr td').removeClass('all_selected');
    $('#tripoverzicht tr td').removeClass('success');
    $("#journeys").val('');
    //writeTripList();
    emptyLineList();
}

function clearAllStops() {
    selectedStops = [];
    $('#halte-list span').remove();
    $('#halte-list .help').show();
    $(".stop").removeClass("success");
    $(".stop span").removeClass("stop-check glyphicon glyphicon-ok-circle pull-right");
    stopSelectionOfLine = {};
    writeOutputAsString(stopSelectionOfLine);
}

function emptyLineList() {
    lijnList = [];
    selectedLines = [];
    $("#lijn-list").empty();
    $("#lines").val('');
    $('.lijn-overzicht').css("display","none");
}

/* Extra Functions */
function showLines() {
    $("#rows tr.success").removeClass('success');
    $("#rows2 tr.success").removeClass('success');
    $("#rows2, #rows .suc-icon").remove();
    $("#rows tr:not(.success)").show();
    $("#rows2 tr:not(.success)").show();
    $("#shorten_buttons").css("display","none");
}

function resetAll(all) {
    $("#shorten_buttons").css("display","none");

    $("#tripoverzicht .tripRow").remove();
    $("#tripoverzicht .help").removeClass('hidden');
    $("#tripoverzicht .geen_ritten").addClass('hidden');

    $("#body_stops .stopRow").remove();
    $("#body_stops .help").show(200);

    $("#rows .geen_lijn").addClass("hidden");
    $("#rows .help").removeClass("hidden");
    $("#rows .line").remove();

    $("#stop_rows .search_stop").remove();
    $("#stop_rows .specificeer").addClass("hidden");
    $("#stop_rows .help").removeClass("hidden");

    $('#div_id_begintime_part').addClass("hidden");
    $('#div_id_endtime_part').addClass('hidden');
    clearAllTrips(1);
    clearAllStops();
    $("#rows2 .geen_lijn").addClass("hidden");
    $("#rows2 .help").removeClass("hidden");
    $("#rows2 .line").remove();


    stopSelectionOfLine = {};
    writeOutputAsString(stopSelectionOfLine);
    if (all) {
        $("#line_search, #haltelijn_search").val("");

    }
}

function changeOfRange() {
    selectedTrips = [];
    currentTrips = [];
    $('.trip').removeClass('all_selected');
    var times = calculateShortenTimes();
    if (tripSelection.length) {
        updateSelectedTrips('tripSelection', times.begintime, times.endtime);
    }
    if (allTrips.length) {
        updateSelectedTrips('allTrips', times.begintime, times.endtime);
    }
}

function calculateShortenTimes() {
    var selection_begintime = null;
    var selection_endtime = null;

    if ($('#id_begintime_part').val().length !=0) {
        var start_hour = (parseInt($('#id_begintime_part').val().split(':')[0]))*3600;
        var start_minutes = (parseInt($('#id_begintime_part').val().split(':')[1]))*60;
        selection_begintime = (start_hour)+(start_minutes);
    };
    if ($('#id_endtime_part').val().length !=0)  {
        var end_hour = parseInt($('#id_endtime_part').val().split(':')[0])*3600;
        var end_minutes = parseInt($('#id_endtime_part').val().split(':')[1])*60;
        /* add 24h when endtime between 00:00 and 04:00 */
        var extra = 0;
        if (parseInt($('#id_endtime_part').val().split(':')[0]) < 4) {
            extra = 3600*24;
        }
        selection_endtime = end_hour+end_minutes+extra;
    };
    return {
        begintime: selection_begintime,
        endtime: selection_endtime,
    };
}

function updateSelectedTrips(x, begintime, endtime) {
    if (x == 'allTrips') {
        var tripSelection_new = "Alle ritten";
//        $.each(allTrips, function (index, line) {
//            $.each(line, function (linenr, tripsofline) {
//                $.each(tripsofline, function (i, trip) {
//                    if (begintime === null && endtime === null) {
//                        tripSelection_new.push(trip.id+'-'+linenr);
//                    } else if (begintime === null && endtime >= trip.departuretime) {
//                            tripSelection_new.push(trip.id+'-'+linenr);
//                    } else if (begintime <= trip.departuretime && endtime === null) {
//                        tripSelection_new.push(trip.id+'-'+linenr);
//                    } else if (begintime <= trip.departuretime && endtime >= trip.departuretime) {
//                        tripSelection_new.push(trip.id+'-'+linenr);
//                    }
//                });
//            });
//        });
        selectedTrips = tripSelection_new;
    } else {
        var tripSelection_new = [];
        $.each(tripSelection, function (index, trip) {
                if (begintime === null && endtime === null) {
                    tripSelection_new.push(trip.id+'-'+currentLine);
                } else if (begintime === null && endtime >= trip.departuretime) {
                        tripSelection_new.push(trip.id+'-'+currentLine);
                } else if (begintime <= trip.departuretime && endtime === null) {
                    tripSelection_new.push(trip.id+'-'+currentLine);
                } else if (begintime <= trip.departuretime && endtime >= trip.departuretime) {
                    tripSelection_new.push(trip.id+'-'+currentLine);
                }
        });
        currentTrips = tripSelection_new;
    }
    colorSelectedRange();

    if (allTrips.length) {
        $.each(allTrips, function(i, val) {
            $.each(val, function(line, trips) {
                if (line == currentLine) {
                    writeSelectedJourneys();
                }
            });
        });
    }
}

function colorSelectedRange() {
    $('.trip').removeClass('all_selected');

    // set background color for every trip_id within given time-range to show selected trips
    if ($('#id_begintime_part').val().length == 0 & $('#id_endtime_part').val().length == 0) {
            $("#trips tr td").each( function() {
                if ($(this).attr('id')) {
                    $(this).addClass('all_selected');
                };
            });
    } else if (currentTrips.length) {
        $.each(currentTrips, function (i, trip) {
                $('#t'+trip.split('-')[0]).addClass('all_selected');
        });
    } else if (selectedTrips.length) {
                $.each(selectedTrips, function (i, trip) {
                    $('#t'+trip.split('-')[0]).addClass('all_selected');
                });
    }
}

function writeStopList(data, status, item) {
    if ($("#haltelijn_search").val().length > 0 && data.object_list.length == 0) {
        $('#stop_rows tr.search_stop').remove();
        $('#stop_rows tr td.help').addClass('hidden');
        $('.specificeer em').text("Er werden geen haltes gevonden. Kies een andere zoekterm aub");
        $('#stop_rows .specificeer').removeClass('hidden');
        return
    }
    if (data.object_list.length > 0 ) {
        $('#stop_rows tr td.help').addClass('hidden');
        $('#stop_rows tr.search_stop').remove();
    }
    /* Add them all, as neccesary */
    validIds = []
    $.each(data.object_list, function (i, stop) {
        validIds.push('sq'+stop.dataownercode+'_'+stop.userstopcode);
        if (!$('#sq'+stop.dataownercode+'_'+stop.userstopcode).length) {
            var out = '';
            var row = '';
            out += "<strong>"+stop.userstopcode+"</strong>";
            row = '<tr class="search_stop" id="sq'+stop.dataownercode+'_'+stop.userstopcode+'"><td>'+out+'</td>';
            row += '<td>'+stop.name+'</td></tr>';
            $(row).hide().appendTo("#stop_rows");
        }
    });
    $(document).ready(function() {
        if ($('#stop_rows tr').length > 11) {
            $('#stop_rows tr:lt(10)').fadeIn(200);
            $('#stop_rows .specificeer').removeClass('hidden');
            $('.specificeer em').text("Er waren meer dan 10 resulaten. Specificeer uw opdracht aub");
        } else {
            $('#stop_rows .specificeer').addClass('hidden');
            $('#stop_rows tr').fadeIn(200);
        }
    });
    /* Cleanup */
    $("#stop_rows tr").each(function(index) {
        if (index == 0 && $(this).attr('id') == undefined) return

        if ($.inArray($(this).attr('id'), validIds) == -1) {
            $(this).fadeOut(200).remove()
        }
    });
}


function getLinesOfStop(event) {
    $(".lines").remove();
    $("#rows2 .line, .suc-icon").remove();
    $("#haltes-original .stopRow").remove();
    $("#stop_rows tr.success").removeClass('success');
    $(event.currentTarget).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    $.ajax('/stop/'+$(event.currentTarget).attr('id').substring(2)+'/lines', {
        success : function(data, status, item){
            writeList(data, status, 1);
        }
    });
    $(event.currentTarget).addClass('success');
    $('#reset').removeClass('hidden');
}


/* TIME FUNCTIONS */
function convertSecondsToTime(seconds) {
    var hours   = Math.floor(seconds / 3600);
    var minutes = Math.floor((seconds - (hours * 3600)) / 60);
    var extra = "";
    if (hours > 23) {
        hours = hours - 24
        extra = " <em>(+1)</em>"
    }
    return ""+padTime(hours)+":"+padTime(minutes)+extra;
}

function checkMessageTime(event, ui) {
    var starttime = parseDate($("#id_messagestarttime").val());
    var endtime   = parseDate($("#id_messageendtime").val());

    if (starttime >= endtime) {
        if ($(this).attr('id') == "id_messagestarttime") {
            endtime.setDate(endtime.getDate()+1);
            $("#id_messageendtime").val(formatDate(endtime));
        } else {
            starttime.setDate(endtime.getDate()-1);
            $("#id_messagestarttime").val(formatDate(starttime));
        }
    }
}

function calculateTime(event, ui) {
    var text = $(this).val().replace(':', '');
    var change = false;
    var newdate = new Date(); /* Note, set date to the client date... */
    if (text.length <= 2) {
        change = true;
        newdate.setHours(parseInt(text), 0, 0);

    } else if (text.length == 3) {
        change = true;
        newdate.setHours(parseInt(text.slice(0,1)),
                         parseInt(text.slice(1,3)), 0);

    } else if (text.length == 5) {
        change = true;
        newdate.setHours(parseInt(text.slice(0,1)),
                         parseInt(text.slice(1,3)),
                         parseInt(text.slice(3,5)));

    } else if (text.length == 4) {
        change = true;
        newdate.setHours(parseInt(text.slice(0,2)),
                         parseInt(text.slice(2,4)), 0);

    } else if (text.length == 6) {
        change = true;
        newdate.setHours(parseInt(text.slice(0,2)),
                         parseInt(text.slice(2,4)),
                         parseInt(text.slice(4,6)));
    }
    if (change) {
        if (newdate < new Date()) {
            newdate.setDate(newdate.getDate()+1);
        }
        $(this).val(formatDate(newdate))
    }
}

function formatDate(d) {
    out = d.getDate() + "-" + (d.getMonth()+1) + "-" + d.getFullYear();
    out += " "+padTime(d.getHours())+":"+padTime(d.getMinutes())+":"+padTime(d.getSeconds());
    return out
}

function parseDate(d) {
    var parts = d.split(' ');
    var dateparts = parts[0].split('-');
    var timeparts = parts[1].split(':');

    // Workaround because Date.parse will get into timezone issues.
    var newdate = new Date();
    newdate.setFullYear(dateparts[2]);
    newdate.setMonth(dateparts[1]-1);
    newdate.setDate(dateparts[0]);
    newdate.setHours(timeparts[0],timeparts[1],timeparts[2]);

    return newdate;
}

function padTime(i) {
    str = i.toString()
    if (str.length == 2) {
        return str;
    } else if (str.length == 1) {
        return '0'+str;
    } else {
        return '00';
    }
}