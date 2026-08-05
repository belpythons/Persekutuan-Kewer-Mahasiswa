<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class FuelRatioServiceTest extends TestCase
{
    use RefreshDatabase;

    public function test_fuel_ratio_calculation_stores_data_successfully(): void
    {
        Http::fake([
            '*/api/v1/predict-fuel-ratio' => Http::response([
                'equipment_id' => 'EXCA-999',
                'calculated_fuel_ratio' => 2.50,
                'status' => 'success'
            ], 200)
        ]);

        $payload = [
            'equipment_id' => 'EXCA-999',
            'operating_hours' => 10.0,
            'fuel_consumed_liters' => 250.0,
            'load_tonnage' => 100.0,
        ];

        $response = $this->post('/fuel-ratio/calculate', $payload);

        $response->assertStatus(302);
        $this->assertDatabaseHas('fuel_ratio_logs', [
            'equipment_id' => 'EXCA-999',
            'calculated_fuel_ratio' => 2.50,
        ]);
    }

    public function test_fuel_ratio_calculation_falls_back_when_python_service_is_offline(): void
    {
        Http::fake(function () {
            throw new \Illuminate\Http\Client\ConnectionException("Connection refused");
        });

        $payload = [
            'equipment_id' => 'EXCA-OFFLINE',
            'operating_hours' => 10.0,
            'fuel_consumed_liters' => 250.0,
            'load_tonnage' => 100.0,
        ];

        $response = $this->post('/fuel-ratio/calculate', $payload);

        $response->assertStatus(302);
        $this->assertDatabaseHas('fuel_ratio_logs', [
            'equipment_id' => 'EXCA-OFFLINE',
            'calculated_fuel_ratio' => 2.50,
        ]);
    }
}
