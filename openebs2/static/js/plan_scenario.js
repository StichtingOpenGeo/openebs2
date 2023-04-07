/* PLAN SCENARIO FUNCTIONS */

function getScenarioMessages(scenario) {
     var url = '/scenario/'+scenario+'/durationtypes.json';
     $.ajax('/scenario/'+scenario+'/durationtypes.json', {
            success : writeEndtime
     })
}

function writeEndtime(data, status) {
    durationtypes = {'no_endtime': 0, 'endtime': 0}
    if (data.object) {
        $.each(data.object, function (i, message) {
            type = message['messagedurationtype']
            if (type == 'ENDTIME') {
                var amount = durationtypes['endtime']
                durationtypes['endtime'] += 1
            }
            else {
                var amount = durationtypes['no_endtime']
                durationtypes['no_endtime'] += 1
            }
        });
    }
    if (durationtypes['no_endtime'] > 0 && durationtypes['endtime'] == 0) {
        $('#div_id_messageendtime').hide();
        $('.text_about_endtime').addClass('hidden');
    } else if (durationtypes['no_endtime'] > 0 && durationtypes['endtime'] > 0) {
        $('.text_about_endtime').removeClass('hidden');
    } else {
        $('.text_about_endtime').addClass('hidden');
    }
}

function updateEndtime(event) {
    var messagestarttime = parseDate($('#id_messagestarttime').val());
    var messageendtime = parseDate($('#id_messageendtime').val());

    if (messagestarttime > messageendtime) {
        messageendtime.setDate(messagestarttime.getDate() + 1);
        var day = messageendtime.getDate();
        var month = messageendtime.getMonth() + 1;
        var year = messageendtime.getFullYear();
        var end_shift = day +'-'+ month + '-' + year + ' 03:00:00'
        $('#id_messageendtime').val(end_shift);
    }
}


// TIME FUNCTIONS
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
