$(function(){

  if(window.who.rtl) {
    $(".chosen-person-select").addClass('chosen-rtl');
  }
  $(".chosen-person-select").chosen({
    width: '100%',
    max_selected_options: window.who.max_selected_options,
    no_results_text: window.who.no_results_text,
    placeholder_text_multiple: ' ', // hide placeholder text
    placeholder_text_single: ' ', // hide placeholder text
    single_backstroke_delete: false
   });

});
