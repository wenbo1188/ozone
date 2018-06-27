tinymce.init({
	selector: 'textarea',
	directionality:'ltr',
	language:'zh_CN',
	height:400,
	plugins: [
		'advlist autolink link image lists charmap print preview hr anchor pagebreak spellchecker','searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking','save table contextmenu directionality emoticons template paste textcolor',],
	toolbar: 'undo redo | \
		     styleselect | \
			 bold italic | \
			 alignleft aligncenter alignright alignjustify | \
		     bullist numlist outdent indent | \
			 link image | \
			 print preview media fullpage | \
			 forecolor backcolor emoticons |\
			 fontsizeselect fullscreen',
	fontsize_formats: '10pt 12pt 14pt 18pt 24pt 36pt',
	nonbreaking_force_tab: true,
});
	
