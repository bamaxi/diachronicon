index_regex = /(?<=change-)\d/g

var tableCount = 1



function add_another_change() {


    // get table parent - <li> (since applying .html() to <table> will give <tbody>
    orig_fieldset = document.querySelector("fieldset[name=changes]");
    console.log(orig_fieldset)
    console.log(typeof(orig_fieldset))
    fieldset = Object.assign(orig_fieldset);

    // leave only csrf tag in <input> and the table (deleting <h3> with form name for example)
    // fieldset.children().not("table, input").remove()

    // put the correct ids into place
    fixed = fieldset.innerHTML.replace(index_regex, tableCount);
//    fieldset.outerHTML = fixed;


////    code = `<div><li><h3>Словоформа ${tableCount + 1}</h3><table></table></li></div>`
//    code = `<div><li><h3>Словоформа ${tableCount + 1}</h3></li></div>`
//    new_table = $(code)
//    $("table", new_table).attr("id", `tokens_list-${tableCount}`)
////        .append(table.html())
//    $("li", new_table).append(table.html())
////    alert(new_table.html())

    orig_fieldset.parentNode.insertBefore(fieldset, orig_fieldset.nextSibling);

    fieldset.innerHTML = fixed;
    tableCount++;
}
