# Business Use Cases

## Overview
This document outlines the primary operational scenarios the "Calculator Încărcare Țeavă HDPE" is designed to handle.

## Scenario A: High Volume, Low Weight (PN6)
**Context**: Transporting large diameter thin-walled pipes (e.g., DN110 PN6).
- **Challenge**: The truck fills up volumetrically long before hitting the 24t limit.
- **Solution**:
  - **Stacking**: Application maximizes hexagonal stacking height (up to 2.7m).
  - **Optimization**: No nesting required (pipes are too light/thin).
  - **Outcome**: 100% Volume utilization, ~10% Weight utilization. Low cost efficiency per km, but optimized for the specific order.

## Scenario B: High Weight, Low Volume (PN16)
**Context**: Heavy duty pipes (e.g., DN800 PN16, 168kg/m).
- **Challenge**: A single pipe weighs >2 tons. 10 pipes hit the 24t limit.
- **Solution**:
  - **Limit Check**: Application strictly enforces the 24t payload limit.
  - **Splitting**: Order is split across multiple trucks.
  - **Efficiency Warning**: "Truck 2 is only 10% full by volume. Recommend adding lighter items to mix."
  - **Outcome**: 100% Weight utilization, Low Volume utilization.

## Scenario C: The "Intercalated" Order (Optimal)
**Context**: Mixed order of large (DN630), medium (DN315), and small (DN110) pipes.
- **Challenge**: Transporting separately would require 3 trucks.
- **Solution (Matryoshka Strategy)**:
  1.  **Host**: DN630 serves as the container.
  2.  **Level 1**: DN315 inserted into DN630.
  3.  **Level 2**: 2x DN110 inserted into DN315.
- **Outcome**:
  - **Trucks Reduced**: From 3 to 1.
  - **Cost Savings**: ~66% reduction in transport costs.
  - **Utilization**: Balanced Volume and Weight.

## User Persona: The Logistics Manager
- **Goal**: Minimize transport invoice value.
- **Action**: Uses the "Calculate Load" button to simulate different order compositions before confirming with production.
- **Requirement**: Needs instant feedback on "Trucks Needed".
