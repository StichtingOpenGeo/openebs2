/* STOP AND SCENARIO FUNCTIONS */
var selectedStops = []
var scenarioStops = []
var blockedStops = [] /* Already have messages set */
var messageData = [] /* all info from blocked stops */
var activeLine = null /* lineplanningnumber */

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
            if (line.publiclinenumber) { // not all lines with a lineplanningnumber has a publiclinenumber or headsign
                row = '<tr class="line" id="l'+line.pk+'"><td>'+line.publiclinenumber+ '</td>';
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

function showStops(event) {
    $("#rows tr.success").removeClass('success');
    $(".suc-icon").remove();
    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    $.ajax('/line/'+$(this).attr('id').substring(1)+'/stops', {
        success : writeLine
    })
    $(this).addClass('success')
}

function selectStop(event, ui) {
    var stop_id = $(ui.selected).attr('id').slice(1,-1);
    if ($.inArray(stop_id, blockedStops) != -1 & $('#id_messagetype_3').parent().hasClass('active') === false) { // if blocked and no OVERRULE
        return
    }
    if (doSelectStop(ui.selected)) {
        $('#halte-list .help').addClass('hidden');
        writeHaltesField();
    }
}

function selectStopFromBall(obj) {
    $('#halte-list .help').addClass('hidden');
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
    $('#halte-list .help').addClass('hidden');
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
            removeStop(index)
        }
    });
    writeHaltesField();
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
        if (selectedStops.length == 0) {
            $('#halte-list .help').removeClass('hidden');
        }
        writeHaltesField()
    }
}

function writeLine(data, status) {
    $('#stops').fadeOut(100).empty();
    out = ""
    blockedStops = [];

    $.each(data.object.stop_map, function (i, stop) {
        out += renderRow(stop)
    });
    $('#stops').hide().append(out);
    $('#stops').fadeIn(100);
    $('.stop_btn').removeClass('hide');
}

