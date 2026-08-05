<?php

use App\Http\Controllers\FuelRatioController;
use Illuminate\Support\Facades\Route;

Route::get('/fuel-ratio', [FuelRatioController::class, 'index']);
Route::post('/fuel-ratio/calculate', [FuelRatioController::class, 'store']);

Route::get('{any?}', function() {
    return view('application');
})->where('any', '.*');