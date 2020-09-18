/* STOP AND SCENARIO FUNCTIONS */
var selectedStops = []
var scenarioStops = []
var blockedStops = [] /* Already have messages set */
var messageData = [] /* all info from blocked stops */
var currentLine = null /* publiclinenumber */
var activeLine = null /* lineplanningnumber */
var lineSelectionOfStop = {}
var lineSelection = []
var line_related = document.getElementById('lijngebonden').checked;


function changeSearch(event) {
    if ($("#line_search").val().length > 0) {
        $.ajax('/line/'+$("#line_search").val(), {
            success : writeList
        })
    }
}

function stopSearch(event) {
    if ($("#halte_search").val().length > 0) {
        $.ajax('/stop/'+$("#halte_search").val(), {
            success : writeStopList
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

function getLinesOfStop(event) {
    $("#rows2").empty();
    $("#stop_rows tr.success").removeClass('success');
    $(".suc-icon").remove();
    $(event.currentTarget).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    $.ajax('/stop/'+$(event.currentTarget).attr('id').substring(2)+'/lines', {
        success : function(data, status, item){
            writeList(data, status, 1);
        }
    })
    $(event.currentTarget).addClass('success');
    //$("#stop_rows tr:not(.success)").fadeOut(100);
}

function writeList(data, status, item) {
    validIds = []
    /* Add them all, as neccesary */
    $.each(data.object_list, function (i, line) {
        validIds.push('l'+line.pk)
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
                    $(row).hide().appendTo('#rows2').fadeIn(999);

                } else {
                    $(row).hide().appendTo('#rows').fadeIn(999);
                }
            }
        }
    });

    /* Cleanup */
    if (item == 1){
        $("#rows2 tr").each(function(index) {
            if ($.inArray($(this).attr('id'), validIds) == -1) {
                $(this).fadeOut(999).remove()
            }
        });
    } else {
        $("#rows tr").each(function(index) {
            if ($.inArray($(this).attr('id'), validIds) == -1) {
                $(this).fadeOut(999).remove()
            }
        });
    }
}

function writeStopList(data, status) {
    validIds = []
    /* Add them all, as neccesary */
    $.each(data.object_list, function (i, stop) {
        validIds.push('sl'+stop.dataownercode+'_'+stop.userstopcode)
        if (!$('#sl'+stop.dataownercode+'_'+stop.userstopcode).length) {
            var out = '';
            var row = '';
            out += "<strong>"+stop.userstopcode+"</strong>";
            row = '<tr class="search_stop" id="sl'+stop.dataownercode+'_'+stop.userstopcode+'"><td>'+out+'</td>';
            row += '<td>'+stop.name+'</td></tr>';
            $(row).hide().appendTo("#stop_rows").fadeIn(999);
        }
    });

    /* Cleanup */
    $("#stop_rows tr").each(function(index) {
        if ($.inArray($(this).attr('id'), validIds) == -1) {
            $(this).fadeOut(999).remove()
        }
    });
}


function showStopsOnChange() {
    $('.stopRow span').remove();
    if (!activeLine) return;

    var line = null;
    if (line_related) {
        line = activeLine;
    }
    if (messageData.length > 0) {
        const filtered = messageData.filter(message => {
            if (message.line == line) {
                start_epoch = epoch(parseDate($('#id_messagestarttime').val()));
                end_epoch = epoch(parseDate($('#id_messageendtime').val()));
                if (message.starttime <= start_epoch && message.endtime >= start_epoch) {
                    return true
                }
            }
        });
        var stops = [];
        if (filtered.length > 0) {
            filtered.filter(message => {
                if ($.inArray(message.userstopcode, stops) == -1) {
                    stops.push(message.userstopcode);
                }
            });
            $.each(stops, function(i, stop) {
                if (line_related){
                    $('[id*='+stop+']').append('<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al een bericht voor deze lijn en begintijd"></span>');
                } else {
                    $('[id*='+stop+']').append('<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al een lijnonafhankelijk bericht voor deze begintijd"></span>');
                }
                blockedStops.push(stop);
            });
        }
    }
    $('.stopRow td.success').append('<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;');

}

function showStops(event) {
    $("#rows tr.success").removeClass('success');
    $(".suc-icon").remove();
    $(event.currentTarget).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    $.ajax('/line/'+$(event.currentTarget).attr('id').substring(1)+'/stops', {
        success : writeLine
    })
    $(event.currentTarget).addClass('success');
}

function selectStop(event, ui) {
    var stop_id = $(ui.selected).attr('id').split("_")[1].slice(0,-1);
    if ($.inArray(stop_id, blockedStops) != -1 & $('#id_messagetype_3').parent().hasClass('active') === false) { // if blocked and no OVERRULE
        return
    }
    $('#halte-list .help').hide();
    if (doSelectStop(ui.selected)) {
        if (line_related) {
            writeHaltesWithLine();
        } else {
            writeHaltesWithoutLine();
        }
    }
}

function selectStopFromBall(obj) {
    $('#halte-list .help').hide();
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
    $('#halte-list .help').hide();
    $('#stops .stop').each(function(index, value) {
        /* Check this is not already selected */
        index = $(this).attr('id').slice(0, -1);
        var selected = selectedStops.filter(stop => stop[2] === index && stop[1] === currentLine);
        if (selected.length == 0) {
            doSelectStop($(this));
        }
    });
    writeHaltesField();
}

function deselectAllVisibleStops() {
    var line = currentLine;
    var id = $.inArray(line, lineSelection);
    lineSelection.splice(id, 1);
    removeStop('all', line);
    writeHaltesField();
}

function doSelectStop(obj) {
    /* Make sure to strip the 'l' or 'r' */
    var id = $(obj).attr('id').slice(0, -1);
    var selectedLines = [];
    if (lineSelectionOfStop[id] !== undefined) {
            selectedLines = lineSelectionOfStop[id];
    }
    var index = $.inArray(currentLine, selectedLines);
    if (index == -1) {
        $("#"+id+"l, #"+id+"r").addClass('success');
        $("#"+id+"l, #"+id+"r").append('<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;');

        selectedLines.push(currentLine);
        lineSelectionOfStop[id] = selectedLines;
        var i = $.inArray(currentLine, lineSelection);
        if (i == -1) {
            lineSelection.push(currentLine);
        }

        if ($(obj).hasClass('stop-left')) {
            direction = "heen";
        } else {
            direction = "trg";
        }
        var headsign = $(obj).text()+'('+direction+') ';
        var stop_id = $(obj).attr('id').slice(0,-1);
        selectedStops.push([headsign, currentLine, stop_id]);
        if (line_related) {
            writeHaltesWithLine();
        } else {
            writeHaltesWithoutLine();
        }
        return true;
    } else {
        removeStop(id, currentLine);
    }
    return false;
}

/* Write data to the form field */
function writeHaltesField() {
    var out = "";
    var stops = [];
    if (line_related) {
        writeLineOutputAsString(lineSelection);
    }
    $.each(selectedStops, function(i, stop) {
        if (stop !== undefined) {
            var stop_id = stop[2].substring(1);
            if ($.inArray(stop_id, stops) === -1) {
                stops.push(stop_id);
            }
        }
    });
    $.each(stops, function(index, halte) {
        out += halte+",";
    });
    $("#haltes").val(out);
}

/* Do the inverse in case we're editing or something */
function readHaltesField() {  // TODO: not adjusted to new line-related yet. Not sure if that's neccessary though
    $.each($("#haltes").val().split(','), function(i, halte) {
        if (halte != "") {
            selectedStops.push('s'+halte)
        }
    });
}

/* Wrapper functions to get the id */
function selectionRemoveStop(event) {
    var stop_id = '';
    var line = null;
    if (line_related) {
        stop_id = $(this).parent().attr('id').split('-')[0].substring(1);
        line = $(this).parent().parent().attr('id').substring(4);
    } else {
        stop_id = $(this).parent().attr('id').substring(1);
        line = currentLine;
    }
    removeStop(stop_id, line);
}

/* Don't know why this is in here, isn't called properly from the html */
function lineRemoveStop(event) {
    removeStop($(this).attr('id').slice(0, -1))
}

function removeStopsOfLine(event) {
    var line = $(this).parent().parent().attr('id').substring(4);

    var idx = $.inArray(line, lineSelection);
    lineSelection.splice(idx, 1);

    $.each(lineSelectionOfStop, function (stop, lines) {
        var idx = $.inArray(line, lines);
        if (idx !== -1) {
            lines.splice(idx, 1);
            lineSelectionOfStop[stop] = lines;
            if (lineSelectionOfStop[stop].length == 0) {
                delete lineSelectionOfStop[stop];
            }
        }
    });

    var new_selection = selectedStops.filter(stop => stop[1] !== line);
    selectedStops = new_selection;

    if (line === currentLine) {
        $(".stop").removeClass('success');
        $(".stop-check").remove();
    }

    var id_end = '-'+line;
    $('[id$='+id_end+']').remove();

    if (Object.keys(lineSelectionOfStop).length == 0) {
        $('#halte-list .help').show();
    }
    $('#'+$(this).parent().parent().attr('id')).remove();

    if (line_related) {
        writeHaltesWithLine();
    } else {
        writeHaltesWithoutLine();
    }
}

/* Do the actual work here */
function removeStop(id, line) {
    if (id == 'all') {
        for (var i = 0; i < selectedStops.length; i++) {
            if (selectedStops[i][1] == line) {
                if (line === currentLine) {
                    var old_id = selectedStops[i][2];
                    $("#"+old_id+"l, #"+old_id+"r").removeClass('success');
                    $("#"+old_id+"l .stop-check, #"+old_id+"r .stop-check").remove();
                    var idx = $.inArray(line, lineSelection)
                    if (idx !== -1) {
                        lineSelection.splice(idx, 1);
                    }
                }
                selectedStops.splice(i, 1);
                i--;
            }
        }
        removeStopFromDict(id, line);
    } else {
        var selection = selectedStops.filter(stop => stop[2] === id && stop[1] === line);
        if (selection.length > 0) {
            var idx = selectedStops.indexOf(selection[0]);
            selectedStops.splice(idx, 1);
            removeStopFromDict(selection[0][2], selection[0][1]);
            var halte = id;
            if (line_related) {
                halte = id+'-'+line;
            }
            $("#"+halte).remove();

            if (line === currentLine) {
                var old_id = id.split('-')[0].substring(1);
                $("#"+id+"l, #"+id+"r").removeClass('success');
                $("#"+id+"l .stop-check, #"+id+"r .stop-check").remove();
            }
            var result = selectedStops.filter(stop => stop[1] === line);
            if (result.length === 0) {
                var i = $.inArray(line, lineSelection);
                lineSelection.splice(i, 1);
            }
        }
    }
    if (line_related) {
        writeHaltesWithLine();
    } else {
        writeHaltesWithoutLine();
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
    $('.stop_btn').removeClass('hide');
}

function renderRow(row) {
    var stopSelection = [];
    var currentStopMeasures = [];
    var messagestarttime = epoch(parseDate($('#id_messagestarttime').val()));
    var messageendtime = epoch(parseDate($('#id_messageendtime').val()));
    var line = null;
    if (line_related) {
        line = activeLine;
    }
    messageData.filter(measure => {
        if (measure.line == line) {
            if (measure.starttime <= messagestarttime && measure.endtime >= messagestarttime) {
                stop = measure.dataownercode + '_' + measure.userstopcode;
                currentStopMeasures.push([stop, measure.starttime, measure.endtime, measure.line, measure.message]);
            }
        }
    });

    out = '<tr class="stopRow">';
    if (row.left != null) {
        if ($.inArray(row.left.id, scenarioStops) != -1) {
            out += '<td class="warning">'+row.left.name+' <span class="glyphicon glyphicon-warning-sign pull-right" title="Al in scenario opgenomen"></span></td>'
        } else {
            var id = 's'+row.left.id+'l';
            if (lineSelectionOfStop['s'+row.left.id] !== undefined) {
                stopSelection = lineSelectionOfStop['s'+row.left.id];
            }
            if ($.inArray(currentLine, stopSelection) != -1) {
                out += '<td class="stop stop-left success" id="'+id+'">'+row.left.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;'
            } else {
                out += '<td class="stop stop-left" id="'+id+'">'+row.left.name;
                var selected = currentStopMeasures.filter(message => message[0] === row.left.id);
                if (selected.length > 0) {
                    if (line_related) {
                        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al een bericht voor deze lijn en begintijd"></span>'
                    } else {
                        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al een lijnonafhankelijk bericht voor deze begintijd"></span>'
                    }
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
            if (lineSelectionOfStop['s'+row.right.id] !== undefined) {
                stopSelection = lineSelectionOfStop['s'+row.right.id];
            }
            if ($.inArray(currentLine, stopSelection) != -1) {
                out += '<td class="stop stop-right success" id="'+id+'">'+row.right.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;</td>';
            } else {
                out += '<td class="stop stop-right" id="'+id+'">'+row.right.name;
                var selected = currentStopMeasures.filter(message => message[0] === row.right.id);
                if (selected.length > 0) {
                    if (line_related) {
                        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al een bericht voor deze lijn en begintijd"></span>'
                    } else {
                        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al een lijnonafhankelijk bericht voor deze begintijd"></span>'
                    }
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

function getHaltesWithMessages(event) {
    var starttime = parseDate($("#id_messagestarttime").val()).toJSON()
    activeLine = $(this).attr('id').substring(1);
    currentLine = $(this).find("small").text();

    $.ajax({ url: '/bericht/haltes.json',
            data: {'messagestarttime': starttime},
            success : function(data) {
                writeHaltesWithMessages(data);
                showStops(event);
                }
    });
}

function writeHaltesWithMessages(data) {
    $('.stopRow span').remove();
    blockedStops = [];
    messageData = data.object;
    if (activeLine) {
        var line = null;
        if (line_related) {
            line = activeLine
        }
        $.each(data.object, function (i, halte) {
            if (halte['line'] == line) {
                blockedStops.push(halte['userstopcode'])
            }
        });
    } else {  /* shouldn't be neccassary, but just in case */
        $.each(data.object, function (i, halte) {
            blockedStops.push(halte['userstopcode'])
        });
    }
}

function lineRelated() {
    line_related = document.getElementById('lijngebonden').checked;
    if (!activeLine) return

    var starttime = parseDate($("#id_messagestarttime").val()).toJSON()
    $.ajax({ url: '/bericht/haltes.json',
            data: {'messagestarttime': starttime},
            success : function(data){
                writeHaltesWithMessages(data);
                showStopsOnChange();
                switchHaltesField();
                }
    });
}

function switchHaltesField() {
    if (line_related) {
        $('#halte-list span').remove();
        writeHaltesWithLine();
    } else {
        $('#halte-list div').remove();
        $('#lines').val('');
        writeHaltesWithoutLine();
    }
}

function writeHaltesWithLine() {
    $('#halte-list div').remove();
    var delLine = '<span class="line-remove glyphicon glyphicon-remove"></span>';
    $.each(lineSelection, function (index, line) {
        $("#halte-list").append('<div><p class=lijn'+line+' id=lijn'+line+'><span class="stop-selection pull-left label label-danger">Lijn: '+line+ ' '+delLine+'</span></p><br /></div><div class="clearfix" id="lijnfix"></div>');
    });
    var delLink = '<span class="stop-remove glyphicon glyphicon-remove"></span>';
    $.each(selectedStops, function(i, stop) {
        var halte_id = stop[2];
        var lijn = stop[1];
        var headsign = stop[0];
        $('.lijn'+lijn).append('<span class="stop-selection pull-left label label-primary" id="s'+halte_id+'-'+lijn+'">'+headsign+delLink+'</span');
    });
    if (selectedStops.length === 0) {
        $('#halte-list .help').show();
    }
    writeHaltesField();
}

function writeHaltesWithoutLine() {
    $('#halte-list span').remove();
    var haltes = {};
    $.each(selectedStops, function(i, stop) {
        var halte_id = stop[2];
        var headsign = stop[0];
        if (!haltes.hasOwnProperty(halte_id)) {
            haltes[halte_id] = headsign;
        }
    });
    var delLink = '<span class="stop-remove glyphicon glyphicon-remove"></span>';
    $.each(haltes, function(halte, headsign) {
        $('#halte-list').append('<span class="stop-selection pull-left label label-primary" id="s'+halte+'">'+headsign+delLink+'</span');
    });
    if (selectedStops.length === 0) {
        $('#halte-list .help').show();
    }
    writeHaltesField();
}

function stopDict(stop, line) {
    var selectedLinesOfStop = [];
    if (lineSelectionOfStop.hasOwnProperty(stop)) {
        selectedLinesOfStop = selectedLinesOfStop[stop];
        if ($.inArray(line, selectedLinesOfStop) === -1) {
                selectedLinesOfStop.push(line);
                lineSelectionOfStop[stop] = selectedLinesOfStop;
        }
    } else {
        selectedLinesOfStop.push(line);
        lineSelectionOfStop[stop] = selectedLinesOfStop;
    }
}

function removeStopFromDict(id, line){
    if (id != 'all') {
        var selection = lineSelectionOfStop[id];
        var index = selection.indexOf(line);
        if (index !== -1){
            selection.splice(index,1);
            if (selection.length == 0) {
                delete lineSelectionOfStop[id];
            } else {
                lineSelectionOfStop[stop] = selection;
            }
        }
    } else {
        var stops = Object.keys(lineSelectionOfStop);
        $.each(stops, function(i,stop) {
            var idx = $.inArray(line, lineSelectionOfStop[stop]);
            if (idx !== -1) {
                lineSelectionOfStop[stop].splice(idx, 1);
            }
            if (lineSelectionOfStop[stop].length == 0) {
                delete lineSelectionOfStop[stop];
            }
        })
    }
}

function writeLineOutputAsString(data) {
    var out = "";
    data.sort();
    $.each(data, function (i, line) {
        out += line;
        out += ",";
    });
    $("#lines").val(out);
}

function epoch(date) {
    return Date.parse(date) / 1000;
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