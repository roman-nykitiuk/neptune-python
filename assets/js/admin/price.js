(function($) {
  $(document).ready(function() {
    /* On admin:device_clientprice_change */
    if ($('.app-price.model-clientprice').length > 0) {
      resizeWindow(2, 1.5);

      $('.field-discount_type > select').each(function () {
        window.disableDiscount($(this));
      });

      $('#discount_set-group').on('change', '.field-discount_type > select', function () {
        window.disableDiscount($(this));
      });
    }

    if ($('.app-price.model-rebate').length > 0) {
      var manufacturerId = $('select#id_manufacturer').val();

      var updateObjectsSelect2 = function($row) {
        var $select = $row.find('td.field-object_id select');
        var $contentTypeSelect = $row.find('td.field-content_type select');

        if ($contentTypeSelect.val()) {
          var modelName = $contentTypeSelect.find('option:selected').text();
          var url = '/api/staff/manufacturers/' + manufacturerId + '/' + modelName;
          $.get(url, function(response) {
            entries = response.map(function (entry) {
              return {value: entry.id, name: entry.name};
            });
            window.updateSelect2($select, entries);
          })
        } else {
          window.updateSelect2($select, []);
        }
      };

      $('#rebate_form').on('change', 'td.field-content_type select', function(event) {
        var $row = $(event.target).parents('.form-row');
        updateObjectsSelect2($row);
      });

      var objectIdInputToSelect2 = function($row) {
        var $objectIdWrapper = $row.find('.field-object_id');
        var $oldObjectIdInput = $objectIdWrapper.find('input');
        var $objectIdSelect = $('<select>');
        $objectIdSelect.attr('name', $oldObjectIdInput.attr('name'))
          .attr('id', $oldObjectIdInput.attr('id'))
          .append('<option value="' + $oldObjectIdInput.val() + '"></option>');
        $oldObjectIdInput.remove();
        $objectIdWrapper.append($objectIdSelect);
        $objectIdSelect.select2();
      }

      $('#rebate_form tr.form-row:not(.empty-form)').each(function() {
        objectIdInputToSelect2($(this));
        updateObjectsSelect2($(this));
      });

      django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
        $($row).find('.field-content_type select').select2();
        objectIdInputToSelect2($row);
        $($row).find('.field-object_id select').html('').select2();
      });

      $('.field-discount_type > select').each(function () {
        window.disableDiscount($(this));
      });

      $('#tier_set-group').on('change', '.field-discount_type > select', function () {
        window.disableDiscount($(this));
      });
    }
  });

})(jQuery);
