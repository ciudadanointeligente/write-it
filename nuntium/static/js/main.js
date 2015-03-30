 $(function() {
   
  // clicking on a link with class="help-loader"
  // attempts to pull in help text specified by the href URL
  // and places it in the element specified by data-target attribute.
  // If no data-target attribute is specified, try to show it in
  // a tooltip-like popup instead.

  $('.help-loader').on("click", function(e){
    console.log("help-loader on click event triggered...");
    e.preventDefault();
    var help_id_prefix = "help-";
    var data_is_loaded = "is-loaded";
    var $target_for_text = null;
    var custom_target_for_text = $(this).data("target");
    console.log("target for displaying the help in is: " + custom_target_for_text);
    if (custom_target_for_text){
      $target_for_text = $(custom_target_for_text);
    }
    var help_text_source_url = $(this).attr('href');
    if (help_text_source_url) {
      var anchor_position = help_text_source_url.indexOf('#');
      if (anchor_position > -1 && help_text_source_url.length-anchor_position > 1) {
        // split the URL to get the id
        // this works because/if there is an id matching the anchor name
        // actually we're just adding a space in front of the #
        help_text_source_id = help_text_source_url.substr(anchor_position + 1);
        if (help_text_source_id && help_text_source_id.indexOf(help_id_prefix) != 0) {
          help_text_source_id = help_id_prefix + help_text_source_id;
        }
        help_text_source_url = help_text_source_url.substr(0, anchor_position)
          + " #" + help_text_source_id;
          console.log("help is available at: " + help_text_source_url);
      } else {
        console.log("no id specified to get the help from... whole page is probably wrong, aborting");
        $(this).hide();
        return;
      }
      if (! $target_for_text) {
        console.log("creating a target, adding it to the thing that was clicked...");
        var new_target = "help-hint-" + help_text_source_id;
        $target_for_text = $("<div class='help-hint'/>").attr('id', new_target);
        $(this).data('target', "#" + new_target);
        $(this).after($target_for_text);
      }
      if (! $(this).data(data_is_loaded)) {
        console.log("making AJAX call to " + help_text_source_url);
        $(this).data(data_is_loaded, true);
        $target_for_text.load(help_text_source_url, function(response, status, xhr){
          if ( status == "error" ) {
            $target_for_text.html("Unable to get help text:<br>(" +
              xhr.status + " " + xhr.statusText +")");
          } else {
              // if the response is actually a <dt> element
              // e.g., from the glossary -- need to change it to a div and maybe
              // presenve the id too
            console.log("Got response (" + response.length + " bytes)");
            var $children = $target_for_text.children();
            if ($children.length === 1) {
              var $only_child = $children.first();
              if ('DD' === $only_child.prop("tagName").toUpperCase()) {
                $only_child.detach();
                var $new_div = $("<div/>");
                var id = $only_child.attr('id');
                var $orphans = $only_child.children();
                $only_child = null; // deletes only child so never two same id's
                $new_div.attr("id", id).append($orphans);
                $target_for_text.empty().append($new_div);
              }
            }
          }
          $target_for_text.slideDown('slow');
        });
      } else {
        console.log("already loaded help data: toggle help-hint box");
        $target_for_text.slideToggle('slow');
      }
    } else {
      console.log("no help text source URL specified (in the href attribute) so don't know where to get help from");
    }
  });

});
