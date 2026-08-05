<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('fuel_ratio_logs', function (Blueprint $table) {
            $table->id();
            $table->string('equipment_id');
            $table->decimal('operating_hours', 8, 2);
            $table->decimal('fuel_consumed_liters', 8, 2);
            $table->decimal('load_tonnage', 8, 2);
            $table->decimal('calculated_fuel_ratio', 8, 2);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('fuel_ratio_logs');
    }
};
