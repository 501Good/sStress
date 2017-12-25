// DOM is ready
$(document).ready(function () {
  // Bind click event
  $('[data-toggle="tooltip"]').tooltip(); 
  
  $('.checkme').click(function () {
	  var text = document.getElementById("test_text").value;
    
	$.ajax({
		type: "POST",
		url: $SCRIPT_ROOT + "/testme/",
		data: text,
		success: function(data){
			$("#testResultsContainer").html(data);
		}
	});

    return false;
  });
  
  $(".clear").click(function () {
	  $("#test_text").val('');
	  
	  return false;
  });
  
});