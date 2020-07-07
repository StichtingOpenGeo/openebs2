/* STOP FUNCTIONS */
var selectedStops = []
var scenarioStops = []
var blockedStops = [] /* Already have shortens set */

function changeSearch(event) {
    if ($("#line_search").val().length > 0) {
        $.ajax('/line/'+$("#line_search").val(), {
            success : writeList
        })
        $("#tripoverzicht tr td").removeClass('success');
        showAll();
    }
}

function changeCount(event) {
    len = $(this).val().length
    addon = $(this).parents('.countwrapper').find('.charcount')[0]
    $(addon).text(len);
    $(addon).removeClass('badge-success badge-warning badge-danger')
    if (len < 178) {
       $(addon).addClass('badge-success')
    } else if (len > 177 && len < 250) {
       $(addon).addClass('badge-warning')
    } else if (len > 249) {
       $(addon).addClass('badge-danger')
    }
}

function writeList(data, status) {
    validIds = []
    /* Add them all, as neccesary */
    $.each(data.object_list, function (i, line) {
        validIds.push('l'+line.pk)
        if (!$('#l'+line.pk).length) {
            if (line.publiclinenumber) { // not all lines with a lineplanningnumber has a publiclinenumber or headsign
                var out = ''
                if (line.publiclinenumber != line.lineplanningnumber) {
                out += "<strong>"+line.publiclinenumber+"</strong>"
                out += " / "
                out += "<small>"+line.lineplanningnumber+"</small>"
                    row = '<tr class="line" id="l'+line.pk+'"><td>'+out+'</td>';
                } else {
                    out += "<strong>"+line.publiclinenumber+"</strong>"
                    out += '<span class="hidden"><small>'+line.lineplanningnumber+'</small>'
                    row = '<tr class="line" id="l'+line.pk+'"><td>'+out+'</td>';
                }
                row += '<td>'+line.headsign+'</td></tr>';
                $(row).hide().appendTo("#rows").fadeIn(999);
            }
        }
    });

    /* Cleanup */
    $("#rows tr").each(function(index) {
        if ($.inArray($(this).attr('id'), validIds) == -1) {
            $(this).fadeOut(999).remove()
        }
    });
}

function showStops(event) {
    $("#rows tr.success").removeClass('success');
    $(".suc-icon").remove();
    $("#body_stops tr.stopRow").remove();
    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    $.ajax('/line/'+$(this).attr('id').substring(1)+'/stops', {
        success : writeLine
    })
    $(this).addClass('success')
}


function selectStop(event, ui) {
    $('#halte-list .help').hide()
    if (doSelectStop(ui.selected)) {
        writeHaltesField();
    }
}

function selectStopFromBall(obj) {
    $('#halte-list .help').hide()
    var did = false
    var parent = $(this).parents('.stopRow');
    var left = $(parent).find(".stop-left");
    var right = $(parent).find(".stop-right");
    if (left.length) {
        doSelectStop(parent.find(".stop.stop-right"));
        did = true;
    }
    /* Check if left and right stops aren't accidentally equal */
    if (left.length && right.length && left.attr('id').slice(0, -1) != right.attr('id').slice(0, -1)) {
        doSelectStop(parent.find(".stop.stop-left"));
        did = true;
    }
    if (did) {
        writeHaltesField();
    }
}

function selectAllVisibleStops() {
    $('#stops .stop').each(function(index, value) {
        /* Check this is not already selected */
        index = $(this).attr('id').slice(0, -1);
        if ($.inArray(index, selectedStops) == -1) {
            doSelectStop($(this));
        }
    });
    writeHaltesField();
}

function deselectAllVisibleStops() {
    $('#stops .stop.success').each(function(index, value) {
        index = $(this).attr('id').slice(0, -1);
        if ($.inArray(index, selectedStops) != -1) {
            var lijn = $('#rows .success').find('small').text();
            removeStop(index, lijn);
        }
    });
    writeHaltesField();
}

