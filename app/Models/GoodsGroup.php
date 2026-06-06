<?php

namespace App\Models;


use App\Events\GoodsGroupDeleted;
use Illuminate\Database\Eloquent\SoftDeletes;

class GoodsGroup extends BaseModel
{

    use SoftDeletes;

    protected $table = 'goods_group';

    protected $dispatchesEvents = [
        'deleted' => GoodsGroupDeleted::class
    ];

    /**
     * 关联商品
     *
     * @return \Illuminate\Database\Eloquent\Relations\HasMany
     *
     * @author    assimon<ashang@utf8.hk>
     * @copyright assimon<ashang@utf8.hk>
     * @link      http://utf8.hk/
     */
    public function goods()
    {
        return $this->hasMany(Goods::class, 'group_id');
    }

    public function parent()
    {
        return $this->belongsTo(self::class, 'parent_id');
    }

    public function children()
    {
        return $this->hasMany(self::class, 'parent_id');
    }

    public function getDisplayNameAttribute()
    {
        return $this->parent ? $this->parent->gp_name . ' / ' . $this->gp_name : $this->gp_name;
    }

    public static function treeOptions($excludeId = null)
    {
        $groups = self::query()
            ->orderBy('parent_id')
            ->orderBy('ord', 'DESC')
            ->orderBy('id')
            ->get()
            ->keyBy('id');

        $options = [];
        foreach ($groups as $group) {
            if ($excludeId && (int) $group->id === (int) $excludeId) {
                continue;
            }

            $names = [$group->gp_name];
            $parentId = (int) $group->parent_id;
            $seen = [$group->id => true];

            while ($parentId && isset($groups[$parentId]) && !isset($seen[$parentId])) {
                $seen[$parentId] = true;
                array_unshift($names, $groups[$parentId]->gp_name);
                $parentId = (int) $groups[$parentId]->parent_id;
            }

            $options[$group->id] = implode(' / ', $names);
        }

        return $options;
    }

}
