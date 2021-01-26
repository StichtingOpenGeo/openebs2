/* STOP AND SCENARIO FUNCTIONS */
var selectedStops = []
var scenarioStops = []
var blockedStops = [] /* Already have messages set */

function changeSearch(event) {
    if ($("#line_search").val().length > 0) {
        $.ajax('/line/'+$("#line_search").val(), {
            success : writeList
        })
    }
}

function writeList(data, status) {
    validIds = []
    /* Add them all, as neccesary */
    $.each(data.object_list, function (i, line) {
        validIds.push('l'+line.pk)
        if (!$('#l'+line.pk).length) {
            row = '<tr class="line" id="l'+line.pk+'"><td>'+line.publiclinenumber+ '</td>';
            row += '<td>'+line.headsign+'</td></tr>';
            $(row).hide().appendTo("#rows").fadeIn(200);
        }
    });

    /* Cleanup */
    $("#rows tr").each(function(index) {
        if ($.inArray($(this).attr('id'), validIds) == -1) {
            $(this).fadeOut(200).remove()
        }
    });
}

/* TRIP SELECTION */
var selectedTrips = [];
var activeJourneys = [];

function showTrips(event) {
    $("#rows tr.success").removeClass('success');
    $(".suc-icon").remove();
    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    $.ajax('/line/'+$(this).attr('id').substring(1)+'/ritten', {
        success : writeTrips
    })
    $('#line').val($(this).attr('id').substring(1))
    $(this).addClass('success')
}

function loadPreselectedJourneys() {
    $(".rit-preload").each(function(id, val) {
        selectedTrips.push($(val).attr('id').substring(2));
    });
    writeTripList();
}

function selectTrip(event, ui) {
    var ritnr = $(ui.selected).attr('id').substring(1);
    if ($.inArray(parseInt(ritnr), activeJourneys) != -1) /* Note our array stores numbers, so convert */
        return;

    var id = $.inArray(ritnr, selectedTrips);
    if (id == -1) {
        $('#rit-list .help').hide();
        $(ui.selected).addClass('success');
        var label = $(ui.selected).find("strong").text();
        var dellink = '<span class="trip-remove glyphicon glyphicon-remove"></span>';
        $('#rit-list').append('<span id="st'+ritnr+'" class="pull-left trip-selection label label-danger">'+label+' '+dellink+'</span>');
        selectedTrips.push(ritnr);
        writeTripList();
    } else {
        removeTrip($(ui.selected).attr('id').substring(1));
    }
}

function removeTripFromX(event, ui) {
    removeTrip($(this).parent().attr('id').substring(2));
}

function removeTrip(ritnr) {
    var id = $.inArray(ritnr, selectedTrips);
    if (id != -1) {
        $('#t'+ritnr).removeClass('success');
        $('#st'+ritnr).remove();
        selectedTrips.splice(id, 1);
    }
    if (selectedTrips.length == 0) {
        $('#rit-list .help').show();
    }
    writeTripList();
}

function writeTripList() {
    var out = "";
    $.each(selectedTrips, function(index, val) {
        out += val+',';
    });
    $("#journeys").val(out)
}

function writeTrips(data, status) {
    $('#trips tbody').fadeOut(100).empty();
    tripRows = null
    maxLen = Math.max(data.object.trips_1.length, data.object.trips_2.length)
    for (i = 0; i <= maxLen; i = i + 1) {
        a = null
        b = null
        if (i in data.object.trips_1)
            a = data.object.trips_1[i]
        if (i in data.object.trips_2)
            b = data.object.trips_2[i]
        tripRows += renderTrip(a, b);
    }
    $('#trips tbody').hide().append(tripRows);
    $('#trips tbody').fadeIn(100);
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

    if ($.inArray(trip.id, activeJourneys) != -1) {
        out = '<td class="trip warning" id="t'+trip.id+'">'
    } else {
        out = '<td class="trip" id="t'+trip.id+'">'
    }
    out += "<strong>Rit "+trip.journeynumber+"</strong>"
    out += "&nbsp;<small>Vertrek "+convertSecondsToTime(trip.departuretime)+"</small>"
    if ($.inArray(trip.id, activeJourneys) != -1) {
        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Rit is al opgeheven"></span>'
    }
    out += "</td>"
    return out
}

function getActiveJourneys() {
     $.ajax('/ritaanpassing/ritten.json', {
            success : writeActiveJourneys
     })
}

function writeActiveJourneys(data, status) {
    if (data.object) {
        $.each(data.object, function (i, journey) {
            activeJourneys.push(journey.journey_id)
        });
    }
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