function doSelectStop(obj) {
    /* Make sure to strip the 'l' or 'r' */
    id = $(obj).attr('id').slice(0, -1)
    index = $.inArray(id, selectedStops)
    var lijn = $('#rows .success').find('small').text();
    if (index == -1) {
        $("#"+id+"l, #"+id+"r").addClass('success')
        $("#"+id+"l, #"+id+"r").append('<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;')
        selectedStops.push(id+"-"+lijn);
        if ($(obj).hasClass('stop-left')) {
            direction = "heen";
        } else {
            direction = "trg";
        }
        delLink = '<span class="stop-remove glyphicon glyphicon-remove"></span>';
        $("#halte-list").append('<span class="stop-selection pull-left label label-primary" id="s'+id+'-'+lijn+'">'+'Lijn ' +lijn+': '+$(obj).text()+'('+direction+') '+delLink+ '</span>');

        stopDict(id.substring(1), lijn);

        return true;
    } else {
        removeStop(id, lijn);
    }

    return false;
}

/* Write data to the form field */
function writeHaltesField() {
    var out = "";
    $.each(selectedStops, function(i, stop) {
        if (stop !== undefined) { /* Don't know why this is required, array gets undefined entries. */
            var new_stop = stop.split("-")[0];
            out += new_stop.substring(1)+",";
        }
    });
    $("#haltes").val(out)
}

/* Do the inverse in case we're editing or something */
function readHaltesField() {
    $.each($("#haltes").val().split(','), function(i, halte) {
        if (halte != "") {
            selectedStops.push('s'+halte)
        }
    });
}

/* Wrapper functions to get the id */
function removeStopFromX(event) {
    var lijn = $(this).parent().text().split(":")[0].split(" ")[1];
    var id = $(this).parent().attr('id').substring(1);
    removeStop(id, lijn)
}

function lineRemoveStop(event) {
    removeStop($(this).attr('id').slice(0, -1))
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
            $("#"+stop_id+"l .stop-check, #"+id+"r .stop-check").remove();
            if (selectedStops.length == 0) {
                $('#halte-list .help').show();
            }
        }
    } else {
        // remove all selected stops from line
        stop_id = 'all';
        for (var i = 0; i < selectedStops.length; i++) {
            if ( selectedStops[i].split('-')[1] === lijn) {
                $("#s"+selectedStops[i]).remove();
                selectedStops.splice(i, 1);
                i--;
            }
        }
    }
    writeHaltesField()
    removeStopFromDict(stop_id, lijn)
}

function writeLine(data, status) {
    out = ""
    $.each(data.object.stop_map, function (i, stop) {
        out += renderRow(stop)
    });
    $('#body_stops').append(out)
    $("#body_stops tr.stopRow").hide();

}

function renderRow(row) {
    out = '<tr class="stopRow">';
    if (row.left != null) {
        var id = 's'+row.left.id+'l';
        if ($.inArray('s'+row.left.id, selectedStops) != -1) {
            out += '<td class="stop stop-left success" id="'+id+'">'+row.left.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;'
        } else {
            out += '<td class="stop stop-left" id="'+id+'">'+row.left.name;
            out += '</td>';
        }
    } else {
        out += '<td>&nbsp;</td>';
    }
    if (row.left != null && row.right != null) {
        out += '<td class="img text-center"><img class="stop-img stop-both" src="/static/img/stop-both.png"></td>'
    } else if (row.left != null) {
        out += '<td class="img text-center"><img class="stop-img stop-left" src="/static/img/stop-left.png"></td>'
    } else if (row.right != null) {
        out += '<td class="img text-center"><img class="stop-img stop-right" src="/static/img/stop-right.png"></td>'
    }
    if (row.right != null) {
        if ($.inArray(row.right.id, scenarioStops) != -1) {
            out += '<td class="warning">'+row.right.name+' <span class="glyphicon glyphicon-warning-sign pull-right" title="Al in scenario opgenomen"></span></td>'
        } else {
            var id = 's'+row.right.id+'r';
            if ($.inArray('s'+row.right.id, selectedStops) != -1) {
                out += '<td class="stop stop-right success" id="'+id+'">'+row.right.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;</td>';
            } else {
                out += '<td class="stop stop-right" id="'+id+'">'+row.right.name;
                if ($.inArray(row.right.id, blockedStops) != -1) {
                    out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al bericht"></span>'
                }
                out += '</td>';
            }
        }
    } else {
        out += '<td>&nbsp;</td>';
    }
    out += '</tr>';
    return out
}

function getHaltesWithShorten() {
    var operating_day = $("#id_operatingday").val();
     $.ajax({ url: '/ritinkorting/haltes.json',
            data: {'operatingday': operating_day},
            success : writeHaltesWithShorten
     });
}

