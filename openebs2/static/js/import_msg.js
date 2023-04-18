/* IMPORTING and CHECKING XML-MESSAGE FUNCTIONS */

function getMessage() {
    $('.import-field').addClass('hidden');
    $('.check-import').removeClass('hidden');
    var xml = $('#import-text').val().toLowerCase();
    var xmlDoc = $.parseXML(xml);
    var $xml = $(xmlDoc);
    var $title = $xml.find("stopmessage");

    var dataownercode = $title.find('dataownercode').text().toUpperCase();
    var messagecodedate = $title.find('messagecodedate').text();
    var messagecodenumber = $title.find('messagecodenumber').text();
    var volgnummer = dataownercode + ' - ' + messagecodedate + ' - #' + messagecodenumber;
    $('#volgnummer-regel').text(volgnummer);

    var messagecontent = $title.find('messagecontent').text();
    $('#bericht-regel').text(messagecontent);

    var messagestarttime = $title.find('messagestarttime').text().replace('t', ' ').split("+")[0];
    var line = messagestarttime.split(' ')[0].replace(/(\d{4})-(\d\d)-(\d\d)/, '$3-$2-$1') + ' '+messagestarttime.split(' ')[1].slice(0,-3) + ' - '// reformat to dd-mm-yyyy HH:mm
    var messageendtime = $title.find('messageendtime').text().replace('t', ' ').split("+")[0];
    if (messageendtime.length > 1) {
        var endtime = new Date(Date.parse(messageendtime, "dd/mm/yyyy HH:mm"));
        var starttime = new Date(Date.parse(messagestarttime, "dd/mm/yyyy HH:mm"));

        var start = Date.UTC(starttime.getFullYear(), starttime.getMonth(), starttime.getDate());
        var end = Date.UTC(endtime.getFullYear(), endtime.getMonth(), endtime.getDate());
        var diff = Math.floor((end - start) / (1000 * 60 * 60 * 24))
        if (diff == 0) {
            line += messageendtime.split(' ')[1].slice(0,-3);
        } else if (diff == 1) {
            line += messageendtime.split(' ')[1].slice(0,-3) + ' (+1)';
        }
    }
    $('#geldigheid-regel').text(line);

    var userstopcodes = $title.find('userstopcodes').text();
    var messagepriority = $title.find('messagepriority').text();
    var messagetype = $title.find('messagetype').text();
    var messagedurationtype = $title.find('messagedurationtype').text();

    var messagetimestamp = $title.find('messagetimestamp').text();

    reasontype = $title.find('reasontype').text();
    subreasontype = $title.find('subreasontype').text();
    reasoncontent = $title.find('reasoncontent').text();
    effecttype = $title.find('effecttype').text();
    subeffecttype = $title.find('subeffecttype').text();
    effectcontent = $title.find('effectcontent').text();
    measuretype = $title.find('measuretype').text();
    submeasuretype = $title.find('submeasuretype').text();
    measurecontent = $title.find('measurecontent').text();
    advicetype = $title.find('advicetype').text();

}