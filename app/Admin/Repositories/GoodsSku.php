<?php

namespace App\Admin\Repositories;

use App\Models\GoodsSku as Model;
use Dcat\Admin\Repositories\EloquentRepository;

class GoodsSku extends EloquentRepository
{
    protected $eloquentClass = Model::class;
}