function writeHaltesWithShorten(data, status) {
    $.each(data.object, function (i, halte) {
        blockedStops.push(halte)
    });
}

/* TRIP SELECTION */
var selectedTrips = [];
var activeJourneys = [];
var activeLine = null;
var selectedLines = [];
var cancelledLines = [];
var currentLineMeasures = null;
var lijnList = [];
var allTrips = [];
var tripSelection = [];
var currentStopMeasures = [];
var stopSelectionOfLine = {};

function showAll() {
    $("#rows tr:not(.success)").show();
    $("#shorten_buttons").css("display","none");
    $("#rittenoverzicht").css("display","none");
    //clearAllTrips();
}

function showTrips(event) {
    $("#rows tr.success").removeClass('success');
    $(".suc-icon").remove();
    var operating_day = $("#id_operatingday").val();

    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    activeLine = $(this).attr('id').substring(1);

    showTripsOnChange();

    $('#line').val(activeLine);
    $(this).addClass('success');

    // Toon alleen de aangeklikte lijn + knop 'toon vorige'.
    $("#rows tr:not(.success)").fadeOut(100);
    $("#shorten_buttons").css("display","block");
    $("#rittenoverzicht").css("display","block");
}

function loadPreselectedJourneys() {
    $(".rit-preload").each(function(id, val) {
        selectedTrips.push($(val).attr('id').substring(2));
    });
    writeTripList();
}

function selectTrip(event, ui) {
    if ($('#rit-list span').text() == "Alle ritten ") {
        selectedTrips = []
        $('#rit-list span').empty()
        $('#rit-list .help').show()
        selectedLines = [];
        lijnList = [];
        emptyLineList();
    }

    var ritnr = $(ui.selected).attr('id').substring(1);
    if ($.inArray(parseInt(ritnr), activeJourneys) != -1 /* Note our array stores numbers, so convert */
       || $(ui.selected).hasClass("line_warning")) /* TODO: ritnr array selection faster than class selection? This disables trip that have been line cancelled. */
        return;

    var lijn = $('#rows tr.success').find("small").text();
    var new_ritnr = ritnr+'-'+lijn;
    var id = $.inArray(new_ritnr, selectedTrips);
    if (id == -1) {

        $('#rit-list .help').hide();
        $(ui.selected).addClass('success');
        var label = $(ui.selected).find("strong").text();
        var dellink = '<span class="trip-remove glyphicon glyphicon-remove"></span>';
        $('#rit-list').append('<span id="st'+new_ritnr+'" class="pull-left trip-selection label label-danger">'+label+' '+dellink+'</span>');
        selectedTrips.push(new_ritnr);
        writeTripList();
    } else {
        removeTrip(new_ritnr);
    }
    currentStopMeasures = blockedStops.filter (s => s.change__line == activeLine || s.change__line===null)

    $("#body_stops tr.help").hide(200);
    $('.stop_btn').removeClass('hide');
    $("#body_stops tr.stopRow").show(200);
    document.querySelector('#halteoverzicht').scrollIntoView({
        behavior: 'smooth'
    });
}

function removeTripFromX(event, ui) {
    if ($('#rit-list span').text() == "Alle ritten ") {
        clearAllTrips();
    } else {
        removeTrip($(this).parent().attr('id').substring(2));
    }
}

function removeTrip(ritnr) {
    var old_ritnr = ritnr.split('-')[0];
    var id = $.inArray(ritnr, selectedTrips);
    if (id != -1) {
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
        writeHaltesField()
    } else {
        var lijn = ritnr.split('-')[1];
        var tripsOfLine = 0;
        $.each(selectedTrips, function (i, trip) {
            if (trip.split('-')[1] === lijn) {
                tripsOfLine += 1;
            }
        });
        if (tripsOfLine === 0) {
            removeStop('all', lijn)
        }
    }
}

function writeTripList() {
    var out = "";
    $.each(selectedTrips, function(index, val) {
        out += val+',';
    });
    $("#journeys").val(out)
}

