window.$ = window.jQuery = (jQuery || django.jQuery);

(function($) {
  django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
    if (jQuery.fn.select2) {
      var $select = $row.find('[class*=field-] select');
      jQuery($select).select2();
    }
  });

  window.collapseInlines = function collapseInlines($inlinesGroup) {
    $inlinesGroup.find('h2').on('click', function() {
      $inlinesGroup.find('fieldset > table').toggle(500);
    }).click();
  }

  window.toggleInlines = function toggleInlines() {
    $('.inline-related.has_original fieldset').hide();
    $('.inline-related.has_original .errorlist').parents('.inline-related').find('fieldset').show();

    var urlParams = new URLSearchParams(window.location.search);
    var clientPriceId = urlParams.get('client-price');
    var clientPriceInput = '[name=client-price-id][value=' + clientPriceId + ']';
    $(clientPriceInput).parents('.inline-related').find('fieldset').show();

    $('.inline-related.has_original h3').on('click', function() {
      $(this).siblings('fieldset').toggle();
    })

    $('.inline-related.has_original h3 span.delete').on('click', function(event) {
      event.stopPropagation();
    });
  };

  window.resizeWindow = function resizeWindow(widthRatio, heightRatio) {
    var widthRatio = widthRatio || 1;
    var heightRatio = heightRatio || 2;
    window.resizeTo(window.outerWidth * widthRatio, window.outerHeight * heightRatio);
  };

  window.doubleWindowHeight = function doubleWindowHeight() {
    window.resizeWindow();
  };

  window.updateSelect2 = function updateSelect2($select, newOptions, callSelect2, tags) {
    if (callSelect2 === undefined) {
      callSelect2 = true;
    }

    var selectedOptions = $select.val() || [];
    $select.html('');
    newOptions.forEach(function (option) {
      var isSelected = selectedOptions.indexOf(option.value.toString()) !== -1;
      var selected = isSelected ? ' selected' : '';
      var attrs = '';
      if (option.attrs) {
        Object.keys(option.attrs).forEach(function(key) {
          attrs += ' ' + key + '="' + option.attrs[key] + '"';
        })
      }
      $select.append('<option value="' + option.value + '" ' + selected + attrs + '>' + option.name + '</option>');
    });
    if (callSelect2) {
      $select.select2({tags: !!tags});
    }
  };

  window.disableDiscount = function disableDiscount($el) {
    var $tr = $el.closest('tr.form-row');
    $tr.find('.field-percent input, .field-value input').prop('readonly', false);

    var disabledFieldName = $el.val() == 1 ? 'value' : 'percent';
    $tr.find('.field-' + disabledFieldName + ' input').prop('readonly', true);
  };
})(jQuery);
