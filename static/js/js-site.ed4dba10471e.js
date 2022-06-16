(function($) {
	$(document).ready(function() {
		
		$('.trigger-tabs a').on('click',function(e){
			e.preventDefault();
			var target = $(this).attr('data-target');
			$(this).parent().next('.code-wrap').children('.element-code').hide();
			$(this).parent().next('.code-wrap').children('.element-code-'+target).toggle();
			
		});
		
		$('.menu_rules a').on('click',function(e){
			e.preventDefault();
			var target = $(this).attr('href');
            $('html, body').animate({
                scrollTop: $(target).offset().top
            }, 500);
			$('#menu_mob-trigger,.bs--menu.menu_rules').removeClass("open");
		});

		$('#menu_mob-trigger').on('click', function(e){
			e.preventDefault();
			$(this).toggleClass("open");
			$('.bs--menu.menu_rules').toggleClass("open");
		});

		
		
	});
}(window.jQuery || window.$));