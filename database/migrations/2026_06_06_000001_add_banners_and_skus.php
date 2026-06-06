<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

class AddBannersAndSkus extends Migration
{
    public function up()
    {
        if (!Schema::hasTable('banners')) {
            Schema::create('banners', function (Blueprint $table) {
                $table->increments('id');
                $table->string('title', 200);
                $table->text('subtitle')->nullable();
                $table->string('button_text', 100)->nullable();
                $table->text('image')->nullable();
                $table->string('link', 500)->nullable();
                $table->integer('ord')->default(1)->index();
                $table->tinyInteger('is_open')->default(1)->index();
                $table->timestamps();
                $table->softDeletes();
            });
        }

        if (!Schema::hasTable('goods_skus')) {
            Schema::create('goods_skus', function (Blueprint $table) {
                $table->increments('id');
                $table->integer('goods_id')->index();
                $table->string('sku_name', 150);
                $table->string('sku_code', 64)->default('DEFAULT');
                $table->decimal('actual_price', 10, 2)->default(0);
                $table->text('picture')->nullable();
                $table->integer('in_stock')->default(0);
                $table->integer('ord')->default(1)->index();
                $table->tinyInteger('is_open')->default(1)->index();
                $table->timestamps();
                $table->softDeletes();
                $table->unique(['goods_id', 'sku_code'], 'goods_skus_goods_id_sku_code_unique');
            });
        }

        if (!Schema::hasColumn('orders', 'sku_id')) {
            Schema::table('orders', function (Blueprint $table) {
                $table->integer('sku_id')->nullable()->after('goods_id')->index();
            });
        }

        if (!Schema::hasColumn('carmis', 'sku_id')) {
            Schema::table('carmis', function (Blueprint $table) {
                $table->integer('sku_id')->nullable()->after('goods_id')->index();
            });
        }

        $now = date('Y-m-d H:i:s');
        DB::statement("INSERT INTO goods_skus (goods_id, sku_name, sku_code, actual_price, picture, in_stock, ord, is_open, created_at, updated_at) SELECT g.id, '默认规格', 'DEFAULT', g.actual_price, g.picture, g.in_stock, 1, 1, '{$now}', '{$now}' FROM goods g LEFT JOIN goods_skus s ON s.goods_id = g.id AND s.sku_code = 'DEFAULT' WHERE s.id IS NULL");
        DB::statement("UPDATE orders o JOIN goods_skus s ON s.goods_id = o.goods_id AND s.sku_code = 'DEFAULT' SET o.sku_id = s.id WHERE o.sku_id IS NULL");
        DB::statement("UPDATE carmis c JOIN goods_skus s ON s.goods_id = c.goods_id AND s.sku_code = 'DEFAULT' SET c.sku_id = s.id WHERE c.sku_id IS NULL");

        $this->insertMenu('/banner', 'Banner', 26, 19, 23, 'fa-image');
        $this->insertMenu('/goods-sku', 'Goods_SKU', 27, 11, 12, 'fa-tags');
    }

    public function down()
    {
        DB::table('admin_menu')->whereIn('uri', ['/banner', '/goods-sku'])->delete();

        if (Schema::hasColumn('orders', 'sku_id')) {
            Schema::table('orders', function (Blueprint $table) {
                $table->dropColumn('sku_id');
            });
        }

        if (Schema::hasColumn('carmis', 'sku_id')) {
            Schema::table('carmis', function (Blueprint $table) {
                $table->dropColumn('sku_id');
            });
        }

        Schema::dropIfExists('goods_skus');
        Schema::dropIfExists('banners');
    }

    private function insertMenu(string $uri, string $title, int $id, int $parentId, int $order, string $icon): void
    {
        if (DB::table('admin_menu')->where('uri', $uri)->exists()) {
            return;
        }

        DB::table('admin_menu')->insert([
            'parent_id' => $parentId,
            'order' => $order,
            'title' => $title,
            'icon' => $icon,
            'uri' => $uri,
            'extension' => '',
            'show' => 1,
            'created_at' => date('Y-m-d H:i:s'),
            'updated_at' => date('Y-m-d H:i:s'),
        ]);
    }
}
