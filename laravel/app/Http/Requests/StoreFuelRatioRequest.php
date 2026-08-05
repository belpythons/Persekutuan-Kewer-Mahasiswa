<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreFuelRatioRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'equipment_id' => 'required|string|max:50',
            'operating_hours' => 'required|numeric|min:0.1',
            'fuel_consumed_liters' => 'required|numeric|min:0.1',
            'load_tonnage' => 'required|numeric|min:0.1',
        ];
    }
}
