<?php

namespace App\Repositories\Contracts;

use App\Models\FuelRatioLog;
use Illuminate\Support\Collection;

interface FuelRatioRepositoryInterface
{
    public function create(array $data): FuelRatioLog;
    public function getAllRecent(): Collection;
}
