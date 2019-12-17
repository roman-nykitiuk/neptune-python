(function($) {
  $(function() {
    /* On admin:device_category_change */
    if ($('.app-device.model-category').length > 0) {
      toggleInlines();
    }

    /* On admin:device_product_change */
    if ($('.app-device.model-product').length > 0) {
      resizeWindow(1.5, 2);
      toggleInlines();
    }
  });

})(jQuery);
