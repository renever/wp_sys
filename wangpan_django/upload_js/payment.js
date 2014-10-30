var Payment = function() {
	function doPaymentRequest(campaign_id, method_id){
    var auto_click = false;
		$.ajax({
      type: "POST",
      url: "/payment.php",
      async: false,
      data: "campaign="+campaign_id+"&paymentMethod="+method_id+"&campaignSelectSubmit=campaignSelectSubmit&special=ajaxRequest",
      success: function(msg){
        //alert(msg);
        $("#private_area").html("");
        $("#private_area").html(msg);
        if ($("#privte_form").get().length != 0) {
          $("#privte_form").submit();
        }
        else if ($("#campaign_"+campaign_id+"_"+method_id).get().length != 0) {
          tb_init("a."+$("#campaign_"+campaign_id+"_"+method_id).attr("class"));//pass where to apply thickbox
          auto_click = true;
        }
        else {
          alert("Payment Gateway is now disabled. Please try again later.");
        }
      }
    });
    if (auto_click) {
      $("#campaign_"+campaign_id+"_"+method_id).click();
    }
	}

	return {
		doPaymentRequest : doPaymentRequest
	}
}();
