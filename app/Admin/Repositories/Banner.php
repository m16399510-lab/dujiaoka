<?php

namespace App\Admin\Repositories;

use App\Models\Banner as Model;
use Dcat\Admin\Repositories\EloquentRepository;

class Banner extends EloquentRepository
{
    protected $eloquentClass = Model::class;
}
