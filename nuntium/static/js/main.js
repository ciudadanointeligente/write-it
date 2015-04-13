 $(function() {

  // clicking on a link with class="help-loader"
  // attempts to pull in help text specified by the href URL
  // and places it in a tooltip-like popup.

  $('.help-loader').on('focus', function(e){
    var $trigger = $(this);
    loadHelpContent($trigger).done(function(response){
      showPopover($trigger, response);
    }).fail(function(response){
      showError($trigger, response);
    });
  }).on('blur', function(e){
    hidePopover($(this));
  }).on('click', function(e){
    e.preventDefault();
  });

  var loadHelpContent = function loadHelpContent($trigger){
    var dfd = $.Deferred();
    var sourceUrl = $trigger.attr('href');
    if (sourceUrl.indexOf('#') > -1) {
      var urlParts = sourceUrl.split('#');
      $.ajax({
        url: urlParts[0]
      }).done(function(response){
        var targetElement = $(response).find('#help-' + urlParts[1]);
        if(targetElement.length){
          dfd.resolve(targetElement.html());
        } else {
          dfd.reject('Ajax call completed, but the target element #help-' + urlParts[1] + ' could not be found in the returned page.');
        }
      }).fail(function(jqXHR){
        dfd.reject('Ajax request failed ' + jqXHR.status + ' ' + jqXHR.statusText);
      });
    } else {
      dfd.reject('Glossary link does not include a #fragment!');
    }
    return dfd.promise();
  };

  var showPopover = function showPopover($trigger, content){
    $trigger.popover({
      content: content,
      html: true,
      placement: 'auto right',
      trigger: 'manual'
    }).popover('show');
  };

  var hidePopover = function hidePopover($trigger){
    $trigger.popover('destroy');
  };

  var showError = function showError($trigger, error){
    var html = '<p>Read more on the help page at: <a href="' + $trigger.attr('href') + '">' + $trigger.attr('href') + '</a></p>';
    showPopover($trigger, html);
  };

});
