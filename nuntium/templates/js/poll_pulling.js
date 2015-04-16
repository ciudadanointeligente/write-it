{% load i18n %}
{% load subdomainurls %}

  var spin_if_pulling = function(url, reload) {
    console.log("Polling " + url);
    var spinning = '<i class="fa fa-spinner fa-pulse" data-toggle="tooltip" data-placement="right" title="{% trans 'We are currently fetching data from PopIt' %}"></i>';
    $.get(url, function(status){
      if (status.inprogress >= 1){
        $(".import_spinner").html(spinning);
        $('[data-toggle="tooltip"]').tooltip()
        setTimeout( spin_if_pulling, 2000, url, 1)
      } else {
        $(".import_spinner").text("");
        // Ideally we could update the sidebar here, but until we can
        // find out how many users we *now* have, just reload
        if (reload == 1) {
          location.reload() 
        }
      }
    })
  };

  $(function(){
    spin_if_pulling("{% url 'pulling_status' %}", 0);
  });

