<?php

namespace App\Models;

use Illuminate\Database\Eloquent\SoftDeletes;

class GoodsSku extends BaseModel
{
    use SoftDeletes;

    const DEFAULT_SKU_CODE = 'DEFAULT';

    protected $table = 'goods_skus';

    public function goods()
    {
        return $this->belongsTo(Goods::class, 'goods_id');
    }

    public function carmis()
    {
        return $this->hasMany(Carmis::class, 'sku_id');
    }

    public static function getIsOpenMap()
    {
        return [
            self::STATUS_OPEN => '启用',
            self::STATUS_CLOSE => '禁用',
        ];
    }

    public function getDisplayNameAttribute()
    {
        $goodsName = $this->goods ? $this->goods->gd_name : ('商品#' . $this->goods_id);
        return $goodsName . ' - ' . $this->sku_name;
    }
}
