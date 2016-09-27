$(function(){

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

  var showUncontactableWarning = function showUncontactableWarning($selectedOption, $originalSelect, $chosenSelect){
    var $warning = $('<div>').addClass('alert alert-danger uncontactable-alert');
    var warningSentence = interpolate(
      gettext("We do not have contact details for %s."),
      [$selectedOption.text()]);
    var choicesSentence = interpolate(
      gettext("%(open_danger_tag)sRemove this recipient%(close_tag)s or %(open_default_tag)sContribute new contact details%(close_tag)s"),
      {open_danger_tag: '<a class="btn btn-danger btn-sm js-deselect">',
       open_default_tag: '<a class="btn btn-default btn-sm" href="http://example.com" target="_blank">',
       close_tag: '</a>'},
      true);
    $warning.attr('role', 'alert');
    $warning.html(
      '<p>' + warningSentence + '</p><p>' + choicesSentence + '</p>'
    );
    $warning.insertAfter($chosenSelect);
    $warning.on('click', '.js-deselect', function(){
      $selectedOption.attr('selected', false);
      // `chosen:updated` notifies chosen.js that the source <select> has changed.
      // `change` notifies our change listener to update the styling and alerts.
      $originalSelect.trigger('chosen:updated').trigger('change');
    });
  }

  // Render the "uncontactable" styling and warning alerts whenever the
  // selection is changed, or chosen.js loads with pre-selected options.
  $('.chosen-person-select').on('change chosen:ready', function(e){
      var $originalSelect = $(this);
      var $chosenSelect = $originalSelect.next();

      // Remove existing warnings (they'll get recreated if still required).
      $('.uncontactable-alert').remove();

      // Show warnings if the selected options include uncontactable people.
      $('option:selected', $originalSelect).each(function(){
        if( $(this).hasClass('uncontactable') ){
          showUncontactableWarning(
            $(this),
            $originalSelect,
            $chosenSelect
          );
        }
      });

      // Update the styling of the chosen.js tokens for uncontactable people.
      $('.search-choice', $chosenSelect).each(function(){
        var optionArrayIndex = $(this).children('a').attr('data-option-array-index');
        var $originalOption = $originalSelect.find('option').eq(optionArrayIndex);
        if( $originalOption.hasClass('uncontactable') ){
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

  // Hide the errror list - this only shows validation errors from
  // people who are selected but for whom there are no contact
  // details, and the Javascript already displays an error for them:
  $('ul.errorlist').hide();

});
