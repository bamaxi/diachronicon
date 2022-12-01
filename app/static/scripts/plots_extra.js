var change_links = document.getElementsByClassName('changes-toggle');
//var change_divs = document.getElementsByClassName('changes');


function load_chart(event) {
//    event.preventDefault(); // prevent page from refreshing

    //this should work, very strange that it doesn't
    //console.log(event.currentTarget)
    //let data = new FormData(event.currentTarget); // grab the data inside the form fields
    //console.log(data);
    //values = Object.fromEntries(data.entries())
    //console.log(values)
    changes_link = event.currentTarget
    console.log(changes_link)
    changes_div_id = changes_link.getAttribute('aria-controls')
    console.log(changes_div_id)
    changes_div_id_parts = changes_div_id.split('-')
    i = changes_div_id_parts[changes_div_id_parts.length - 1]
    console.log(i)

    chart_div = changes_div.getElementsById('')

//    let data2 = new Object();
//    for (let inp of event.currentTarget) {
//        data2[inp.id] = inp.value
//    };
//
//    console.log(data2)
//    json_data = JSON.stringify(data2)
//    console.log(json_data)
//
//    console.log('sending xhr data')
//    var xhr = new XMLHttpRequest;
//    xhr.open('POST', '/send-report', true);
//    xhr.send(json_data);
//
//    $(destElem).html('<img src="{{ url_for('static', filename='loading.gif') }}">');
//    $.post('/translate', {
//        text: $(sourceElem).text(),
//        source_language: sourceLang,
//        dest_language: destLang
//    }).done(function(response) {
//        $(destElem).text(response['text'])
//    }).fail(function() {
//        $(destElem).text("{{ _('Error: Could not contact server.') }}");
//    });

    //console.log('sending xhr form')
    //var xhr = new XMLHttpRequest;
    //xhr.open('POST', '/report', true);
    //xhr.send(event.currentTarget);

    //console.log('sending xhr serialised')
    //var xhr = new XMLHttpRequest;
    //xhr.open('POST', '/report', true);
    //xhr.send(event.currentTarget);


    ////res = event.currentTarget.serializeArray()
    //console.log(event.currentTarget.attributes);
    //console.log(event.currentTarget.getAttribute('id'));
    //console.log($('#' + event.currentTarget.getAttribute('id')));
    //$('#' + event.currentTarget.getAttribute('id')).each(function () { console.log(this) });

    //res = $('#' + event.currentTarget.getAttribute('id')).serializeArray();
    //console.log(res);

    //res2 = $('#' + event.currentTarget.getAttribute('id')).serialize();
    //console.log(res2);

    //console.log($('#' + event.currentTarget.getAttribute('id'))[0])
    //console.log(event.currentTarget[2])

    //console.log(data2)
};

console.log(change_links)

for (var i = 0; i < change_links.length; i++) {
    change_links[i].addEventListener("click", load_chart)
};