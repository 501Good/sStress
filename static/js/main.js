// DOM is ready
$(document).ready(function () {
  // Bind click event
  $('.pushme').click(function () {
	  var text = document.getElementById("lstm_text").value;
    
	$.ajax({
		type: "POST",
		url: $SCRIPT_ROOT + "/predict/",
		data: text,
		success: function(data){
			document.getElementById("lstm_text").value = data;
		}
	});

    return false;
  });
});