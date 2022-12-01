const logic = import('./form_parsers/logic_query.js');

INVALID_FORM_STYLE = {
    'border': '2px solid red',
    'border-radius': '0.375rem',
    'padding': '2px',
}

function setStyle(elem, propertyObject)
{
// var elem = document.getElementById(objId);
 for (var property in propertyObject)
    elem.style[property] = propertyObject[property];
}

let get_id = (id) => document.getElementById(id);
let get_classed = (className) => document.getElementsByClassName(className);

form = get_id('search-form')
form_error = get_id('form-error')

//let grammar_validate = (el)

inputs = document.getElementsByTagName("input")
errors = get_classed("error")

failureIcons = get_classed("failure-icon")
successIcons = get_classed("success-icon")

console.log([inputs.length, errors.length, failureIcons.length, successIcons.length])

if (inputs.length != errors.length
//    | inputs.length != failureIcons.length
//    | failureIcons.length != successIcons.length
){
    throw "error"
}

let check_all = (message) => {
    var any_filled = false;

    console.log(any_filled)

    for (var i = 0; i < inputs.length; i++){
        el = inputs[i]
        type = el.type
        val = el.value
        id = el.id

        console.log(i, val, type, id, typeof(val))

        if (type === 'text' && val.trim() !== ""
            || type === 'checkbox' && el.checked){
            any_filled = true;
            break;
        }
    }

    if (any_filled){
        form_error.innerHTML = ""
        form.style = ""
    }
    else {
        form_error.innerHTML = message
        setStyle(form, INVALID_FORM_STYLE)
    }

    console.log(any_filled);
    return any_filled
}


form.addEventListener("submit", (e) => {
    console.log("caught");

    var any_filled = check_all("Хотя бы одно из полей должно быть заполнено");
    if (!any_filled){
        e.preventDefault();
    }
});



