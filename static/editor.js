// Javascript Item Editor
// Inventory App!  Cool!
// Patrick Pragman
// 7/18/2021
// All vanilla javascript in here for now.
// This is making me realize I hate javascript.

var item_editor_div_name = "item_editor"  // this is editable if I decide to change the nomenclature here
var item_editor_div = document.getElementById(item_editor_div)
var username = document.cookie

function get_request(pathway) {
    // send an XML HTTP Request to the server
    var xhttp = new XMLHttpRequest();
    alert("Here!")
    xttp.onreadystatechange = function(){
        //once the
        console.log(xhttp.onreadystatechange);
        if (this.readyState == 4 && this.status == 200){
            console.log(xhttp.responseText); // debug
            return xhttp.responseText;
        }
    };
    xhttp.open("GET", pathway, true)
    xhttp.send();
};