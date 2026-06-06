<?php

namespace App\Admin\Controllers;

use App\Admin\Actions\Post\BatchRestore;
use App\Admin\Actions\Post\Restore;
use App\Admin\Repositories\GoodsGroup;
use Dcat\Admin\Form;
use Dcat\Admin\Grid;
use Dcat\Admin\Show;
use Dcat\Admin\Http\Controllers\AdminController;
use App\Models\GoodsGroup as GoodsGroupModel;

class GoodsGroupController extends AdminController
{

    /**
     * Make a grid builder.
     *
     * @return Grid
     */
    protected function grid()
    {
        return Grid::make(new GoodsGroup(['parent']), function (Grid $grid) {
            $grid->model()->orderBy('id', 'DESC');
            $grid->column('id')->sortable();
            $grid->column('parent.gp_name', '上级分类')->display(function ($value) {
                return $value ?: '顶级分类';
            });
            $grid->column('gp_name')->editable();
            $grid->column('is_open')->switch();
            $grid->column('ord')->editable();
            $grid->column('created_at');
            $grid->column('updated_at')->sortable();
            $grid->disableViewButton();
            $grid->filter(function (Grid\Filter $filter) {
                $filter->equal('id');
                $filter->scope(admin_trans('dujiaoka.trashed'))->onlyTrashed();
            });
            $grid->actions(function (Grid\Displayers\Actions $actions) {
                if (request('_scope_') == admin_trans('dujiaoka.trashed')) {
                    $actions->append(new Restore(GoodsGroupModel::class));
                }
            });
            $grid->batchActions(function (Grid\Tools\BatchActions $batch) {
                if (request('_scope_') == admin_trans('dujiaoka.trashed')) {
                    $batch->add(new BatchRestore(GoodsGroupModel::class));
                }
            });
        });
    }

    /**
     * Make a show builder.
     *
     * @param mixed $id
     *
     * @return Show
     */
    protected function detail($id)
    {
        return Show::make($id, new GoodsGroup(), function (Show $show) {
            $show->field('id');
            $show->field('parent.gp_name', '上级分类')->as(function ($value) {
                return $value ?: '顶级分类';
            });
            $show->field('gp_name');
            $show->field('is_open')->as(function ($isOpen) {
                if ($isOpen == GoodsGroupModel::STATUS_OPEN) {
                    return admin_trans('dujiaoka.status_open');
                } else {
                    return admin_trans('dujiaoka.status_close');
                }
            });
            $show->field('ord');
            $show->field('created_at');
            $show->field('updated_at');
        });
    }

    /**
     * Make a form builder.
     *
     * @return Form
     */
    protected function form()
    {
        return Form::make(new GoodsGroup(), function (Form $form) {
            $form->display('id');
            $form->select('parent_id', '上级分类')
                ->options([0 => '顶级分类'] + GoodsGroupModel::treeOptions())
                ->default(0);
            $form->text('gp_name');
            $form->switch('is_open')->default(GoodsGroupModel::STATUS_OPEN);
            $form->number('ord')->default(1)->help(admin_trans('dujiaoka.ord'));
            $form->display('created_at');
            $form->display('updated_at');
            $form->disableViewButton();
            $form->saving(function (Form $form) {
                if ((int) $form->parent_id === (int) $form->model()->id) {
                    $form->parent_id = 0;
                }
            });
            $form->footer(function ($footer) {
                // 去掉`查看`checkbox
                $footer->disableViewCheck();
            });
        });
    }
}
