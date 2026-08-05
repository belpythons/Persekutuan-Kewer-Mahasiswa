<?php

namespace App\Http\Controllers;

use App\Http\Requests\StoreFuelRatioRequest;
use App\Services\FuelRatioService;
use App\Repositories\Contracts\FuelRatioRepositoryInterface;
use Inertia\Inertia;
use Exception;

class FuelRatioController extends Controller
{
    protected $service;
    protected $repository;

    public function __construct(FuelRatioService $service, FuelRatioRepositoryInterface $repository)
    {
        $this->service = $service;
        $this->repository = $repository;
    }

    public function index()
    {
        return Inertia::render('FuelRatioAnalytics', [
            'logs' => $this->repository->getAllRecent()
        ]);
    }

    public function store(StoreFuelRatioRequest $request)
    {
        try {
            $this->service->calculateAndSave($request->validated());
            return redirect()->back()->with('success', 'Fuel ratio successfully calculated and saved.');
        } catch (Exception $e) {
            return redirect()->back()->withErrors([
                'api_error' => 'Failed to connect to AI Prediction Service: ' . $e->getMessage()
            ]);
        }
    }
}
