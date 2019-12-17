(function($) {
  $(document).ready(function() {
    var updateOwnersPhysicianSelect2 = function(clientId) {
      var $selects = $('select#id_owners, select#id_physician');

      if (isNaN(clientId)) {
        $selects.html('');
        $selects.select2();
      } else {
        var url = '/api/staff/clients/' + clientId + '/accounts';
        $.get(url, function(response) {
          var ownersOptions = response.map(function(account) {
            return {name: account.email, value: account.id, physician: account.is_physician};
          });

          var physicianOptions = ownersOptions.filter(function(account) {
            return account.physician;
          });

          updateSelect2($('select#id_owners'), ownersOptions);
          updateSelect2($('select#id_physician'), physicianOptions);
        });
      }
    };

    var deviceOrCostTypeChangedHandler = function($row, productDiscounts) {
      var $device = $row.find('.item-device > select');
      var productId = parseInt($device.find('option:selected').attr('product'));
      var productDiscount = productDiscounts.find(function (product) {
        return product.id === productId;
      });

      var costType = $row.find('.field-cost_type select').val();
      var newOptions = (productDiscount ? productDiscount.discounts[costType] || [] : []).map(function(discount) {
        return {name: discount.name, value: discount.id};
      });

      var $select = $row.find('.field-discounts select');
      updateSelect2($select, newOptions);
    };

    var updateDiscountsSelect2 = function() {
      var clientId = $('#repcase-client-id').val();
      var url = '/api/staff/clients/' + clientId + '/discounts';
      $.get(url, function (response) {
        var $itemsInline = $('#item_set-group');

        $itemsInline.find('.form-row:not(.empty-form)').each(function () {
          var $row = $(this);
          deviceOrCostTypeChangedHandler($row, response);
        });

        $itemsInline.on('change', '.item-device > select, .field-cost_type select', function(event) {
          var $row = $(event.target).parents('.form-row');
          deviceOrCostTypeChangedHandler($row, response);
        });
      });
    }

    var updateDeviceSelect2 = function(clientId) {
      var devices = {};
      var bindSelect2ChangeEvent = function(trigger, target, keys) {
        keys.push(trigger);
        $('#item_set-group').on('change', '.item-' + trigger + ' > select', function() {
          var $triggerSelect = $(this);
          var $targetSelect = $triggerSelect.siblings('.item-' + target).find('> select');
          var options = keys.reduce(function(targetOptions, key) {
            var triggerValue = $triggerSelect.parents('.item-' + key).find('> select').val();
            return targetOptions[triggerValue];
          }, devices);

          if (target !== 'device') {
            options = Object.keys(options).map(function(option) {
              return {name: option, value: option};
            });
          }
          updateSelect2($targetSelect, options);
          $targetSelect.trigger('change');
        });
      };

      var url = '/api/staff/clients/' + clientId + '/devices';
      $.get(url, function(response) {
        response.forEach(function(device) {
          devices[device.specialty] = devices[device.specialty] || {};
          devices[device.specialty][device.category] = devices[device.specialty][device.category] || {};
          var manufacturers = devices[device.specialty][device.category][device.manufacturer] || [];
          manufacturers.push({ name: device.name, value: device.id, attrs: { product: device.product } });
          devices[device.specialty][device.category][device.manufacturer] = manufacturers;
        });

        var specialties = Object.keys(devices).map(function(specialty) {
          return {name: specialty, value: specialty}
        });
        updateSelect2($('#item_set-empty .item-specialty > select'), specialties, false);
        updateSelect2($('.errorlist + .item-specialty').find('> select'), specialties, true);
        $('.errorlist').closest('.form-row').find('.item-purchase_type > select').select2();

        bindSelect2ChangeEvent('specialty', 'category', []);
        bindSelect2ChangeEvent('category', 'manufacturer', ['specialty']);
        bindSelect2ChangeEvent('manufacturer', 'device', ['specialty', 'category']);

        $('.errorlist').closest('.form-row').find('.item-specialty > select').trigger('change');
      });

      $('#item_set-group').on('change', '.item-device > select, .item-purchase_type > select', function() {
        var $fieldIdentifier = $(this).closest('.field-identifier');
        var $identifier = $fieldIdentifier.find('.item-identifier > select');
        var isBulk = $fieldIdentifier.find('.item-purchase_type > select').val() === '1';
        if (isBulk) {
          var deviceId = $fieldIdentifier.find('.item-device > select').val();
          var url = '/api/staff/devices/' + deviceId + '/items';
          $.get(url, function (response) {
            var items = response.map(function(item) {
              return { name: item.identifier, value: item.identifier, attrs: { cost: item.cost_type } };
            });
            updateSelect2($identifier, items);
            $identifier.trigger('change');
          });
        } else {
          var identifier = $identifier.val() || '';
          updateSelect2($identifier, [{name: identifier, value: identifier}], true, true);
          $identifier.trigger('change');
        }
      });

      $('.errorlist').closest('.form-row').find('.item-purchase_type > select').trigger('change');
      $('#item_set-group').on('change', '.item-identifier > select', function() {
        var $costType = $(this).closest('.form-row').find('.field-cost_type > select');
        $costType.val($(this).find('option:selected').attr('cost') || 1).trigger('change');
      });
    };

    /* On admin:tracker_repcase_change */
    if ($('.app-tracker.model-repcase.change-form').length > 0) {
      toggleInlines();

      var clientId = $('#repcase-client-id').val();
      updateOwnersPhysicianSelect2(clientId);

      if ($('select#id_client').length > 0) { // On Add rep case
        $('select#id_client').change(function () {
          updateOwnersPhysicianSelect2($(this).val());
        });
      } else {  // On Change rep case
        updateDeviceSelect2(clientId);
        updateDiscountsSelect2();
      }

      django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
        $($row).find('.item-specialty > select').trigger('change');
      });
    }
  });
})(jQuery);
