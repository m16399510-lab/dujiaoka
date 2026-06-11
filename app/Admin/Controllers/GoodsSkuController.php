<?php

namespace App\Admin\Controllers;

use App\Admin\Actions\Post\BatchRestore;
use App\Admin\Actions\Post\Restore;
use App\Admin\Repositories\GoodsSku;
use App\Models\Carmis;
use App\Models\Goods;
use App\Models\GoodsSku as GoodsSkuModel;
use Dcat\Admin\Form;
use Dcat\Admin\Grid;
use Dcat\Admin\Http\Controllers\AdminController;
use Dcat\Admin\Show;
use Illuminate\Support\Facades\DB;

class GoodsSkuController extends AdminController
{
    protected function grid()
    {
        return Grid::make(new GoodsSku(['goods']), function (Grid $grid) {
            $grid->model()
                ->withCount(['carmis as available_carmis_count' => function ($query) {
                    $query->where('status', Carmis::STATUS_UNSOLD);
                }])
                ->where(function ($query) {
                    $query->where('sku_code', '<>', GoodsSkuModel::DEFAULT_SKU_CODE)
                        ->orWhereNotExists(function ($subQuery) {
                            $subQuery->select(DB::raw(1))
                                ->from('goods_skus as real_skus')
                                ->whereColumn('real_skus.goods_id', 'goods_skus.goods_id')
                                ->where('real_skus.sku_code', '<>', GoodsSkuModel::DEFAULT_SKU_CODE)
                                ->whereNull('real_skus.deleted_at');
                        });
                })
                ->orderBy('goods_id')
                ->orderBy('ord', 'DESC');
            $grid->column('id')->sortable();
            $grid->column('goods.gd_name', '所属商品');
            $grid->column('sku_name', '规格名称');
            $grid->column('sku_code', '规格编码');
            $grid->column('actual_price', '价格')->sortable();
            $grid->column('real_stock', '真实库存')->display(function () {
                return $this->real_stock;
            });
            $grid->column('is_open', '状态')->select(GoodsSkuModel::getIsOpenMap());
            $grid->column('ord', '排序')->sortable();
            $grid->column('created_at');
            $grid->column('updated_at')->sortable();
            $grid->filter(function (Grid\Filter $filter) {
                $filter->equal('goods_id', '所属商品')->select(Goods::query()->pluck('gd_name', 'id'));
                $filter->like('sku_name', '规格名称');
                $filter->equal('is_open', '状态')->select(GoodsSkuModel::getIsOpenMap());
                $filter->scope(admin_trans('dujiaoka.trashed'))->onlyTrashed();
            });
            $grid->actions(function (Grid\Displayers\Actions $actions) {
                if (request('_scope_') == admin_trans('dujiaoka.trashed')) {
                    $actions->append(new Restore(GoodsSkuModel::class));
                }
            });
            $grid->batchActions(function (Grid\Tools\BatchActions $batch) {
                if (request('_scope_') == admin_trans('dujiaoka.trashed')) {
                    $batch->add(new BatchRestore(GoodsSkuModel::class));
                }
            });
        });
    }

    protected function detail($id)
    {
        return Show::make($id, new GoodsSku(['goods']), function (Show $show) {
            $show->field('id');
            $show->field('goods.gd_name', '所属商品');
            $show->field('sku_name', '规格名称');
            $show->field('sku_code', '规格编码');
            $show->field('actual_price', '价格');
            $show->field('picture', '规格图片')->image();
            $show->field('real_stock', '真实库存');
            $show->field('in_stock', '手动库存');
            $show->field('is_open', '状态')->using(GoodsSkuModel::getIsOpenMap());
            $show->field('ord', '排序');
            $show->field('created_at');
            $show->field('updated_at');
        });
    }

    protected function form()
    {
        return Form::make(new GoodsSku(), function (Form $form) {
            $form->display('id');
            $form->select('goods_id', '所属商品')->options(Goods::query()->pluck('gd_name', 'id'))->required();
            $form->text('sku_name', '规格名称')->required();
            $form->text('sku_code', '规格编码')->default(GoodsSkuModel::DEFAULT_SKU_CODE)->required();
            $form->currency('actual_price', '规格价格')->default(0)->required();
            $form->image('picture', '规格图片')->autoUpload()->uniqueName();
            $form->number('in_stock', '手动库存（人工处理）')->default(0)->help('只给人工处理商品使用；自动发货的真实库存会自动统计该规格未售出的卡密数量。');
            $form->number('ord', '排序')->default(1);
            $form->switch('is_open', '是否启用')->default(GoodsSkuModel::STATUS_OPEN);
            $form->display('created_at');
            $form->display('updated_at');
        });
    }
}
