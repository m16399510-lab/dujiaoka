<!doctype html>
<html lang="{{ str_replace('_', '-', strtolower(app()->getLocale())) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ isset($page_title) && $page_title ? $page_title . ' | ' : '' }}{{ dujiaoka_config_get('title', dujiaoka_config_get('text_logo', '预言家SHOP')) }}</title>
    <meta name="keywords" content="{{ dujiaoka_config_get('keywords') }}">
    <meta name="description" content="{{ dujiaoka_config_get('description') }}">
    <link rel="stylesheet" href="{{ asset('assets/yuyanjia/css/app.css') }}?v=2026060602">
</head>
<body>
<div class="site-shell">
    <header class="site-header">
        <div class="container nav-wrap">
            <a class="brand" href="{{ url('/') }}">
                @if(dujiaoka_config_get('img_logo'))
                    <img src="{{ picture_ulr(dujiaoka_config_get('img_logo')) }}" alt="{{ dujiaoka_config_get('text_logo', '预言家SHOP') }}">
                @endif
                <span>{{ dujiaoka_config_get('text_logo', '预言家SHOP') }}</span>
            </a>
            <nav class="top-nav">
                <a href="{{ url('/') }}">首页</a>
                <a href="{{ url('/') }}#goods">商品中心</a>
                <a href="{{ url('order-search') }}">订单查询</a>
            </nav>
        </div>
    </header>

    <main>
        @yield('content')
    </main>

    <footer class="site-footer">
        <div class="container">
            {!! dujiaoka_config_get('footer') !!}
        </div>
    </footer>
</div>
<script src="{{ asset('assets/yuyanjia/js/app.js') }}?v=2026060602"></script>
@yield('js')
</body>
</html>
