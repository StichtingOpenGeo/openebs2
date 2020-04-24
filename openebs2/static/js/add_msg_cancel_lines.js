/* SHOW_LINE FUNCTIONS */

function changeSearchBlocks(event) {
      $.ajax('/line/'+$("#line_search").val(), {
          success : writeBlocks
      })
}

function writeBlocks(data, status) {
    validIds = []
    /* Add them all, as neccesary */
    $.each(data.object_list, function (i, line) {
        validIds.push('l'+line.pk)
        if (!$('#l'+line.pk).length) {
            row = '<div class="lineblock" id="l'+line.pk+'" title="'+line.headsign+'"><link rel=>'+line.publiclinenumber+'</div>';
            $(row).hide().appendTo("#lineblocks").fadeIn(999);
        }
    });

    /* Cleanup */
    $("#lineblocks div").each(function(index) {
        if ($.inArray($(this).attr('id'), validIds) == -1) {
            $(this).fadeOut(999).remove()
        }
    });
}


/* LINE SELECTION */
var selectedLines = [];
var activeLines = [];

function selectLineBlocks(event, ui) {
    var lijn = $(ui.selected).attr('id').substring(1);
    if ($.inArray(parseInt(lijn), activeLines) != -1) /* Note our array stores numbers, so convert */
        return;

    var id = $.inArray(lijn, selectedLines);
    if (id == -1) {
        $('#lijn-list .help').hide();
        $(ui.selected).addClass('success');
        var label = $(ui.selected).text();
        var dellink = '<span class="line-remove glyphicon glyphicon-remove"></span>';
        $('#lijn-list').append('<span id="st'+lijn+'" class="pull-left line-selection label label-danger">'+label+' '+dellink+'</span>');
        selectedLines.push(lijn);
        writeLinesList();
    } else {
        removeLine($(ui.selected).attr('id').substring(1));
    }
}

function writeLinesList() {
    var out = "";
    $.each(selectedLines, function(index, val) {
        out += val+',';
    });
    $("#lijnen").val(out)
}

function removeLineFromX(event, ui) {
    removeLine($(this).parent().attr('id').substring(2));
}

function removeLine(lijn) {
    var id = $.inArray(lijn, selectedLines);
    if (id != -1) {
        $('#l'+lijn).removeClass('success');
        $('#st'+lijn).remove();
        selectedLines.splice(id, 1);
    }
    if (selectedLines.length == 0) {
        $('#lijn-list .help').show();
    }
    writeLinesList();
}

function writeLines(data, status) {
    $('#trips tbody').fadeOut(200).empty();
    lineRows = null
    maxLen = Math.max(data.object.trips_1.length)
    for (i = 0; i <= maxLen; i = i + 1) {
        a = null
        if (i in data.object.trips_1)
            a = data.object.trips_1[i]
        lineRows += renderLine(a);
    }
    $('#trips tbody').append(lineRows)
    $('#trips tbody').fadeIn(200);
}

function renderLine(line_a) {
    out = '<tr>';
    out += renderLineCell(line_a);
    out += '</tr>';
    return out
}

function renderLineCell(line) {
    if (line == null)
        return "<td>&nbsp;</td>";

    if ($.inArray(line.id, activeLines) != -1) {
        out = '<td class="line warning" id="t'+line.id+'">'
    } else {
        out = '<td class="line" id="t'+line.id+'">'
    }
    out += "<strong>Lijn "+line.publiclinenumber+"</strong>"
    if ($.inArray(line.id, activeLines) != -1) {
        out += '<span class="glyphicon glyphicon-warning-sign pull-right" title="Lijn is al opgeheven"></span>'
    }
    out += "</td>"
    return out
}

function changeOperatingDayLines() {
    $("#lijn-list span").remove();
    $('#lijn-list .help').show();
    activeLines = [];
    selectedLines = [];

    $("#lijnen").val('');
    $("#lineblocks > .success").removeClass('success');

    changeSearchBlocks();
    var operating_day_text = $("#id_operatingday option:selected" ).text();
    $("#operating_day_text").text(operating_day_text);
}

function notMonitored() {
    $("#notMonitored").text($(this).text());
    $("#notMonitoredInput").val($(this).attr('value'));
    $("#notMonitored").removeClass('disabled');
}
