//sort through scroll to the first div that matches
//Pat Pragman
//8/6/2021 with help from W3 Schools

function search(class_to_search){
    //this fires whenever the search bar or the sort by dropdown changes
    // first let's get the search bar and the select menu so we can tinker with their values
    var search_bar = document.getElementById("search_bar");

    var filter = search_bar.value.toUpperCase();
    var edit_boxes = document.getElementsByClassName(class_to_search);
    var i; //for iterating - i get it.... sorry
    var div;

    //adapted from code at w3 schools
    //this iterates through the customer edit boxes, makes a div to mess with
    //then finds the index of the filter in the class name
    for (i = 0; i < edit_boxes.length; i++) {
        div = edit_boxes[i]; // get one of the divs with customer edit info
        var txtValue = div.className;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            div.style.display = "";
        } else {
            div.style.display = "none";
        }
    }

}