<?php

namespace App\Models;

use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Support\Str;

class GoodsSku extends BaseModel
{
    use SoftDeletes;

    const DEFAULT_SKU_CODE = 'DEFAULT';

    protected $table = 'goods_skus';

    protected $fillable = [
        'goods_id',
        'sku_name',
        'sku_code',
        'actual_price',
        'picture',
        'in_stock',
        'ord',
        'is_open',
    ];

    protected static function boot()
    {
        parent::boot();

        static::saving(function (GoodsSku $sku) {
            if (empty($sku->sku_name)) {
                $sku->sku_name = '默认规格';
            }

            $sku->sku_code = trim((string) $sku->sku_code);

            if (empty($sku->sku_code)) {
                $sku->sku_code = self::makeUniqueCode($sku->goods_id);
            }

            if (self::codeExistsForAnotherSku($sku)) {
                $sku->sku_code = self::makeUniqueCode($sku->goods_id);
            }

            if ($sku->actual_price === null || $sku->actual_price === '') {
                $sku->actual_price = 0;
            }

            if ($sku->in_stock === null || $sku->in_stock === '') {
                $sku->in_stock = 0;
            }

            if ($sku->ord === null || $sku->ord === '') {
                $sku->ord = 1;
            }

            if ($sku->is_open === null || $sku->is_open === '') {
                $sku->is_open = self::STATUS_OPEN;
            }
        });
    }

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

    public function getRealStockAttribute(): int
    {
        $goods = $this->relationLoaded('goods') ? $this->goods : $this->goods()->first();

        if ($goods && (int) $goods->type === Goods::AUTOMATIC_DELIVERY) {
            if (array_key_exists('available_carmis_count', $this->attributes)) {
                return max(0, (int) $this->attributes['available_carmis_count']);
            }

            return (int) $this->carmis()
                ->where('status', Carmis::STATUS_UNSOLD)
                ->count();
        }

        return max(0, (int) $this->in_stock);
    }

    private static function makeUniqueCode($goodsID): string
    {
        for ($i = 0; $i < 10; $i++) {
            $code = 'SKU-' . strtoupper(Str::random(8));

            if (!$goodsID || !self::withTrashed()->where('goods_id', $goodsID)->where('sku_code', $code)->exists()) {
                return $code;
            }
        }

        return 'SKU-' . strtoupper(Str::random(12));
    }

    private static function codeExistsForAnotherSku(GoodsSku $sku): bool
    {
        if (!$sku->goods_id || !$sku->sku_code) {
            return false;
        }

        return self::withTrashed()
            ->where('goods_id', $sku->goods_id)
            ->where('sku_code', $sku->sku_code)
            ->when($sku->id, function ($query) use ($sku) {
                $query->where('id', '<>', $sku->id);
            })
            ->exists();
    }
}
