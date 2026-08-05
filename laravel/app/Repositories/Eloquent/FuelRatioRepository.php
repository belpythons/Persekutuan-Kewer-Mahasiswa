<?php

namespace App\Repositories\Eloquent;

use App\Models\FuelRatioLog;
use App\Repositories\Contracts\FuelRatioRepositoryInterface;
use Illuminate\Support\Collection;

class FuelRatioRepository implements FuelRatioRepositoryInterface
{
    public function create(array $data): FuelRatioLog
    {
        return FuelRatioLog::create($data);
    }

    public function getAllRecent(): Collection
    {
        return FuelRatioLog::latest()->take(10)->get();
    }
}
