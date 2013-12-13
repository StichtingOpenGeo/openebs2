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
            row = '<tr class="line" id="l'+line.pk+'"><td>'+line.publiclinenumber+ '</td>';
            row += '<td>'+line.headsign+'</td></tr>';
            $(row).hide().appendTo("#rows").fadeIn(999);
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
    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    $.ajax('/line/'+$(this).attr('id').substring(1)+'/stops', {
        success : writeLine
    })
    $(this).addClass('success')
}

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


function selectStop(event, ui) {
    $('#halte-list .help').remove()
    if (doSelectStop(ui.selected)) {
        writeHaltesField();
    }
}

function selectTrip(event, ui) {
    $('.trip.success').removeClass('success')
    $(this).addClass('success')
    ritnr = $(this).attr('id').substring(1)
    label = $(this).find("strong").text()
    bullet = '<span class="label label-success">'+label+'</span>'
    $('#rit-list').empty().append(bullet)
    $("#journey").val(ritnr)
}

function selectStopFromBall(obj) {
    $('#halte-list .help').remove()
    did = false
    if ($(this).parent().parent().find(".stop-right").length) {
        doSelectStop($(this).parent().parent().find(".stop.stop-right"));
        did = true;
    }
    if ($(this).parent().parent().find(".stop-left").length) {
        doSelectStop($(this).parent().parent().find(".stop.stop-left"));
        did = true;
    }
    if (did) {
        writeHaltesField();
    }
}

function doSelectStop(obj) {
    /* Make sure to strip the 'l' or 'r' */
    id = $(obj).attr('id').slice(0, -1)
    index = $.inArray(id, selectedStops)
    if (index == -1) {
        $("#"+id+"l, #"+id+"r").addClass('success')
        $("#"+id+"l, #"+id+"r").append('<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;')
        selectedStops.push(id);
        if ($(obj).hasClass('stop-left')) {
            direction = "heen";
        } else {
            direction = "trg";
        }
        delLink = '<span class="stop-remove glyphicon glyphicon-remove"></span>';
        $("#halte-list").append('<span class="stop-selection pull-left label label-primary" id="s'+id+'">'+$(obj).text()+'('+direction+') '+delLink+ '</span>');

        return true;
    } else {
        removeStop(id);
    }

    return false;
}

/* Write data to the form field */
function writeHaltesField() {
    var out = "";
    $.each(selectedStops, function(i, stop) {
        if (stop !== undefined) { /* Don't know why this is required, array gets undefined entries. */
            out += stop.substring(1)+",";
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
function selectionRemoveStop(event) {
    removeStop($(this).parent().attr('id').substring(1))
}

function lineRemoveStop(event) {
    removeStop($(this).attr('id').slice(0, -1))
}

/* Do the actual work here */
function removeStop(id) {
    var i = $.inArray(id, selectedStops);
    if (i != -1) {
        selectedStops.splice(i, 1);
        $("#s"+id).remove();
        $("#"+id+"l, #"+id+"r").removeClass('success')
        $("#"+id+"l .stop-check, #"+id+"r .stop-check").remove()
        writeHaltesField()
    }
}

function writeLine(data, status) {
    $('#stops').fadeOut(200).empty();
    out = ""
    $.each(data.object.stop_map, function (i, stop) {
        out += renderRow(stop)
    });
    $('#stops').append(out)
    $('#stops').fadeIn(200);
}

function writeTrips(data, status) {
    $('#trips tbody').fadeOut(200).empty();
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
    $('#trips tbody').append(tripRows)
    $('#trips tbody').fadeIn(200);
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

    out = '<td class="trip" id="t'+trip.id+'">'
    out += "<strong>Rit "+trip.journeynumber+"</strong>"
    time = trip.departuretime.split(":", 2).join(":")
    out += "&nbsp;<small>Vertrek "+time+"</small></td>"
    return out
}

function renderRow(row) {
    out = '<tr>';
    if (row.left != null) {
        if ($.inArray(row.left.id, scenarioStops) != -1) {
            out += '<td class="warning">'+row.left.name+' <span class="glyphicon glyphicon-warning-sign pull-right" title="Al in scenario opgenomen"></span></td>'
        } else {
            var id = 's'+row.left.id+'l';
            if ($.inArray('s'+row.left.id, selectedStops) != -1) {
                out += '<td class="stop stop-left success" id="'+id+'">'+row.left.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;'
            } else {
                out += '<td class="stop stop-left" id="'+id+'">'+row.left.name;
                if ($.inArray(row.left.id, blockedStops) != -1) {
                    out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al bericht"></span>'
                }
                out += '</td>';
            }
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

function getScenarioStops(scenario) {
     $.ajax('/scenario/'+scenario+'/haltes.geojson', {
            success : writeScenarioStops
     })
}

function writeScenarioStops(data, status) {
    if (data.features) {
        $.each(data.features, function (i, halte) {
            stop = halte['properties']['dataownercode']+ '_' + halte['properties']['userstopcode']
            scenarioStops.push(stop)
        });
    }
}

function getHaltesWithMessages() {
    $.ajax('/bericht/haltes.json', {
            success : writeHaltesWithMessages
     })
}

function writeHaltesWithMessages(data, status) {
    $.each(data.object, function (i, halte) {
        stop = halte['dataownercode']+ '_' + halte['userstopcode']
        blockedStops.push(stop)
    });
}
