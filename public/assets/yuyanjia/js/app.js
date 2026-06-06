(function () {
    function onReady(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    }

    onReady(function () {
        var tabs = document.querySelectorAll('[data-group-target]');
        var cards = document.querySelectorAll('[data-product-name]');
        tabs.forEach(function (tab) {
            tab.addEventListener('click', function () {
                tabs.forEach(function (item) { item.classList.remove('active'); });
                tab.classList.add('active');
                var group = tab.getAttribute('data-group-target');
                cards.forEach(function (card) {
                    card.style.display = group === 'all' || card.getAttribute('data-group') === group ? '' : 'none';
                });
            });
        });

        var search = document.querySelector('[data-product-search]');
        if (search) {
            search.addEventListener('input', function () {
                var value = search.value.trim().toLowerCase();
                cards.forEach(function (card) {
                    var name = (card.getAttribute('data-product-name') || '').toLowerCase();
                    card.style.display = !value || name.indexOf(value) !== -1 ? '' : 'none';
                });
            });
        }

        var skuButtons = document.querySelectorAll('[data-sku-option]');
        var skuInput = document.querySelector('[data-sku-input]');
        var priceTarget = document.querySelector('[data-sku-price-label]');
        var stockTarget = document.querySelector('[data-sku-stock]');
        var imageTarget = document.getElementById('skuPicture');
        var amountInput = document.querySelector('[data-buy-amount]');
        var submitButton = document.querySelector('[data-submit-order]');
        skuButtons.forEach(function (button) {
            button.addEventListener('click', function () {
                skuButtons.forEach(function (item) { item.classList.remove('active'); });
                button.classList.add('active');
                if (skuInput) skuInput.value = button.getAttribute('data-sku-id') || '';
                if (priceTarget) priceTarget.textContent = Number(button.getAttribute('data-sku-price') || 0).toFixed(2);
                var stockValue = Number(button.getAttribute('data-sku-stock') || 0);
                if (stockTarget) stockTarget.textContent = String(stockValue);
                if (imageTarget && button.getAttribute('data-sku-picture')) imageTarget.src = button.getAttribute('data-sku-picture');
                if (amountInput) {
                    amountInput.max = stockValue > 0 ? String(stockValue) : '';
                    if (stockValue > 0 && Number(amountInput.value || 1) > stockValue) {
                        amountInput.value = String(stockValue);
                    }
                    if (Number(amountInput.value || 1) < 1) {
                        amountInput.value = '1';
                    }
                }
                if (submitButton) submitButton.disabled = stockValue <= 0;
            });
        });
        if (skuButtons[0]) skuButtons[0].click();

        var payButtons = document.querySelectorAll('[data-pay-option]');
        var payInput = document.querySelector('[data-pay-input]');
        payButtons.forEach(function (button) {
            button.addEventListener('click', function () {
                payButtons.forEach(function (item) { item.classList.remove('active'); });
                button.classList.add('active');
                if (payInput) payInput.value = button.getAttribute('data-pay-id');
            });
        });

        var buyForm = document.querySelector('[data-buy-form]');
        if (buyForm) {
            buyForm.addEventListener('submit', function (event) {
                var amount = Number(amountInput && amountInput.value ? amountInput.value : 1);
                var activeSku = document.querySelector('[data-sku-option].active');
                var stock = activeSku ? Number(activeSku.getAttribute('data-sku-stock') || 0) : 0;
                if (stock <= 0) {
                    alert('当前规格库存不足，请换一个规格。');
                    event.preventDefault();
                    return;
                }
                if (stock > 0 && amount > stock) {
                    alert('库存不足，请减少购买数量。');
                    event.preventDefault();
                    return;
                }
                if (window.YUYANJIA_BUY_LIMIT && amount > window.YUYANJIA_BUY_LIMIT) {
                    alert('已超过本商品限购数量。');
                    event.preventDefault();
                }
            });
        }

        document.querySelectorAll('[data-copy-target]').forEach(function (button) {
            button.addEventListener('click', function () {
                var source = document.querySelector('[data-copy-source="' + button.getAttribute('data-copy-target') + '"]');
                if (!source) return;
                source.select();
                var text = source.value;
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(text).then(function () { alert('复制成功'); });
                } else {
                    document.execCommand('copy');
                    alert('复制成功');
                }
            });
        });

        var toastClose = document.querySelector('[data-close-toast]');
        if (toastClose) {
            toastClose.addEventListener('click', function () {
                var toast = document.querySelector('[data-toast-note]');
                if (toast) toast.style.display = 'none';
            });
        }

        if (window.YUYANJIA_ORDER_CHECK_URL) {
            var timer = window.setInterval(function () {
                fetch(window.YUYANJIA_ORDER_CHECK_URL, { credentials: 'same-origin' })
                    .then(function (res) { return res.json(); })
                    .then(function (res) {
                        if (res.code === 400001) {
                            window.clearInterval(timer);
                            alert('订单已过期');
                            window.location.href = '/';
                        }
                        if (res.code === 200) {
                            window.clearInterval(timer);
                            alert('支付成功');
                            window.location.href = window.YUYANJIA_ORDER_DETAIL_URL || '/';
                        }
                    })
                    .catch(function () {});
            }, 5000);
        }
    });
})();
