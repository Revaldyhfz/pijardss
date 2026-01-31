"""
API Routes.

Defines all REST endpoints for the Pijar DSS backend.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import time
from datetime import datetime
from typing import Optional

from .schemas import (
    SimulationRequest,
    SimulationResponse,
    SummaryStats,
    PathDataResponse,
    PathPercentileResponse,
    OutcomeResponse,
    ReturnBucketResponse,
    RiskMetricsResponse,
    PremortemResponse,
    FailureCauseResponse,
    CriticalPeriodResponse,
    FailureTrajectoryResponse,
    RegimeImpactResponse,
    SensitivityResponse,
    TornadoItemResponse,
    CorrelationResponse,
    SimulationMetaResponse,
)

from ..core.models.parameters import (
    SimulationInput,
    CapitalDevParams,
    SalesParams,
    PricingParams,
    RetentionCostParams,
    SimulationConfig,
    DistributionSpec as InternalDistSpec,
    DistributionType,
    RiskEventConfig,
)
from ..core.simulation import SimulationEngine
from ..core.analytics import (
    RiskAnalyzer,
    SensitivityAnalyzer,
    PremortemAnalyzer,
)
from ..config import get_settings


router = APIRouter()


def convert_dist_spec(api_spec: dict) -> InternalDistSpec:
    """Convert API distribution spec to internal format."""
    dist_type = api_spec.get('type', 'triangular').upper()
    
    # Map string to enum
    type_map = {
        'TRIANGULAR': DistributionType.TRIANGULAR,
        'BETA': DistributionType.BETA,
        'LOGNORMAL': DistributionType.LOGNORMAL,
        'GAMMA': DistributionType.GAMMA,
        'FIXED': DistributionType.FIXED,
    }
    
    return InternalDistSpec(
        type=type_map.get(dist_type, DistributionType.TRIANGULAR),
        params=api_spec.get('params', {})
    )


def build_simulation_input(request: SimulationRequest) -> SimulationInput:
    """Convert API request to internal simulation input."""
    
    # Build risk event configs
    risk_configs = []
    for event in request.risk_events:
        risk_configs.append(RiskEventConfig(
            name=event.name,
            intensity=event.intensity,
            impact_type=event.impact_type,
            severity_min=event.severity_min,
            severity_mode=event.severity_mode,
            severity_max=event.severity_max,
            recovery_rate=event.recovery_rate,
            start_month=event.start_month,
            end_month=event.end_month
        ))
    
    return SimulationInput(
        capital_dev=CapitalDevParams(
            initial_capital=convert_dist_spec(request.initial_capital.model_dump()),
            dev_duration=convert_dist_spec(request.dev_duration.model_dump()),
            dev_burn=convert_dist_spec(request.dev_burn.model_dump()),
        ),
        sales=SalesParams(
            leads_per_month=convert_dist_spec(request.leads_per_month.model_dump()),
            win_rate_bumn=convert_dist_spec(request.win_rate_bumn.model_dump()),
            win_rate_open=convert_dist_spec(request.win_rate_open.model_dump()),
            bumn_ratio=request.bumn_ratio,
            sales_cycle_months=convert_dist_spec(request.sales_cycle_months.model_dump()),
        ),
        pricing=PricingParams(
            contract_small=convert_dist_spec(request.contract_small.model_dump()),
            contract_medium=convert_dist_spec(request.contract_medium.model_dump()),
            contract_large=convert_dist_spec(request.contract_large.model_dump()),
            size_distribution=request.size_distribution,
        ),
        retention_costs=RetentionCostParams(
            churn_rate=convert_dist_spec(request.churn_rate.model_dump()),
            op_overhead=request.op_overhead,
            cost_per_customer=request.cost_per_customer,
        ),
        risk_events=risk_configs,
        config=SimulationConfig(
            n_simulations=request.n_simulations,
            time_horizon=request.time_horizon,
            seed=request.seed,
            enable_regime_switching=request.enable_regime_switching,
            enable_risk_events=request.enable_risk_events,
        )
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": get_settings().app_version
    }


@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    """
    Run Monte Carlo simulation.
    
    This is the main endpoint that:
    1. Runs the Monte Carlo simulation
    2. Performs risk analysis
    3. Runs sensitivity analysis
    4. Generates premortem analysis
    
    Returns complete results for the frontend dashboard.
    """
    try:
        start_time = time.time()
        
        # Convert request to internal format
        sim_input = build_simulation_input(request)
        
        # Create and run simulation engine
        settings = get_settings()
        engine = SimulationEngine(sim_input, n_jobs=settings.n_jobs)
        
        # Run Monte Carlo
        path_results, sim_time = engine.run()
        
        # Aggregate basic results
        basic_result = engine.aggregate_results(path_results, sim_time)
        
        # Run additional analytics
        risk_analyzer = RiskAnalyzer(path_results)
        risk_result = risk_analyzer.analyze()
        
        sensitivity_analyzer = SensitivityAnalyzer(path_results, output_metric='return')
        sensitivity_result = sensitivity_analyzer.analyze()
        
        premortem_analyzer = PremortemAnalyzer(path_results, failure_threshold=-20.0)
        premortem_result = premortem_analyzer.analyze()
        
        total_time = (time.time() - start_time) * 1000
        
        # Build response
        response = SimulationResponse(
            summary=SummaryStats(
                prob_profit=basic_result.summary.prob_profit,
                prob_double=basic_result.summary.prob_double,
                prob_ruin=basic_result.summary.prob_ruin,
                return_mean=basic_result.summary.return_mean,
                return_median=basic_result.summary.return_median,
                return_std=basic_result.summary.return_std,
                return_p5=basic_result.summary.return_p5,
                return_p95=basic_result.summary.return_p95,
                var_5=basic_result.summary.var_5,
                cvar_5=basic_result.summary.cvar_5,
                max_drawdown_mean=basic_result.summary.max_drawdown_mean,
                max_drawdown_p95=basic_result.summary.max_drawdown_p95,
                breakeven_mean=basic_result.summary.breakeven_mean,
                breakeven_rate=basic_result.summary.breakeven_rate,
                recommendation=basic_result.summary.recommendation.value,
            ),
            paths=PathDataResponse(
                percentiles=[
                    PathPercentileResponse(
                        month=p.month,
                        p5=p.p5,
                        p25=p.p25,
                        p50=p.p50,
                        p75=p.p75,
                        p95=p.p95
                    ) for p in basic_result.paths.percentiles
                ],
                sample_paths=basic_result.paths.sample_paths or [],
                median_path=basic_result.paths.median_path,
            ),
            outcomes=OutcomeResponse(
                double_plus=basic_result.outcomes.double_plus,
                profitable=basic_result.outcomes.profitable,
                loss=basic_result.outcomes.loss,
                ruin=basic_result.outcomes.ruin,
                total=basic_result.outcomes.total,
            ),
            return_distribution=[
                ReturnBucketResponse(
                    range_start=b.range_start,
                    range_end=b.range_end,
                    count=b.count,
                    percentage=b.percentage
                ) for b in basic_result.return_distribution
            ],
            risk_metrics=RiskMetricsResponse(
                var={k: v.var_absolute for k, v in risk_result.var.items()},
                cvar={k: v.cvar_absolute for k, v in risk_result.cvar.items()},
                drawdown_mean=risk_result.drawdown.mean,
                drawdown_std=risk_result.drawdown.std,
                drawdown_p95=risk_result.drawdown.p95,
                drawdown_max=risk_result.drawdown.max_observed,
                months_underwater_mean=risk_result.underwater.mean_months_underwater,
                survival_curve=risk_result.survival.survival_curve,
                tail_loss_mean=risk_result.tail.tail_mean_return,
            ),
            premortem=PremortemResponse(
                failure_definition=premortem_result.failure_definition,
                failure_rate=premortem_result.failure_rate,
                failure_count=premortem_result.failure_count,
                primary_causes=[
                    FailureCauseResponse(
                        factor=c.factor,
                        display_name=c.display_name,
                        failed_mean=c.failed_mean,
                        success_mean=c.success_mean,
                        difference_pct=c.difference_pct,
                        attribution_score=c.attribution_score,
                        direction=c.direction,
                        interpretation=c.interpretation
                    ) for c in premortem_result.primary_causes[:5]
                ],
                cause_interactions=[
                    {"cause1": c[0], "cause2": c[1], "cooccurrence": c[2]}
                    for c in premortem_result.cause_interactions
                ],
                critical_periods=[
                    CriticalPeriodResponse(
                        start_month=p.start_month,
                        end_month=p.end_month,
                        hazard_rate=p.hazard_rate,
                        cumulative_failures=p.cumulative_failures,
                        dominant_cause=p.dominant_cause
                    ) for p in premortem_result.critical_periods
                ],
                failure_timing_histogram=premortem_result.failure_timing_histogram,
                median_failure_month=premortem_result.median_failure_month,
                failure_trajectories=[
                    FailureTrajectoryResponse(
                        trajectory_type=t.trajectory_type,
                        prevalence=t.prevalence,
                        months_to_failure=t.months_to_failure,
                        peak_capital_reached=t.peak_capital_reached,
                        warning_signs=t.warning_signs
                    ) for t in premortem_result.failure_trajectories
                ],
                regime_impacts=[
                    RegimeImpactResponse(
                        regime=r.regime,
                        time_spent_pct=r.time_spent_pct,
                        conditional_failure_rate=r.conditional_failure_rate,
                        risk_multiplier=r.risk_multiplier
                    ) for r in premortem_result.regime_impacts
                ],
                early_warning_signals=premortem_result.early_warning_signals,
                mitigation_priorities=premortem_result.mitigation_priorities,
            ),
            sensitivity=SensitivityResponse(
                tornado=[
                    TornadoItemResponse(
                        parameter=t.parameter,
                        display_name=t.display_name,
                        low_value=t.low_value,
                        base_value=t.base_value,
                        high_value=t.high_value,
                        output_at_low=t.output_at_low,
                        output_at_base=t.output_at_base,
                        output_at_high=t.output_at_high,
                        swing=t.swing
                    ) for t in sensitivity_result.tornado
                ],
                correlations=[
                    CorrelationResponse(
                        parameter=c.parameter,
                        spearman_corr=c.spearman_corr,
                        is_significant=c.is_significant
                    ) for c in sensitivity_result.correlations
                ],
                top_positive_drivers=sensitivity_result.top_positive_drivers,
                top_negative_drivers=sensitivity_result.top_negative_drivers,
                total_r2=sensitivity_result.total_r2,
            ),
            meta=SimulationMetaResponse(
                n_simulations=request.n_simulations,
                time_horizon=request.time_horizon,
                seed=request.seed,
                computation_time_ms=total_time,
                timestamp=datetime.utcnow().isoformat(),
            )
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets")
async def get_presets():
    """
    Get predefined parameter presets.
    
    Returns preset configurations for quick scenario testing.
    """
    return {
        "presets": {
            "base": {
                "name": "Base Case",
                "description": "Default parameters based on market research",
                "initial_capital": {"type": "triangular", "params": {"min": 4000, "mode": 5000, "max": 6000}},
                "dev_duration": {"type": "triangular", "params": {"min": 4, "mode": 6, "max": 9}},
                "dev_burn": {"type": "triangular", "params": {"min": 160, "mode": 200, "max": 250}},
                "leads_per_month": {"type": "triangular", "params": {"min": 4, "mode": 7, "max": 12}},
                "win_rate_bumn": {"type": "beta", "params": {"alpha": 14, "beta": 6}},
                "win_rate_open": {"type": "beta", "params": {"alpha": 4, "beta": 14}},
            },
            "conservative": {
                "name": "Conservative",
                "description": "Pessimistic assumptions for risk assessment",
                "initial_capital": {"type": "triangular", "params": {"min": 5000, "mode": 6000, "max": 7000}},
                "dev_duration": {"type": "triangular", "params": {"min": 6, "mode": 8, "max": 12}},
                "dev_burn": {"type": "triangular", "params": {"min": 180, "mode": 220, "max": 280}},
                "leads_per_month": {"type": "triangular", "params": {"min": 3, "mode": 5, "max": 8}},
                "win_rate_bumn": {"type": "beta", "params": {"alpha": 10, "beta": 6}},
                "win_rate_open": {"type": "beta", "params": {"alpha": 3, "beta": 15}},
            },
            "aggressive": {
                "name": "Aggressive",
                "description": "Optimistic assumptions for upside assessment",
                "initial_capital": {"type": "triangular", "params": {"min": 6000, "mode": 7000, "max": 8500}},
                "dev_duration": {"type": "triangular", "params": {"min": 3, "mode": 5, "max": 7}},
                "dev_burn": {"type": "triangular", "params": {"min": 200, "mode": 280, "max": 350}},
                "leads_per_month": {"type": "triangular", "params": {"min": 6, "mode": 10, "max": 15}},
                "win_rate_bumn": {"type": "beta", "params": {"alpha": 18, "beta": 5}},
                "win_rate_open": {"type": "beta", "params": {"alpha": 5, "beta": 12}},
            },
        }
    }