<?php

namespace App\Admin\Forms;

use App\Models\Carmis;
use App\Models\GoodsSku;
use Dcat\Admin\Widgets\Form;
use Illuminate\Support\Facades\Storage;

class ImportCarmis extends Form
{

    /**
     * Handle the form request.
     *
     * @param array $input
     *
     * @return mixed
     */
    public function handle(array $input)
    {
        if (empty($input['carmis_list']) && empty($input['carmis_txt'])) {
            return $this->response()->error(admin_trans('carmis.rule_messages.carmis_list_and_carmis_txt_can_not_be_empty'));
        }
        $sku = GoodsSku::query()->find($input['sku_id'] ?? 0);
        if (!$sku) {
            return $this->response()->error('请选择有效的商品规格');
        }
        $carmisContent = "";
        if (!empty($input['carmis_txt'])) {
            $carmisContent = Storage::disk('public')->get($input['carmis_txt']);
        }
        if (!empty($input['carmis_list'])) {
            $carmisContent = $input['carmis_list'];
        }
        $carmisData = [];
        $tempList = explode(PHP_EOL, $carmisContent);
        foreach ($tempList as $val) {
            if (trim($val) != "") {
                $carmisData[] = [
                    'goods_id' => $sku->goods_id,
                    'sku_id' => $sku->id,
                    'carmi' => trim($val),
                    'status' => Carmis::STATUS_UNSOLD,
                    'created_at' => date('Y-m-d H:i:s'),
                    'updated_at' => date('Y-m-d H:i:s'),
                ];
            }
        }
        if ($input['remove_duplication'] == 1) {
            $carmisData = assoc_unique($carmisData, 'carmi');
        }
        Carmis::query()->insert($carmisData);
        // 删除文件
        Storage::disk('public')->delete($input['carmis_txt']);
        return $this
				->response()
				->success(admin_trans('carmis.rule_messages.import_carmis_success'))
				->location('/carmis');
    }

    /**
     * Build a form here.
     */
    public function form()
    {
        $this->confirm(admin_trans('carmis.fields.are_you_import_sure'));
        $this->select('sku_id', '商品规格')->options($this->skuOptions())->required();
        $this->textarea('carmis_list')
            ->rows(20)
            ->help(admin_trans('carmis.helps.carmis_list'));
        $this->file('carmis_txt')
            ->disk('public')
            ->uniqueName()
            ->accept('txt')
            ->maxSize(5120)
            ->help(admin_trans('carmis.helps.carmis_list'));
        $this->switch('remove_duplication');
    }

    private function skuOptions(): array
    {
        return GoodsSku::query()
            ->with('goods')
            ->orderBy('goods_id')
            ->orderBy('ord', 'DESC')
            ->get()
            ->mapWithKeys(function (GoodsSku $sku) {
                $goodsName = $sku->goods ? $sku->goods->gd_name : ('商品#' . $sku->goods_id);
                return [$sku->id => $goodsName . ' - ' . $sku->sku_name];
            })
            ->toArray();
    }

}
