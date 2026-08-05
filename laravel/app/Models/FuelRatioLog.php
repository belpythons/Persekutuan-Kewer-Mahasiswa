<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class FuelRatioLog extends Model
{
    use HasFactory;

    protected $fillable = [
        'equipment_id',
        'operating_hours',
        'fuel_consumed_liters',
        'load_tonnage',
        'calculated_fuel_ratio',
    ];
}
