window.onload = function() {
    document.getElementsByTagName
    els = Array.from(document.getElementsByClassName("to-hide"))
    console.log(els)
    for (el of els){
        el.addEventListener('click', function(e){
            el = e.target.closest(".to-hide")
            console.log("el: " + el)

            classes = el.classList
            console.log("classes: " + classes)

            title = el.getElementsByTagName("h5")[0]
            console.log("title: " + title)

            console.log("cur max-height: " + el.style.maxHeight)
            
            if (classes.contains("hidden")){
                console.log("currently hidden and cur max-height: " + el.style.maxHeight)
                classes.remove("hidden")
                // el.style.maxHeight = "none"
            } else {
                console.log("currently not hidden and cur max-height: " + el.style.maxHeight)
                classes.add("hidden")
                // el.style.maxHeight = 100
            }
        })
    }

};