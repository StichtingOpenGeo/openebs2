var selectedStops = []

function changeSearch(event) {
    if ($("#line_search").val().length > 0) {
        $.ajax('/line/'+$("#line_search").val(), {
            success : writeList
        })
    }
}

function changeCount(event) {
    console.log("Count");
    len = $(this).val().length
    addon = $(this).parent().find('.input-group-addon')[0]
    $(addon).text(len+" tekens");
    $(addon).parent().removeClass('has-warning has-error')
    if (len > 150 && len < 250) {
       $(addon).parent().addClass('has-warning')
    } else if (len > 249) {
       $(addon).parent().addClass('has-error')
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
    $(this).children('td').eq(1).append('<span class="suc-icon pull-right glyphicon glyphicon-arrow-right"></span>');
    $.ajax('/line/'+$(this).attr('id').substring(1)+'/stops', {
        success : writeLine
    })
    $(this).addClass('success')
}

function selectStop(event, ui) {
    $('#halte-list .help').remove()

    if (doSelectStop(ui.selected)) {
        writeHaltesField();
    }
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
    out = ""
    for (item in selectedStops) {
        if (selectedStops[item] !== undefined) { /* Don't know why this is required, array gets undefined entries. */
            out += selectedStops[item].substring(1)+",";
        }
    }
    $("#haltes").val(out)
}

/* Do the inverse in case we're editing or something */
function readHaltesField() {
    initialHaltes = $("#haltes").val().split(',');
    for (halte in initialHaltes) {
        if(initialHaltes[halte] != "") {
            selectedStops.push('s'+initialHaltes[halte])
        }
    }
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
    for (key in data.object.stop_map) {
        out += renderRow(data.object.stop_map[key])
    }
    $('#stops').append(out)
    $('#stops').fadeIn(200);
}

function renderRow(row) {
    out = '<tr>';
    if (row.left != null) {
        var id = 's'+row.left.id+'l';
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
        var id = 's'+row.right.id+'r';
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