function writeTrips(data, status) {
    maxLen = Math.max(data.object.trips_1.length, data.object.trips_2.length)
    if (maxLen > 0) {
        $('#trips tbody').fadeOut(200).empty();
        tripRows = null
        for (i = 0; i <= maxLen; i = i + 1) {
            a = null
            b = null
            if (i in data.object.trips_1)
                a = data.object.trips_1[i]
            if (i in data.object.trips_2)
                b = data.object.trips_2[i]
            tripRows += renderTrip(a, b);
        }
        $('#trips tbody').append(tripRows)
        $('#trips thead').fadeIn(200);
        $('#trips tbody').fadeIn(200);
        $("#all_journeys").removeAttr('disabled');
    } else {
        $('#trips thead').hide();
        $('#trips tbody').text("Geen ritten in database.");
        $('#all_journeys').attr('disabled','disabled');
    }
}

function renderTrip(trip_a, trip_b) {
    out = '<tr>';
    out += renderTripCell(trip_a);
    out += renderTripCell(trip_b);
    out += '</tr>';
    return out
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
    } else if ($.inArray(trip.id, activeJourneys) != -1) {
        out = '<td class="trip warning" id="t'+trip.id+'">';
    } else {
        out = '<td class="trip" id="t'+trip.id+'">';
    }
    out += "<strong>Rit "+trip.journeynumber+"</strong>";
    out += "&nbsp;<small>Vertrek "+convertSecondsToTime(trip.departuretime)+"</small>";

    if (currentTripMeasures.length > 0) {
        if (currentTripMeasures.filter(l =>l.id === null).length > 0) {
            out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Vervoerder is opgeheven"></span>'
        } else if (currentTripMeasures.filter(l => l.id == activeLine).length > 0) {
        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Lijn is opgeheven"></span>'
        }
    } else if ($.inArray(trip.id, activeJourneys) != -1) {
        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Rit is opgeheven"></span>'
    }
    out += "</td>";
    return out
}

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
        $('#trips tbody').addClass('empty_database');
        $('#trips tbody').text("Er staan geen ritten in de database.");
    }
}

function saveLines(data, status) {
    if (data.object) {
        cancelledLines = data.object;
    } else {
        cancelledLines = [];
    }
    getActiveJourneys();
}

function getActiveJourneys() {
     var operating_day = $("#id_operatingday").val();
     $.ajax({ url: '/ritaanpassing/ritten.json',
            data: {'operatingday': operating_day},
            success : writeActiveJourneys
     });
}

function writeActiveJourneys(data, status) {
    if (data.object) {
        $.each(data.object, function (i, journey) {
            activeJourneys.push(journey.id)
        });
    }
    showTripsOnChange();
}

function changeOperatingDayTrips() {
    selectedTrips = [];
    $('#rit-list span').empty();
    $('#rit-list .help').show();
    selectedStops = [];
    $('#halte-list span').empty();
    $('#halte-list .help').show();
    $('#stops span').removeClass('stop-check glyphicon glyphicon-ok-circle pull-right');
    $('#stops td').removeClass('ui-selected success');

    activeJourneys = [];
    $("#journeys").val('');
    getActiveLines();
    var operating_day_text = $("#id_operatingday option:selected" ).text();
    $("#operating_day_text").text(operating_day_text);
}

function showTripsOnChange() {
    if (activeLine !== null) {
        currentLineMeasures = cancelledLines.filter(l => l.id == activeLine || l.id === null);
        tripSelection = [];
        var operating_day = $("#id_operatingday").val();
        $.ajax({ url: '/line/'+activeLine+'/ritten',
         data: {'operatingday': operating_day},
            success : writeTrips
        });
    }
}

