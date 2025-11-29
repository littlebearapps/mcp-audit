# Idea: What-If Simulations

**Status**: Proposed
**Priority**: Medium
**Phase**: v1.0+
**Related**: idea-static-mcp-footprint-analyzer.md, idea-context-categories-reports.md

---

## Summary

Enable users to simulate the impact of configuration changes (disabling servers, trimming descriptions) on context usage and costs without actually making those changes.

---

## Problem Statement

Users want to optimize their MCP setup but:

- Don't know which changes will have the biggest impact
- Are hesitant to disable servers without understanding consequences
- Can't easily quantify "if I trim descriptions by 50%, how much do I save?"

What-if simulations let users experiment safely with data they already have.

---

## Proposed Solution

### CLI Interface

```bash
# Simulate disabling specific servers
mcp-audit report --what-if disable=mcp__omnisearch,mcp__github

# Simulate trimming tool descriptions
mcp-audit report --what-if trim-descriptions=0.5

# Combine simulations
mcp-audit report --what-if disable=mcp__docs --what-if trim-descriptions=0.3

# Compare original vs simulated
mcp-audit report --what-if disable=mcp__omnisearch --compare
```

### Simulation Types

#### 1. Disable Server

Remove a server's contribution entirely:

```
What-If: Disable mcp__omnisearch
──────────────────────────────────────────
                        Original    Simulated    Savings
Static metadata         28,544      14,330       14,214 (50%)
Dynamic tool outputs    91,331      52,000       39,331 (43%)
Total context          137,000      83,455       53,545 (39%)
Estimated cost/session   $0.42       $0.26        $0.16 (38%)
```

#### 2. Trim Descriptions

Reduce static metadata by a percentage:

```
What-If: Trim descriptions by 50%
──────────────────────────────────────────
                        Original    Simulated    Savings
MCP tool metadata       28,544      14,272       14,272 (50%)
Per-call overhead       12,000       8,500        3,500 (29%)
Session cost             $0.42       $0.35        $0.07 (17%)
```

#### 3. Disable Specific Tools

Remove individual tools while keeping server:

```
What-If: Disable mcp__omnisearch.web_search
──────────────────────────────────────────
Tool web_search:
  • Static metadata:    700 tokens removed
  • Dynamic outputs:  52,310 tokens removed (avg 6,539/call)
  • Calls avoided:          8

Session impact:
  • Context freed:    53,010 tokens (39%)
  • Cost saved:         $0.16 (38%)
```

#### 4. Replace with Cheaper Tool

Estimate impact of using alternative:

```
What-If: Replace mcp__omnisearch.web_search with mcp__lite.search
──────────────────────────────────────────
                        Current     Alternative   Difference
Avg tokens/call          6,539         2,100       -4,439 (68%)
Static metadata            700           200         -500 (71%)
Session cost (8 calls)   $0.18         $0.06       -$0.12 (67%)
```

---

## Implementation Details

### Simulation Engine

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class WhatIfScenario:
    type: str  # disable_server, trim_descriptions, disable_tool, replace_tool
    target: str  # server or tool name
    value: float | str | None = None  # trim percentage or replacement

@dataclass
class SimulationResult:
    original_tokens: int
    simulated_tokens: int
    original_cost: float
    simulated_cost: float

    @property
    def tokens_saved(self) -> int:
        return self.original_tokens - self.simulated_tokens

    @property
    def cost_saved(self) -> float:
        return self.original_cost - self.simulated_cost

    @property
    def savings_percent(self) -> float:
        if self.original_tokens == 0:
            return 0.0
        return (self.tokens_saved / self.original_tokens) * 100


