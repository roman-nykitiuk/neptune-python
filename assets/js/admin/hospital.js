(function($) {
  $(function() {
    /* On admin:hospital_device_change */
    if ($('.app-hospital.model-client').length > 0) {
      collapseInlines($('#account_set-group'));
      collapseInlines($('#account_set-2-group'));
      collapseInlines($('#preference_set-group'));
      collapseInlines($('#preference_set-2-group'));
      collapseInlines($('#preference_set-3-group'));
    }

    /* On admin:hospital_device_change */
    if ($('.app-hospital.model-device').length > 0) {
      doubleWindowHeight();
      toggleInlines();
    }
  });
})(jQuery);

