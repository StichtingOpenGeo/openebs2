/* TRIP SELECTION */
var selectedTrips = [];
var activeJourneys = [];
var activeLine = null;
var selectedLines = [];
var cancelledLines = [];
var currentLineMeasures = null;
var lijnList = [];

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
                $(row).hide().appendTo("#rows").fadeIn(200);
            }
        }
    });

    /* Cleanup */
    $("#rows tr").each(function(index) {
        if ($.inArray($(this).attr('id'), validIds) == -1) {
            $(this).fadeOut(200).remove()
        }
    });
}

function showTrips(event) {
    $("#rows tr.success").removeClass('success');
    $(".suc-icon").remove();
    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    activeLine = $(this).attr('id').substring(1);

    showTripsOnChange();
    $('#line').val(activeLine);
    $(this).addClass('success');
}

function loadPreselectedJourneys() {
    $(".rit-preload").each(function(id, val) {
        selectedTrips.push($(val).attr('id').substring(2));
    });
    writeTripList();
}

function selectTrip(event, ui) {
    if ($.inArray($("#all_journeys").text(), selectedTrips) != -1) {
        emptyJourneyList();
        $('.lijn-overzicht').css("display","none");
        emptyLineList();
    }
    $("#trips td.all_selected").removeClass('all_selected');
    $('.lijn-overzicht').css("display","none");
    $('.rit-overzicht').css("display","block");
    $('#lijn-list span').remove();

    var ritnr = $(ui.selected).attr('id').substring(1);
    if ($.inArray(parseInt(ritnr), activeJourneys) != -1 /* Note our array stores numbers, so convert */
       || $(ui.selected).hasClass("line_warning")) /* TODO: ritnr array selection faster than class selection? This disables trip that have been line cancelled. */
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
    if ($.inArray($("#all_journeys").text(), selectedTrips) != -1) {
        $('#rit-list span').empty();
        $('#rit-list .help').show();
        $("#journeys").val('')
        $('#lijn-list').empty();
        lijnList = [];
        $("#lines").val('')
        $('.lijn-overzicht').css("display","none");
    } else {
        removeTrip($(this).parent().attr('id').substring(2));
    }
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
    maxLen = Math.max(data.object.trips_1.length, data.object.trips_2.length);
    if (maxLen > 0) {
        $('#trips tbody').fadeOut(100).empty();
        tripRows = null;
        for (i = 0; i <= maxLen; i = i + 1) {
            a = null;
            b = null;
            if (i in data.object.trips_1)
                a = data.object.trips_1[i];
            if (i in data.object.trips_2)
                b = data.object.trips_2[i];
            tripRows += renderTrip(a, b);
        }
        $('#trips tbody').hide().append(tripRows);
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

    if ($.inArray(trip.id, activeJourneys) != -1) {
        out = '<td class="trip warning" id="t'+trip.id+'">'
    } else if (currentLineMeasures.length > 0) {
        out = '<td class="trip line_warning" id="t'+trip.id+'">'
    } else {
        out = '<td class="trip" id="t'+trip.id+'">'
    }
    out += "<strong>Rit "+trip.journeynumber+"</strong>"
    out += "&nbsp;<small>Vertrek "+convertSecondsToTime(trip.departuretime)+"</small>"
    if ($.inArray(trip.id, activeJourneys) != -1) {
        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Rit is al opgeheven"></span>'
    }
    if (currentLineMeasures.length > 0) {
    out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Lijn is al opgeheven"></span>'
    }
    out += "</td>"
    return out
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
            activeJourneys.push(journey.journey_id);
        });
    }
    showTripsOnChange();
}

function changeOperatingDayTrips() {
    $("#rit-list span").remove();
    $('#rit-list .help').show();
    selectedTrips = [];
    activeJourneys  = [];
    $("#journeys").val('');
    getActiveLines();
    var operating_day_text = $("#id_operatingday option:selected" ).text();
    $("#operating_day_text").text(operating_day_text);
}

function showTripsOnChange() {
    if (activeLine != null) {
        currentLineMeasures = cancelledLines.filter(l => l.id == activeLine || l.id === null);
        var operating_day = $("#id_operatingday").val();
        $.ajax({ url: '/line/'+activeLine+'/ritten',
         data: {'operatingday': operating_day},
            success : writeTrips
        });
    }
}

function getActiveLines() {
var operating_day = $("#id_operatingday").val();
    if (operating_day != null) {
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

function selectAllTrips() {
    selectedTrips = []
    activeJourneys = []
    $('#journeys').val('');
    $('#rit-list span').empty();
    $("#trips tr td").removeClass('success');
    $('#rit-list .help').hide();
    $('.lijn-overzicht').css("display","block");

    var ritnr = $("#all_journeys").text();
    var dellink = '<span class="trip-remove glyphicon glyphicon-remove"></span>';
    $('#rit-list').append('<span id="st'+ritnr+'" class="pull-left trip-selection label label-danger">'+ritnr+' '+dellink+'</span>');
    selectedTrips.push(ritnr);

    if ($.inArray(activeLine, selectedLines) == -1) {
        var label = $('#rows tr.success').find("strong").text();
        var lijn = $('#rows tr.success').find("small").text();
        var dellink_line = '<span class="line-remove glyphicon glyphicon-remove"></span>';
        $('#lijn-list').append('<span id="st'+label+'" class="pull-left line-selection label label-danger">'+label+' '+dellink_line+'</span>');
        lijnList.push(lijn);
        writeLineList();
    }
    writeTripList();

    /* in case of a small screen with everything below each other instead of next to */
    document.querySelector('#ritaanpassing').scrollIntoView({
        behavior: 'smooth'
    });
}

function writeLineList() {
    var id = $.inArray(activeLine, selectedLines);
    if (activeLine !== '' && id == -1) {
        selectedLines.push(activeLine);
        var out = "";
        $.each(selectedLines, function(index, val) {
            out += val+',';
        });
        $("#lines").val(out);
    }
}

function emptyLineList() {
    lijnList = [];
    $("#lijn-list").empty();
    $("#lines").val('');
    selectedLines = [];
    cancelledLines = [];
    currentLineMeasures = [];
    $('#lijn-list span').remove();
    $('.lijn-overzicht').css("display","none");
}

function removeLineFromX(event, ui) {
    if ($.inArray($("#all_lines").text(), selectedLines) != -1) {
        $('.rit-overzicht').css("display","block");
        $('#rit-list .help').show();
        $('#lijn-list').empty();
        lijnList = [];
        $("#lines").val('')
        $('.lijn-overzicht').css("display","none");
    } else {
        removeLine($(this).parent().attr('id').substring(2));
    }
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

    }
    if (selectedLines.length == 0) {
        $('#rit-list .help').show();
        $('#rit-list span').remove();
        $('.lijn-overzicht').css("display","none");
        $("#journeys").val('');
    }
}

function emptyJourneyList() {
    selectedTrips = [];
    activeJourneys = [];
    allTrips = [];
    tripSelection = [];
    selectTripMeasures = [];
    $("#rit-list span").remove();
    $('.rit-overzicht').css("display","block");
    $('#rit-list .help').show();
    $('#trips thead').show();
    $('#trips tbody').show();
    $("#trips tr td").removeClass('ui-selected success');
    $("#journeys").val('');
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
