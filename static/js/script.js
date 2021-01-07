$(document).ready(function(){
    $(".sidenav").sidenav({edge: "right"});
    $(".collapsible").collapsible();
    $(".tooltipped").tooltip();
    $("select").formSelect();
    $('.datepicker').datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 6,
        showClearBtn: true,
        i18n: {
            done: "select"
        }
    });

    validateMaterializeSelect();
    function validateMaterializeSelect() {
        //We create 2 new variables that contain the 2 different stylings of the valid and Invalid bottom borders
        let classValid = { "border-bottom": "1px solid #4caf50", "box-shadow": "0 1px 0 0 #4caf50" };
        let classInvalid = { "border-bottom": "1px solid #f44336", "box-shadow": "0 1px 0 0 #f44336" };
        //if any 'select' element has the property of 'required' we nned to unhide it but make it invisible through CSS properties, we need the 'select' elements to be physically on the DOM
        if ($("select.validate").prop("required")) {
            $("select.validate").css({ "display": "block", "height": "0", "padding": "0", "width": "0", "position": "absolute" });
        }
        //once the user is focused in ("focusin") the <input> on screen, we traverse the DOM up and down with 'parent' and 'children' selctors with event listeners.
        $(".select-wrapper input.select-dropdown").on("focusin", function () {
            $(this).parent(".select-wrapper").on("change", function () {
                //if one of the listed items is selected but doesn't have the 'disabled' class for our default item we'll apply styles to make it valid and green
                if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () { })) {
                    $(this).children("input").css(classValid);
                }
            });
        }).on("click", function () {
            //we'll apply a valid class again if there isn't a valid or invalid class assigned, based on the same DOM-traversing above.
            //the default border is still applied but it will get updated through user selection and we consider it valid
            if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                //Otherwise is the user comes out of the selection and the border was not updated to green it means they didn't properly select anything.
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    //if that's the case we'll apply the red-border class to the input.
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
    }
  });