function renderRow(row) {
    var pathname = window.location.pathname;
    if (pathname.indexOf('scenario') == -1) {
        var currentStopMeasures = [];
        var messagestarttime = epoch(parseDate($('#id_messagestarttime').val()));
        var messageendtime = epoch(parseDate($('#id_messageendtime').val()));

        messageData.filter(measure => {
            if (measure.starttime <= messagestarttime) {
                if (measure.endtime >= messagestarttime || measure.endtime === null) {
                    stop = measure.dataownercode + '_' + measure.userstopcode;
                    currentStopMeasures.push([stop, measure.starttime, measure.endtime, measure.message]);
                }
            }
        });
    }
    out = '<tr class="stopRow">';
    if (row.left != null) {
        if ($.inArray(row.left.id, scenarioStops) != -1) {
            out += '<td class="warning">'+row.left.name+' <span class="glyphicon glyphicon-warning-sign pull-right" title="Al in scenario opgenomen"></span></td>'
        } else {
            var id = 's'+row.left.id+'l';
            if ($.inArray('s'+row.left.id, selectedStops) != -1) {
                out += '<td class="stop stop-left success" id="'+id+'">'+row.left.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;'
            } else {
                var pathname = window.location.pathname;
                if (pathname.indexOf('scenario') == -1) {
                    var selected = currentStopMeasures.filter(message => message[0] === row.left.id);
                    out += '<td class="stop stop-left" id="'+id+'">'+row.left.name;
                    if (selected.length > 0) {
                        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al een bericht voor deze begintijd"></span>';
                        blockedStops.push(row.left.id);
                    }
                    out += '</td>';
                } else {
                    out += '<td class="stop stop-left" id="'+id+'">'+row.left.name;
                    if ($.inArray(row.left.id, blockedStops) != -1) {
                        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al bericht"></span>'
                    }
                    out += '</td>';
                }
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
                var pathname = window.location.pathname;
                if (pathname.indexOf('scenario') == -1) {
                    var selected = currentStopMeasures.filter(message => message[0] === row.right.id);
                    out += '<td class="stop stop-right" id="'+id+'">'+row.right.name;

                    if (selected.length > 0) {
                        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al een bericht voor deze begintijd"></span>'
                        blockedStops.push(row.right.id);
                    }
                    out += '</td>';
                } else {
                    out += '<td class="stop stop-right" id="'+id+'">'+row.right.name;
                    if ($.inArray(row.right.id, blockedStops) != -1) {
                        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al bericht"></span>'
                    }
                    out += '</td>';
                }
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
            success : function(data) {
                messageData = data.object;
            }
     });
}

function formValidation() {
    var pathname = window.location.pathname;
    var validationdata = $('.form').serializeArray().reduce(function(obj, item) {
        obj[item.name] = item.value;
        return obj;
    }, {});
    validationdata['csrfmiddlewaretoken'] = document.getElementsByName('csrfmiddlewaretoken')[0].value;

    $.ajax({url: pathname,
            data: validationdata,
            method: 'POST',
            success : function(result) {
                if (pathname.indexOf('scenario') !== -1) {
                    var base_href = pathname.split('bericht')[0];
                    window.location.href = base_href + 'bewerk';
                } else {
                    window.location.href = '/bericht';
                }
            },
            error: function(result) {
                var response = result.responseJSON;
                if (!$("#error_list").hasClass('hidden')) {
                        $("#error_list").empty();
                        $(".has-error").removeClass('has-error');
                        $(".error-label").removeClass('error-label');
                }
                $.each(response, function(field, errorlist) {
                    $.each(errorlist, function(idx, error) {
                        $("#error_list").append('<p><span class="glyphicon glyphicon-flag" style="color:#a94442"><em class="help" style="color: #a94442"> '+error+'</em></span></p>');
                        error = error.toLowerCase();
                        if (error.indexOf('begin') !== -1) {
                            $('#div_id_messagestarttime').addClass('has-error');
                        }
                        if (error.indexOf('eind') !== -1) {
                            $('#div_id_messageendtime').addClass('has-error');
                        } else if (error.indexOf('type') !== -1) {
                            $('#div_id_messagetype').addClass('has-error');
                        }

                        if (error.indexOf('halte') !== -1) {
                            $('#div_id_haltes').addClass('error-label');
                        } else if (error.indexOf('bericht') !== -1) {
                            $('#div_id_messagecontent').addClass('has-error');
                        }

                    });
                });
                if ($("#error_list").hasClass('hidden')) {
                    $("#error_list").removeClass('hidden');
                }
            }
     });
}

function showStopsOnChange() {
    $('.stopRow span').remove();
    if (!$("#error_list").hasClass('hidden')) {
        $("#error_list").empty();
        $("#error_list").addClass('hidden');
        $('[id^=ss'+stop+']').removeClass('stop_warning');
        $('#div_id_haltes').addClass('error-label');
    }
    blockedStops = [];
    if (messageData.length > 0) {
        const filtered_messagedata = messageData.filter(message => {
            start_epoch = epoch(parseDate($('#id_messagestarttime').val()));
            end_epoch = epoch(parseDate($('#id_messageendtime').val()));
            if (message.starttime <= start_epoch) {
                if (message.endtime >= start_epoch || message.endtime === null) {
                    return true
                }
            }
        });
        if (window.location.pathname.indexOf('bewerken') !== -1 && window.location.pathname.indexOf('scenario') === -1) { // remove current message_id from current when updating message
            var current_id = window.location.pathname.split('/')[2];
            var filtered = filtered_messagedata.filter(message => {
                if (message.message_id != current_id) {
                    return true
                }
            });
        } else {
            var filtered = filtered_messagedata;
        }

        var stops = [];
        if (filtered.length > 0) {
            filtered.filter(message => {
                if ($.inArray(message.userstopcode, stops) == -1) {
                    stops.push(message.userstopcode);
                    blockedStops.push(message.dataownercode+"_"+message.userstopcode);
                }
            });

            $.each(blockedStops, function(i, stop) {
                $('[id^=s'+stop+']').append('<span class="glyphicon glyphicon-warning-sign pull-right" title="Halte heeft al een bericht voor deze begintijd"></span>');
                if ($.inArray('s'+stop, selectedStops) !== -1) {
                    $('[id^=ss'+stop+']').addClass('stop_warning');
                    $('[id^=s'+stop+']').addClass('stop_warning');
                    $('#div_id_haltes').addClass('error-label');
                    $("#error_list").append('<p><span class="glyphicon glyphicon-flag" style="color:#a94442"><em class="help" style="color: #a94442"> Halte heeft al een bericht voor deze begintijd</em></span></p>');
                    $("#error_list").removeClass('hidden');
                }
            });
        }
    }
    $('.stopRow td.success').append('<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;');
    writeHaltesField();

}

/* TIME FUNCTIONS */
function checkMessageTime(event, ui) {
    var starttime = parseDate($("#id_messagestarttime").val());
    var endtime   = parseDate($("#id_messageendtime").val());
    if (starttime != 'Invalid Date') {
        if (starttime >= endtime) {
            var new_endtime = starttime;
            if ($(this).attr('id') == "id_messagestarttime") {
                new_endtime.setDate(new_endtime.getDate()+1);
                $("#id_messageendtime").val(formatDate(new_endtime));
            } else {
                starttime.setDate(endtime.getDate()-1);
                $("#id_messagestarttime").val(formatDate(starttime));
            }
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

    var startdate = parseDate($('#id_messagestarttime').val());
    if (startdate != 'Invalid Date') {
        var new_enddate = startdate;
        new_enddate.setDate(new_enddate.getDate()+1);
        $("#id_messageendtime").val(formatDate(new_enddate));
    } else {
        enddate.setDate(enddate.getDate()+1);
        $('#id_messageendtime').val(formatDate(enddate));
    }
}

function epoch(date) {
    return Date.parse(date) / 1000;
}