function selectAllTrips() {
    if ($('#rit-list span').text() != "Alle ritten ") {
        activeJourneys = [];
        clearAllTrips();
        $('#rit-list .help').hide();

        $('.lijn-overzicht').css("display","block");

        var label = $("#all_journeys").text();
        var dellink = '<span class="trip-remove glyphicon glyphicon-remove"></span>';
        $('#rit-list').append('<span id="st'+label+'" class="pull-left trip-selection label label-danger">'+label+' '+dellink+'</span>');
    }

    // add activeLine if not already in selectedLines
    if ($.inArray(activeLine, selectedLines) == -1) {
        var label = '';
        if ($('#rows tr.success').find("strong").text() === $('#rows tr.success').find("small").text()) {
            label += $('#rows tr.success').find("strong").text();
        } else {
            label += $('#rows tr.success').find("strong").text();
            label += ' (';
            label += $('#rows tr.success').find("small").text();
            label += ')';
        }
        var lijn = $('#rows tr.success').find("small").text();
        var dellink_line = '<span class="line-remove glyphicon glyphicon-remove"></span>';
        $('#lijn-list').append('<span id="st'+lijn+'" class="pull-left line-selection label label-danger">'+label+' '+dellink_line+'</span>');
        lijnList.push(lijn);
        writeLineList();

        // if no begin-time or end-time is given:
        $("#trips tr td").each( function() {
        if ($(this).attr('id')) {
            $(this).addClass('success');
            selectedTrips.push($(this).attr('id').substring(1));

        };
        writeTripList();
    });
    }

    currentStopMeasures = blockedStops.filter (s => s.change__line == activeLine || s.change__line===null)

    $("#body_stops tr.help").hide(200);
    $('.stop_btn').removeClass('hide');
    $("#body_stops tr.stopRow").show(200);
    document.querySelector('#halteoverzicht').scrollIntoView({
        behavior: 'smooth'
    });

}

function writeLineList() {
    var id = $.inArray(activeLine, selectedLines);
    if (activeLine !== null && id == -1) {
        selectedLines.push(activeLine);
        var out = "";
        $.each(selectedLines, function(index, val) {
            out += val+',';
        });
        $("#lines").val(out);
    }
}

function clearAllTrips() {
    selectedTrips = [];
    $('#rit-list span').empty();
    $('#rit-list .help').show();
    $('#tripoverzicht tr td.success').removeClass('success');
    $("#journeys").val('')
    writeTripList();
    clearAllStops();
    emptyLineList();
}

function clearAllStops() {
    selectedStops = [];
    $('#halte-list span').empty();
    $('#halte-list .help').show();
    $("#body_stops tr.help").show(200);
    $('.stop_btn').addClass('hide');
    $("#body_stops tr.stopRow").hide(200);
    $(".stop").removeClass("success");
    $(".stop span").removeClass("stop-check glyphicon glyphicon-ok-circle pull-right");
    stopSelectionOfLine = {};
    writeOutputAsString(stopSelectionOfLine);
    writeHaltesField();
}

function removeLineFromX() {
    removeLine($(this).parent().attr('id').substring(2));
}

function removeLine(lijn) {
    var id = $.inArray(lijn, lijnList);

    if (id != -1) {
        $('#st'+lijn).remove();
        selectedLines.splice(id, 1);
        lijnList.splice(id, 1);
        var out = "";
        $.each(selectedLines, function(index, val) {
            out += val+',';
        });
        $("#lines").val(out);
        removeStop('all', lijn)

    }
    if (selectedLines.length == 0) {
        $('.lijn-overzicht').css("display","none");
        clearAllTrips();
    }
}

function emptyLineList() {
    lijnList = [];
    selectedLines = [];
    $("#lijn-list").empty();
    $("#lines").val('');
    $('.lijn-overzicht').css("display","none");

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

function removeStopFromDict(id, linenr){
    var selection = stopSelectionOfLine[linenr];
    if (id != 'all') {
        var index = selection.indexOf(id.substring(1));
        if (index !== -1){
            selection.splice(index,1);
            stopSelectionOfLine[linenr] = selection;
        }
    } else {
        delete stopSelectionOfLine[linenr];
    }
    writeOutputAsString(stopSelectionOfLine);
}

function writeOutputAsString(data) {
    var out = "";
    $.each(data, function (line, stops) {
        out += line;
        out += ":"
        $.each(stops, function(i, stop) {
            out += stop;
            out += ",";
        });
        out += ";";
    });
    $("#stopdict").val(out);
}

function resetAll() {
    $("#shorten_buttons").css("display","none");
    clearAllTrips();
    $("#line_search").val("");
    $("#rows").empty();
    stopSelectionOfLine = {};
    writeOutputAsString(stopSelectionOfLine);
}


/* TIME FUNCTIONS */
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
/*
function hideEndTime() {
    $('#div_id_messageendtime').hide();
    $('#id_messageendtime').val('31-12-2099 00:00:00');
}
function showEndTime() {
   $('#div_id_messageendtime').show();
   var enddate = new Date();
   enddate.setHours(3, 0, 0);
   enddate.setDate(enddate.getDate()+1);
   $('#id_messageendtime').val(formatDate(enddate));
}
*/