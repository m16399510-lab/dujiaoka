@extends('yuyanjia.layouts.default')

@section('content')
    <section class="page-section compact-section">
        <div class="container narrow">
            <div class="panel">
                <span class="eyebrow"><span></span>确认订单</span>
                <h1>请核对订单信息</h1>
                <div class="detail-list">
                    <div><span>订单号</span><strong>{{ $order_sn }}</strong></div>
                    <div><span>商品</span><strong>{{ $title }}</strong></div>
                    @if(!empty($sku))
                        <div><span>规格</span><strong>{{ $sku['sku_name'] ?? '' }}</strong></div>
                    @endif
                    <div><span>数量</span><strong>{{ $buy_amount }}</strong></div>
                    <div><span>邮箱</span><strong>{{ $email }}</strong></div>
                    <div><span>支付方式</span><strong>{{ $pay['pay_name'] ?? '' }}</strong></div>
                    @if(!empty($coupon))
                        <div><span>优惠码</span><strong>{{ $coupon['coupon'] }}</strong></div>
                    @endif
                    <div><span>应付金额</span><strong class="price">{{ number_format((float)$actual_price, 2) }} CNY</strong></div>
                    <div><span>创建时间</span><strong>{{ $created_at }}</strong></div>
                </div>
                <div class="actions">
                    <a class="btn primary" href="{{ url('pay-gateway', ['handle' => urlencode($pay['pay_handleroute']),'payway' => $pay['pay_check'], 'orderSN' => $order_sn]) }}">立即支付</a>
                    <a class="btn ghost" href="{{ url('order-search') }}">查询订单</a>
                </div>
            </div>
        </div>
    </section>
@stop
