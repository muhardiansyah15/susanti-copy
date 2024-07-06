odoo.define('susanti_vendor_portal.vendor_price_submission', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    if (location.pathname.includes('/my/home') || location.pathname.includes('/my')) {
        $(document).ready(function () {
            var element = document.querySelector('.list-group-item[href="/my/price-submissions"]');
            if (element) {
                element.classList.remove('d-none');
            }
            var element2 = document.querySelector('.list-group-item[href="/my/price-submission/items"]');
            if (element2) {
                element2.classList.remove('d-none');
            }
        });
    }

    if (location.pathname.includes('/my/price-submission/items')) {
        $(document).ready(function () {
            $('.btn-new-pricelistitem').click(function (){
                
                $('#createNewPricelistItem').modal('show');
            });

            $('.new-pricelistitem-btn').click(function (){
                var pricelistitem_name = $('#pricelistitem_name').val();
                var pricelistitem_code = $('#pricelistitem_code').val();
                var delivery_from = $('#delivery_from').val();
                var delivery_to = $('#delivery_to').val();
                var price = $('#price').val();
                var start_date = $('#start_date').val();
                var end_date = $('#end_date').val();
                ajax.jsonRpc('/my/price-submission/items/create', 'call',
                    {'pricelist_item_data': {
                        'pricelistitem_name': pricelistitem_name,
                        'pricelistitem_code': pricelistitem_code,
                        'delivery_from': delivery_from,
                        'delivery_to': delivery_to,
                        'price': price,
                        'start_date': start_date,
                        'end_date': end_date,
                    }}).then(function(result) {
                        $('#createNewPricelistItem').modal('hide');
                });
            });

            $('.new-pricelistitem-btn').click(function (){
                
            });
        });
    }

});