var selectedStops = []

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
        for (key in data.object_list) {
            line = data.object_list[key]
                validIds.push('l'+line.pk)
                if (!$('#l'+line.pk).length) {
                    row = '<tr class="line" id="l'+line.pk+'"><td>'+line.lineplanningnumber+ '</td>'
                        row += '<td>'+line.headsign+'</td></tr>'
                        $(row).hide().appendTo("#rows").fadeIn(999)
                }
        }
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
    $(this).addClass('success');
    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    $.ajax('/line/'+$(this).attr('id').substring(1)+'/stops', {
        success : writeLine
    })
    $(this).addClass('success')
}

function selectStop(event) {
    $('#halte-list .help').remove()
    if (event.ctrlKey) {
        if ($(this).hasClass('stop-left')) {
            selectStopLeftEnd(this);
        } else if ($(this).hasClass('stop-right')) {
            selectStopRightEnd(this);
        }
    } else {
        if (selectStopInner(this)) {
            writeHaltesField();
        }
    }
}

function selectStopBoth(event) {
    $('#halte-list .help').remove()

    var result = false;
    result |= selectStopInner($(this).parent().prev(".stop-left"));
    result |= selectStopInner($(this).parent().next(".stop-right"));

    if (result) {
        writeHaltesField();
    }
}

function selectStopLeft(event) {
    $('#halte-list .help').remove()
    if (selectStopInner($(this).parent().prev(".stop-left"))) {
        writeHaltesField();
    }
}

/* TODO: deze twee functies werken niet, omdat ik jQuery nog niet helemaal snap. */

function selectStopRight(event) {
    $('#halte-list .help').remove()
    if (selectStopInner($(this).parent().next(".stop-right"))) {
        writeHaltesField();
    }
}

function selectStopLeftEnd(start) {
    var result = false;
    for (obj in $(start).parent().parent().prevAll(".stop-left")) {
            result |= selectStopInner(obj);
    }

    return result;
}

function selectStopRightEnd(start) {
    var result = false;
    for (obj in $(start).parent().parent().nextAll(".stop-right")) {
        result |= selectStopInner(obj);
    }

    return result;
}

function selectStopInner(obj) {
    if ($.inArray($(obj).attr('id'), selectedStops) == -1) {
        $(obj).addClass('success')
        $(obj).append('<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;')
        selectedStops.push($(obj).attr('id'));
        if ($(obj).hasClass('stop-left')) {
            direction = "heen";
        } else {
            direction = "trg";
        }
        delLink = '<span class="stop-remove glyphicon glyphicon-remove"></span>';
        $("#halte-list").append('<span class="stop-selection pull-left label label-primary" id="s'+$(obj).attr('id')+'">'+$(obj).text()+'('+direction+') '+delLink+ '</span>');

        return true;
    }

    return false;
}

function writeHaltesField() {
    out = ""
    for (item in selectedStops) {
        if (selectedStops[item] !== undefined) { /* Don't know why this is required, array gets undefined entries. */
            out += selectedStops[item].substring(1)+",";
        }
    }
    $("#haltes").val(out)
}

/* Wrapper functions to get the id */
function selectionRemoveStop(event) {
    removeStop($(this).parent().attr('id').substring(1))
}

function lineRemoveStop(event) {
    removeStop($(this).attr('id'))
}

/* Do the actual work here */
function removeStop(id) {
    var i = $.inArray(id, selectedStops);
    if (i != -1) {
        selectedStops.splice(i, 1);
        $("#s"+id).remove();
        $("#"+id).removeClass('success')
        $("#"+id+" .stop-check").remove()
        writeHaltesField()
    }
}

function writeLine(data, status) {
    $('#stops').fadeOut(200).empty();
    out = ""
    for (key in data.object.stop_map) {
        out += renderRow(data.object.stop_map[key])
    }
    $('#stops').append(out)
    $('#stops').fadeIn(200);
}

function renderRow(row) {
    out = '<tr>';
    if (row.left != null) {
        var id = 's'+row.left.id;
        if ($.inArray(id, selectedStops) != -1) {
            out += '<td class="stop stop-left success" id="'+id+'">'+row.left.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;</td>';
        } else {
            out += '<td class="stop stop-left" id="'+id+'">'+row.left.name+'</td>';
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
        var id = 's'+row.right.id;
        if ($.inArray(id, selectedStops) != -1) {
            out += '<td class="stop stop-right success" id="'+id+'">'+row.right.name+'<span class="stop-check glyphicon glyphicon-ok-circle pull-right"></span>&nbsp;</td>';
        } else {
            out += '<td class="stop stop-right" id="'+id+'">'+row.right.name+'</td>';
        }
    } else {
        out += '<td>&nbsp;</td>';
    }
    out += '</tr>';
    return out
}