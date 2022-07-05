/* TRIP SELECTION */
var selectedTrips = [];
var activeJourneys = [];
var activeLine = null;
var selectedLines = [];
var cancelledLines = [];
var currentLineMeasures = null;
var lijnList = [];
var allTrips = [];
var selectTripMeasures = [];
var tripSelection = [];

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
    if ($.inArray($("#all_lines").text(), selectedLines) != -1) {
        selectedLines = [];
        emptyLineList();
        $('.rit-overzicht').css("display","block");
        $('#rit-list .help').show();
        $('#div_id_begintime_part').addClass('hidden');
        $('#div_id_endtime_part').addClass('hidden');
    }
    $("#rows tr.success").removeClass('success');
    $(".suc-icon").remove();
    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    activeLine = $(this).attr('id').substring(1);

    showTripsOnChange();
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
    if (!$('#div_id_begintime_part').hasClass('hidden')) {
        $('#div_id_begintime_part').addClass('hidden');
        $('#div_id_endtime_part').addClass('hidden');
        $('#id_begintime_part').val('');
        $('#id_endtime_part').val('');
    }
    $("#trips td.all_selected").removeClass('all_selected');
    $('.rit-overzicht').css("display","block");

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
        $("#trips tr td").removeClass('all_selected');
        $('#rit-list span').remove();
        $('#rit-list .help').show();
        $("#journeys").val('');
        emptyLineList();
        $('.lijn-overzicht').css("display","none");

        if (!$('#div_id_begintime_part').hasClass('hidden')) {
            $('#div_id_begintime_part').addClass('hidden');
            $('#div_id_endtime_part').addClass('hidden');
            $('#id_begintime_part').val('');
            $('#id_endtime_part').val('');
        }
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
    $("#journeys").val(out);
}

