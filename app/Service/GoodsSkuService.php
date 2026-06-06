<?php

namespace App\Service;

use App\Exceptions\RuleValidationException;
use App\Models\BaseModel;
use App\Models\Carmis;
use App\Models\Goods;
use App\Models\GoodsSku;

class GoodsSkuService
{
    public function ensureDefaultSku(Goods $goods): GoodsSku
    {
        $sku = GoodsSku::query()
            ->where('goods_id', $goods->id)
            ->where('sku_code', GoodsSku::DEFAULT_SKU_CODE)
            ->first();

        if ($sku) {
            return $sku;
        }

        $sku = new GoodsSku();
        $sku->goods_id = $goods->id;
        $sku->sku_name = '默认规格';
        $sku->sku_code = GoodsSku::DEFAULT_SKU_CODE;
        $sku->actual_price = $goods->actual_price;
        $sku->picture = $goods->picture;
        $sku->in_stock = $goods->in_stock;
        $sku->ord = 1;
        $sku->is_open = BaseModel::STATUS_OPEN;
        $sku->save();

        return $sku;
    }

    public function resolveForGoods(Goods $goods, $skuID = null): GoodsSku
    {
        $query = GoodsSku::query()
            ->where('goods_id', $goods->id)
            ->where('is_open', BaseModel::STATUS_OPEN);

        if ($skuID) {
            $sku = (clone $query)->where('id', $skuID)->first();
            if (!$sku) {
                throw new RuleValidationException('请选择有效的商品规格');
            }
        } else {
            $sku = (clone $query)->where('sku_code', GoodsSku::DEFAULT_SKU_CODE)->first();
        }

        if (!$sku) {
            $sku = $this->ensureDefaultSku($goods);
        }

        if ((int) $sku->is_open !== BaseModel::STATUS_OPEN) {
            throw new RuleValidationException('该规格已下架');
        }

        return $sku;
    }

    public function availableStock(Goods $goods, GoodsSku $sku): int
    {
        if ((int) $goods->type === Goods::AUTOMATIC_DELIVERY) {
            return Carmis::query()
                ->where('goods_id', $goods->id)
                ->where('sku_id', $sku->id)
                ->where('status', Carmis::STATUS_UNSOLD)
                ->count();
        }

        return max(0, (int) $sku->in_stock);
    }

    public function options(): array
    {
        return GoodsSku::query()
            ->with('goods')
            ->orderBy('goods_id')
            ->orderBy('ord', 'DESC')
            ->get()
            ->mapWithKeys(function (GoodsSku $sku) {
                return [$sku->id => $sku->display_name];
            })
            ->toArray();
    }
}