class WhatIfSimulator:
    def __init__(self, session: Session, footprints: Dict[str, ServerFootprint]):
        self.session = session
        self.footprints = footprints

    def simulate(self, scenarios: List[WhatIfScenario]) -> SimulationResult:
        """Apply scenarios and calculate impact."""
        original = self._calculate_baseline()
        simulated = self._apply_scenarios(original, scenarios)
        return SimulationResult(
            original_tokens=original.total_tokens,
            simulated_tokens=simulated.total_tokens,
            original_cost=original.total_cost,
            simulated_cost=simulated.total_cost
        )

    def _calculate_baseline(self) -> SessionMetrics:
        """Calculate original session metrics."""
        # Sum all token usage from session
        return SessionMetrics(
            total_tokens=sum(c.input_tokens for c in self.session.calls),
            total_cost=sum(c.cost for c in self.session.calls),
            by_server=self._group_by_server()
        )

    def _apply_scenarios(self, baseline: SessionMetrics, scenarios: List[WhatIfScenario]) -> SessionMetrics:
        """Apply what-if scenarios to baseline."""
        result = baseline.copy()

        for scenario in scenarios:
            if scenario.type == "disable_server":
                result = self._disable_server(result, scenario.target)
            elif scenario.type == "trim_descriptions":
                result = self._trim_descriptions(result, scenario.value)
            elif scenario.type == "disable_tool":
                result = self._disable_tool(result, scenario.target)

        return result

    def _disable_server(self, metrics: SessionMetrics, server: str) -> SessionMetrics:
        """Remove all contributions from a server."""
        if server not in metrics.by_server:
            return metrics

        server_tokens = metrics.by_server[server].total_tokens
        server_cost = metrics.by_server[server].total_cost

        # Also remove static footprint
        static_tokens = self.footprints.get(server, ServerFootprint()).total_tokens

        return SessionMetrics(
            total_tokens=metrics.total_tokens - server_tokens - static_tokens,
            total_cost=metrics.total_cost - server_cost,
            by_server={k: v for k, v in metrics.by_server.items() if k != server}
        )

    def _trim_descriptions(self, metrics: SessionMetrics, factor: float) -> SessionMetrics:
        """Reduce static metadata by factor (e.g., 0.5 = 50% reduction)."""
        static_reduction = sum(
            fp.total_tokens * factor
            for fp in self.footprints.values()
        )

        return SessionMetrics(
            total_tokens=metrics.total_tokens - static_reduction,
            total_cost=metrics.total_cost,  # Static doesn't affect per-call cost
            by_server=metrics.by_server
        )
```

### CLI Integration

```python
@app.command()
def report(
    what_if: List[str] = typer.Option(None, help="What-if scenarios (e.g., disable=mcp__foo)"),
    compare: bool = typer.Option(False, help="Show original vs simulated side-by-side"),
):
    """Generate report with optional what-if simulations."""
    session = load_latest_session()
    footprints = load_footprint_cache()

    if what_if:
        scenarios = parse_what_if_args(what_if)
        simulator = WhatIfSimulator(session, footprints)
        result = simulator.simulate(scenarios)

        if compare:
            print_comparison_report(session, result)
        else:
            print_simulation_report(result)
    else:
        print_standard_report(session)


def parse_what_if_args(args: List[str]) -> List[WhatIfScenario]:
    """Parse --what-if arguments into scenarios."""
    scenarios = []
    for arg in args:
        if arg.startswith("disable="):
            servers = arg.replace("disable=", "").split(",")
            for server in servers:
                scenarios.append(WhatIfScenario(
                    type="disable_server",
                    target=server
                ))
        elif arg.startswith("trim-descriptions="):
            factor = float(arg.replace("trim-descriptions=", ""))
            scenarios.append(WhatIfScenario(
                type="trim_descriptions",
                value=factor
            ))
    return scenarios
```

---

## User Value

- **Safe experimentation**: Test changes without modifying config
- **Data-driven decisions**: Quantify impact before acting
- **MCP server optimization**: Guides authors on where to trim
- **Cost forecasting**: Predict savings from planned changes

---

## Example Output

```
What-If Analysis
════════════════════════════════════════════════════════════════

Scenarios Applied:
  1. Disable mcp__omnisearch
  2. Trim descriptions by 50%

Results
────────────────────────────────────────────────────────────────
Metric                    Original        Simulated       Savings
────────────────────────────────────────────────────────────────
Static metadata           28,544          7,165           21,379 (75%)
Dynamic tokens           108,456         56,290           52,166 (48%)
Total context            137,000         63,455           73,545 (54%)
────────────────────────────────────────────────────────────────
Estimated cost             $0.42           $0.19            $0.23 (55%)
────────────────────────────────────────────────────────────────

Recommendations:
  → mcp__omnisearch alone accounts for 53,545 tokens (39%)
  → Consider consolidating omnisearch tools or using on-demand
  → Trimming descriptions saves 7,136 tokens (5%) with minimal effort
```

---

## Dependencies

- Static footprint analyzer (for metadata token counts)
- Per-server/tool usage tracking (existing)
- Cost calculation module (existing)

---

## Success Metrics

- Users can run what-if simulations in <3 seconds
- At least 3 scenario types supported
- Simulations match actual results within 10% accuracy

---

## References

- MCP context optimization articles
- Tool consolidation case studies
