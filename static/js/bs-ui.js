(function($) {
	$(document).ready(function() {
// Code
// Alert
		$('.bs--alert-close').on('click',function(e){
			e.preventDefault();
			$(this).parent().slideUp(200);
		});		

// Menu
		$('.bs--menu-item').on('click',function(){
			$(this).parent().children('.bs--menu-item').removeClass('active');
			$(this).addClass('active');
		});		
// Media elements
		$('audio').each(function(){
			$(this).mediaelementplayer({
				success: function(mediaElement, originalNode, instance) {}
			});
		})
		$('video').each(function(){
			$(this).mediaelementplayer({
				success: function(mediaElement, originalNode, instance) {}
			});
		})
// Color input
		$('input[type=color]').on('change', function() {
			$(this).parent().css('backgroundColor', $(this).val() );
		});
// Input number
		$('input[type=number]').each(function(){
			var min = $(this).attr('min') || false;
			var max = $(this).attr('max') || false;
			
			var plusminus = {};
			
			plusminus.dec = $(this).prev();
			plusminus.inc = $(this).next();
			
			$(this).each(function() {
				init($(this));
			});
			
			function init(el) {
				
				plusminus.dec.on('click', decrement);
				plusminus.inc.on('click', increment);
				
				function decrement() {
					var value = el[0].value;
					value--;
					if(!min || value >= min) {
						el[0].value = value;
					}
				}
			
				function increment() {
					var value = el[0].value;
					value++;
					if(!max || value <= max) {
						el[0].value = value++;
					}
				}
			}
		});
// Datepicker
		$('.bs--datepicker').each(function(){
			$(this).datepicker({language: 'fr', todayButton: new Date() , startDate : new Date() });
		});
		$('.bs--datepicker-time').each(function(){
			$(this).datepicker({language: 'fr', timepicker: true,  todayButton: new Date() , startDate : new Date() });
		});
		


	});
}(window.jQuery || window.$));