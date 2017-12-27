// DOM is ready
$(document).ready(function () {
  // Bind click event

  $('.pushme').click(function () {
	  var text = document.getElementById("lstm_text").value;
    
    if ($("#ServerKey").val() === "lstm") {
    	$.ajax({
    		type: "POST",
    		url: $SCRIPT_ROOT + "/predict/",
    		data: text,
    		success: function(data){
    			$("#resultsContainer").html(data);
    		}
    	});

        return false;
    } else if ($("#ServerKey").val() === "rules") {
        $.ajax({
            type: "POST",
            url: $SCRIPT_ROOT + "/predict_rules/",
            data: text,
            success: function(data){
              $("#resultsContainer").html(data);
            }
        });

        return false;
    }
    });
  
  $(".clear").click(function () {
	  $("#lstm_text").val('');
	  
	  return false;
  });
});