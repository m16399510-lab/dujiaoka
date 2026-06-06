@extends('yuyanjia.layouts.default')

@section('content')
    <section class="page-section compact-section">
        <div class="container narrow">
            <div class="panel notice-panel">
                <span class="eyebrow danger">请求没有完成</span>
                <h1>{{ $title }}</h1>
                <p>{{ $content }}</p>
                <div class="actions">
                    @if(!$url)
                        <a class="btn secondary" href="javascript:history.back(-1);">返回上一页</a>
                    @else
                        <a class="btn secondary" href="{{ $url }}">返回</a>
                    @endif
                    <a class="btn ghost" href="{{ url('/') }}">回到首页</a>
                </div>
            </div>
        </div>
    </section>
@stop
