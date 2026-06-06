@extends('yuyanjia.layouts.default')

@section('content')
    <section class="page-section compact-section">
        <div class="container narrow">
            <div class="panel pay-panel">
                <span class="eyebrow"><span></span>{{ $payname ?? '扫码支付' }}</span>
                <h1>扫码完成支付</h1>
                <p class="lead">请在 {{ dujiaoka_config_get('order_expire_time', 5) }} 分钟内支付，成功后页面会自动跳转。</p>
                <div class="qr-box">
                    <img src="data:image/png;base64,{!! base64_encode(QrCode::format('png')->size(220)->generate($qr_code)) !!}" alt="支付二维码">
                </div>
                <strong class="qr-price">{{ number_format((float)$actual_price, 2) }} CNY</strong>
                @if(Agent::isMobile() && isset($jump_payuri))
                    <a class="btn primary" href="{{ $jump_payuri }}">打开 App 支付</a>
                @endif
            </div>
        </div>
    </section>
@stop

@section('js')
    <script>
        window.YUYANJIA_ORDER_CHECK_URL = "{{ url('check-order-status', ['orderSN' => $orderid]) }}";
        window.YUYANJIA_ORDER_DETAIL_URL = "{{ url('detail-order-sn', ['orderSN' => $orderid]) }}";
    </script>
@stop