function writeTrips(data, status) {
    tripSelection = data.object.trips_1.concat(data.object.trips_2);
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
    if ($.inArray(activeLine, selectedLines) != -1) {
        if (selectTripMeasures.length) {
            colorSelectedRange();
        }
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

    if ($.inArray(trip.id, activeJourneys) != -1) {
        out = '<td class="trip warning" id="t'+trip.id+'">';
    } else if (currentTripMeasures.length > 0) {
        out = '<td class="trip line_warning" id="t'+trip.id+'">';
    } else {
        out = '<td class="trip" id="t'+trip.id+'">';
    }
    out += "<strong>Rit "+trip.journeynumber+"</strong>";
    out += "&nbsp;<small>Vertrek "+convertSecondsToTime(trip.departuretime)+"</small>";
    if ($.inArray(trip.id, activeJourneys) != -1) {
        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Rit is al opgeheven"></span>';
    }
    if (currentTripMeasures.length > 0) {
        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Lijn is al opgeheven"></span>';
    }
    out += "</td>";
    return out;
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
    if (!$('#div_id_begintime_part').hasClass('hidden')) {
        $('#div_id_begintime_part').addClass('hidden');
        $('#div_id_endtime_part').addClass('hidden');
        $('#id_begintime_part').val('');
        $('#id_endtime_part').val('');
    }
    emptyLineList();
    emptyJourneyList();
    getActiveLines();
    if ($("#id_operatingday").text === undefined || ($("#id_operatingday").length == 1 ) && $("#id_operatingday option:selected" ).text() !== $("#operating_day_text").text()) {
        $('#trips tr.help').remove();
        $('#trips tr.empty_dates').show();
        $('#line_search').attr('disabled','disabled');
        $('#all_lines').attr('disabled','disabled');
        $('.btn-primary').attr('disabled','disabled');
    }
    else {
        var operating_day_text = $("#id_operatingday option:selected" ).text();
        $("#operating_day_text").text(operating_day_text);
    }
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

function selectAllTrips() {
    selectedTrips = [];
    activeJourneys = [];
    if ($.inArray($("#all_lines").text(), selectedLines) != -1) {
        emptyLineList();
    }
    $('#rit-list .help').hide();
    $('#journeys').val('');
    $('#rit-list span').remove();
    $("#trips tr td").removeClass('success');
    $('.lijn-overzicht').css("display","block");
    if ($('#div_id_begintime_part').hasClass('hidden')) {
        $('#div_id_begintime_part').removeClass('hidden');
        $('#div_id_endtime_part').removeClass('hidden');
    }
    var ritnr = $("#all_journeys").text();
    var dellink = '<span class="trip-remove glyphicon glyphicon-remove"></span>';
    $('#rit-list').append('<span id="st'+ritnr+'" class="pull-left trip-selection label label-danger">'+ritnr+' '+dellink+'</span>');
    selectedTrips.push(ritnr);

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
    }
    // create dict with all trips of active lines
    var obj = {};
    obj[$('#rows .success').find('small').text()] = tripSelection;
    allTrips.push(obj);

    colorSelectedRange();
    writeTripList();

    /* in case of a small screen with everything below each other instead of next to */
    document.querySelector('#ritaanpassing').scrollIntoView({
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
        emptyLineList();
        emptyJourneyList();
        $('.rit-overzicht').css("display","block");
        $('#rit-list .help').show();
        $('#trips thead').show();
        $('#trips tbody').show();
    } else {
        lijnnr =$(this).parent().attr('id').replace('st', '');
        //remove from selectTripMeasures & allTrips
        $.each(selectTripMeasures, function(index, dict) {
            $.each(dict, function(i, key) {
                if (i === lijnnr) {
                    delete selectTripMeasures[index];
                }
            });
        });
        $.each(allTrips, function(index, dict) {
            $.each(dict, function(i, key) {
                if (i === lijnnr) {
                    delete allTrips[index];
                }
            });
        });
        // clear empty objects in arrays
        alltrips = allTrips.filter(function(x) {
            return x != null;
        });
        selectTripMeasures = selectTripMeasures.filter(function(x) {
            return x != null;
        });
        removeLine($(this).parent().attr('id').substring(2));
        colorSelectedRange();
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
        emptyJourneyList();
        emptyLineList();
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

function selectAllLines() {
    emptyLineList();
    emptyJourneyList();
    activeLine = null;
    if ($('#div_id_endtime_part').hasClass('hidden')) {
        $('#div_id_begintime_part').removeClass('hidden');
        $('#div_id_endtime_part').removeClass('hidden');
    }
    $('#trips tbody tr').remove();
    $('.rit-overzicht').css("display","none");
    $('#trips thead').hide();
    $('#trips tbody').hide();
    $('#rit-list .help').hide();
    $("#rows tr").removeClass('success');
    $(".suc-icon").remove();

    var lijn = $("#all_lines").text();
    var dellink = '<span class="line-remove glyphicon glyphicon-remove"></span>';
    $('#lijn-list').append('<span id="st'+lijn+'" class="pull-left line-selection label label-danger">'+lijn+' '+dellink+'</span>');
    selectedLines.push(lijn);
    lijnList.push(lijn);
    $('#lines').val('Hele vervoerder');
    $('.lijn-overzicht').css("display","block");
    $('#all_journeys').attr('disabled','disabled');
    $('#all_journeys').attr('disabled','disabled');


    /* in case of a small screen with everything below each other instead of beside */
    document.querySelector('#ritaanpassing').scrollIntoView({
        behavior: 'smooth'
    });
}

function colorSelectedRange() {
    var selection_begintime = null;
    var selection_endtime = null;
    $('.trip').removeClass('all_selected');

    if ($('#id_begintime_part').val().length !=0) {
        var start_hour = (parseInt($('#id_begintime_part').val().split(':')[0]))*3600;
        var start_minutes = (parseInt($('#id_begintime_part').val().split(':')[1]))*60;
        selection_begintime = (start_hour)+(start_minutes);
    };
    if ($('#id_endtime_part').val().length !=0)  {
        var end_hour = parseInt($('#id_endtime_part').val().split(':')[0])*3600;
        var end_minutes = parseInt($('#id_endtime_part').val().split(':')[1])*60;
        selection_endtime = end_hour+end_minutes;
    };

    selectTripMeasures = [];
    $.each(allTrips, function (index, line) {
        var tripSelection_new = [];
        $.each(line, function (linenr, tripsofline) {
            $.each(tripsofline, function (i, trip) {
                if (selection_begintime === null && selection_endtime === null) {
                    tripSelection_new.push(trip.id);
                } else if (selection_begintime === null && selection_endtime >= trip.departuretime) {
                        tripSelection_new.push(trip.id);
                } else if (selection_begintime <= trip.departuretime && selection_endtime === null) {
                    tripSelection_new.push(trip.id);
                } else if (selection_begintime <= trip.departuretime && selection_endtime >= trip.departuretime) {
                    tripSelection_new.push(trip.id);
                }
            });
            var obj = {};
            obj[linenr] = tripSelection_new;
            if ($.inArray(obj, selectTripMeasures) == -1) {
                selectTripMeasures.push(obj);
            }
        });
    });

    // change background color for every trip_id within given time-range to show selected trips
    if (selectTripMeasures.length) {
        $.each(selectTripMeasures, function (index, line) {
            $.each(line, function (linenr, tripsofline) {
                $.each(tripsofline, function (i, trip) {
                    $('#t'+trip).addClass('all_selected');
                });
            });
        });
    }
}

function changeOfRange() {
    selectTripMeasures = [];
    $('#trips.td.all_selected').removeClass('all_selected');
    colorSelectedRange();
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
