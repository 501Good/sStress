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
			$("#testResultsContainer").html(data.result);
            $("#testScoreContainer").html('<div id="example"  class="pie-title-center" data-percent="0"><span class="pie-value"></span></div>');
            $('#example').attr('data-percent', data.percent * 100);
            $("#example").pieChart({
                        barColor: '#68b828',
                        trackColor: '#eee',
                        lineCap: 'round',
                        lineWidth: 8,
                        onStep: function (from, to, percent) {
                            $(this.element).find('.pie-value').text(Math.round(percent) + '%');
                        }
                    });
		}
	});

    return false;
  });
  
  $(".clear").click(function () {
	  $("#test_text").val('');
	  
	  return false;
  });
  
});