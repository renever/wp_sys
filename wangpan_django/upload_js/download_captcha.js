var Landing = function() {
	var dlLink = false;
	var showCaptchaEnable = false;
	function roundNumber(num, dec) {
		var result = Math.round(num*Math.pow(10,dec))/Math.pow(10,dec);
		return result;
	}

	function updateTimer(){
		var timer = $(".timer");
		var waittime = timer.attr("data-time");
		var format = timer.attr("data-format");
		if(waittime > 0){
			waittime -= 1;
			timer.html(format.replace("%TIME%", roundNumber(waittime, 0)));
			timer.attr("data-time", waittime);
			setTimeout("Landing.updateTimer()",1000);
		} else {
			if (waittime == 0) {
				$("#popupCaptchaArea").remove();
				$("#navBar3").prepend(captchaArea);
			
				$(window).scrollTop(0);
			}
			setTimeout("Landing.checkDownload()", 1000);
		}
     }
 
	function clickDownloadLink(){
		$('#createTokenForm').submit(function(){
			$('#createTokenFormSubmit').attr('disabled', 'disabled');
			return true;
		});
	}

	function ready(downloadLink){
		dlLink = downloadLink;
		$("#regularBtn").click(function(){
            $('#errorBox').hide();
			$("#regularBtn").unbind('click');
			showTimer();
			return false;
		});
	}

	function submitAfter(){
		$.post(dlLink, {'downloadLink': 'show'}, function(data) {
			if(data == 'fail'){
				location.reload(true);
			 }else if( data == 'fail404'){
			 	location.href = '/error-404.html';
			 }else if(data == 'forcePremiumDownload_exceed_2') {
				 location.href = '/l-error.php?error_code=610';
			 }else if(data == 'forcePremiumDownload_exceed_3') {
				 location.href = '/l-error.php?error_code=611';
			 }else if(data == 'forcePremiumDownload_exceed_4') {
				 location.href = '/l-error.php?error_code=613';
			 }else if(data == 'forcePremiumDownload_exceed_5') {
				 location.href = '/l-error.php?error_code=614';
			 }else if(data == 'forcePremiumDownload_exceed_6') {
				 location.href = '/l-error.php?error_code=615';
			 }else{
				$('#captchaArea').hide();
				$('#downloadBox').show();
				
				$('#showTimer').hide();
				$('#showSlowDownload').show();
				$('#showPremiumPlan').hide();
				$("#regularBtn3").click(function(){
					$("#regularBtn3").unbind('click');
					$("#regularForm").submit();
				    return false;
				});
				$("body").append(data);
			}
		});
	}
	
	return {
		ready : ready,
		updateTimer : updateTimer,
		clickDownloadLink : clickDownloadLink,
		submitAfter : submitAfter,
		checkDownload : checkDownload
	};

	function showTimer() {
		$("#captchaArea").css("display","none");
		$('#showPremiumPlanSmallTxt').hide();
		$.post(dlLink, {'downloadLink': 'wait'}, function(data) {
			if(data == 'fail'){
				location.reload(true);
			 }else if( data == 'fail404'){
			 	location.href = '/error-404.html';
			 }else{
				$('#showTimer').show();
				$("#regularBtn, #regularBtn2, #regularBtn3").unbind('click');
				if(data.waitTime){
					$('#timer').html(data.waitTime);
					if(data.display){
						$('body').append(data.display);
					}
				}else{
					$('#timer').html(data);
			 	}
				updateTimer();
			}
		}, 'json');
	}
	
	function submitCaptcha() {
		$.ajax({
			type: "POST",
			url: "/checkReCaptcha.php",
			data: ({
				recaptcha_challenge_field:$("#recaptcha_challenge_field").val(),
				recaptcha_response_field:$("#recaptcha_response_field").val(),
				recaptcha_shortencode_field:$("#recaptcha_shortencode_field").val()
			}),
			success: function(msg){
				var captchaResult = eval('(' + msg + ')');
				if(captchaResult.success){
					$('#captchaError').hide();
					submitAfter();
				}else{
					if(captchaResult.error=="captcha-fail"){
						submitErrorForm('captchaFail', captchaResult.msg);
					}else{
						$("#captchaError").html("Invalid Captcha! Please try again.");
						showCaptcha();
					}
				}
			}
		});
	}
	
	function chooseBtwCaptchaTimer(){
		$.ajax({
			type: "POST",
			url: "/selectCaptchaTimer.php",
			data: ({
				recaptcha_shortencode_field:$("#recaptcha_shortencode_field").val()
			}),
			success: function(msg){
                msg = jQuery.trim(msg);
				if (msg=="1") {
					$("#regularBtn").click(function(){
						submitCaptcha();
						return false;
					});				
					showCaptcha();
				} else {
					showTimer();
				}
			}
		});
  }
						
	function checkDownload() {
		$.ajax({
			type: "POST",
			dataType: "json",
			data: "checkDownload=check",
			success: function(json){
				if(json.fail != undefined){
					submitErrorForm(json.fail, json.waitTime);
					return false;
				}else if(json.success != undefined){
					switch(json.success){
						case 'showCaptcha':
					//		submitAfter();
					//		break;
							$("#regularBtn").unbind('click');
							$("#regularBtn2").click(function(){
								submitCaptcha();
								return false;
							});
							showCaptcha();
							$('#captchaArea').show();
							break;
						case 'showTimer':
							showTimer();
							break;
					}
				}
			}
		});
	}
}();

function submitErrorForm(errorType, waitTime) {
	var regularForm3 = '<form id="regularForm3" method="post"><input type="hidden" name="checkDownload" value="showError"/>';
	regularForm3 += '<input type="hidden" name="errorType" value="'+errorType+'"/>';
	if(waitTime != undefined)
		regularForm3 += '<input type="hidden" name="waitTime" value="'+waitTime+'"/>';
	regularForm3 += '</form>';
	$('body').append(regularForm3);
	$("#regularForm3").submit();
}

function showCaptcha() {
    var RecaptchaOptions = {
        theme: 'custom',
        lang: 'en',
        custom_theme_widget: 'recaptcha_widget',
        callback: function(){$('#captchaArea').show();Recaptcha.focus_response_field;}
    };
    Recaptcha.create(reCAPTCHA_publickey,
        "captchaArea", RecaptchaOptions);

	//window.scrollTo(0, $(document).height());
}