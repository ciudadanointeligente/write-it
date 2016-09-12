$(function(){

  // Temporarily add the "uncontactable" class to a random selection
  // of contacts in the person selector.
  // TODO: This should be done in forms.py > PersonMultipleChoiceField
  $('.chosen-person-select option').each(function(i){
    if( Math.random(0, 1) <= 0.2 ){
      $(this).addClass('uncontactable');
    }
  });

  // Copy the "uncontactable" class from the original dropdown `<option>`s,
  // onto the chosen.js dropdown `<li>`s.
  $('.chosen-person-select').on('chosen:showing_dropdown', function(e, params){
    var $options = $(params.chosen.dropdown[0]).find('li');
    $options.each(function(i){
      var originalOptElement = params.chosen.results_data[i];
      if(originalOptElement.classes.indexOf('uncontactable') !== -1){
        $(this).addClass('uncontactable');
      }
    });
  });

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
