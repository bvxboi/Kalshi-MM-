# Dynamic Timing Feature

## Overview

The dynamic timing feature allows the market maker to automatically adjust its trading strategy as market expiration approaches. This is particularly useful for markets that close or expire within hours, where risk management becomes increasingly important as the deadline nears.

## Configuration

### Basic Setup

To enable dynamic timing, you need to set two main parameters in your `config.yaml`:

1. **expiry_time**: The absolute expiration time of the market (UTC)
2. **dynamic_timing**: Configuration for how the strategy should adapt

### Example Configuration

```yaml
ETH-3740:
  api:
    market_ticker: KXBTCD-25OCT2117-T110999.99
  market_maker:
    trade_side: "yes"
    max_position: 10

    # Set the market expiration time (UTC)
    expiry_time: "2025-10-25 21:17:00"  # Format: YYYY-MM-DD HH:MM:SS

    # Enable dynamic timing
    dynamic_timing:
      enabled: true

      phases:
        # ... phase configurations ...
```

## Strategy Phases

The bot operates in different phases based on time remaining until expiration:

### 1. Normal Phase (>60 minutes to expiry)
- Standard market making behavior
- Full order sizes
- Normal spreads and risk parameters

### 2. Wind-down Phase (15-60 minutes to expiry)
- Begins reducing risk exposure
- Wider spreads (1.3x multiplier)
- Smaller order sizes (70% of normal)
- More conservative (gamma multiplier: 1.5x)

### 3. Aggressive Unwind Phase (5-15 minutes to expiry)
- Actively works to reduce inventory
- Much wider spreads (2.0x multiplier)
- Smaller orders (40% of normal)
- Very conservative (gamma multiplier: 2.5x)
- Updates every second (dt_override: 1.0)
- Target: Reduce inventory to 50% of current position

### 4. Emergency Exit Phase (<5 minutes to expiry)
- Aggressive position closure
- Tighter spreads for better fills (1.2x multiplier)
- Very small orders (30% of normal)
- Extremely conservative (gamma multiplier: 5.0x)
- Updates twice per second (dt_override: 0.5)
- Target: Exit all positions (inventory_target_ratio: 0.0)

## Phase Parameters

Each phase can be customized with the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `min_time_to_expiry` | Minimum minutes to expiry for this phase to activate | Required |
| `gamma_multiplier` | Multiplies the risk aversion parameter | 1.0 |
| `spread_multiplier` | Multiplies the calculated spreads | 1.0 |
| `order_size_multiplier` | Multiplies the calculated order sizes | 1.0 |
| `dt_override` | Overrides the update frequency (seconds) | null (use default) |
| `inventory_target_ratio` | Target inventory as ratio of current (for unwinding) | null (no target) |

## How It Works

### Time Calculation
- The bot calculates time remaining until `expiry_time`
- Selects the appropriate phase based on minutes remaining
- Applies phase-specific multipliers to all calculations

### Dynamic Adjustments

**Gamma (Risk Aversion)**:
- Higher gamma = wider quotes, more conservative
- Multiplied by `gamma_multiplier` from current phase
- Example: Emergency phase uses 5x gamma for extreme caution

**Spreads**:
- Base spread calculated using Avellaneda-Stoikov formula
- Multiplied by `spread_multiplier` from current phase
- Wider spreads in wind-down to reduce trading
- Tighter spreads in emergency to ensure fills

**Order Sizes**:
- Calculated based on position limits and inventory
- Multiplied by `order_size_multiplier` from current phase
- Smaller sizes near expiry to minimize last-minute risk

**Inventory Unwinding**:
- When `inventory_target_ratio` is set, bot actively works toward that target
- `inventory_target_ratio: 0.5` means reduce to 50% of current inventory
- `inventory_target_ratio: 0.0` means exit all positions
- Only places orders on the unwinding side

### Update Frequency
- Normal dt: 2.0 seconds (from main config)
- Phase can override with `dt_override`
- Emergency phase updates every 0.5 seconds for responsiveness

## Usage Examples

### Example 1: Conservative Unwinding

For markets where you want to minimize end-of-day risk:

```yaml
dynamic_timing:
  enabled: true
  phases:
    normal:
      min_time_to_expiry: 120  # 2 hours
      gamma_multiplier: 1.0
      spread_multiplier: 1.0
      order_size_multiplier: 1.0

    early_unwind:
      min_time_to_expiry: 30  # 30 minutes
      gamma_multiplier: 2.0
      spread_multiplier: 1.5
      order_size_multiplier: 0.5
      inventory_target_ratio: 0.3  # Reduce to 30%

    final_exit:
      min_time_to_expiry: 0
      gamma_multiplier: 3.0
      spread_multiplier: 1.0
      order_size_multiplier: 0.3
      dt_override: 1.0
      inventory_target_ratio: 0.0  # Exit all
```

### Example 2: Aggressive Until Last Minute

For markets where you want to trade actively until the very end:

```yaml
dynamic_timing:
  enabled: true
  phases:
    normal:
      min_time_to_expiry: 5  # Only 5 minutes
      gamma_multiplier: 1.0
      spread_multiplier: 1.0
      order_size_multiplier: 1.0

    quick_exit:
      min_time_to_expiry: 0
      gamma_multiplier: 4.0
      spread_multiplier: 0.8  # Tighter for fills
      order_size_multiplier: 0.5
      dt_override: 0.5
      inventory_target_ratio: 0.0
```

## Disabling Dynamic Timing

To use the original time-based behavior:

```yaml
expiry_time: null  # Or omit this field
dynamic_timing:
  enabled: false
```

Or simply set `T` in `market_maker` config and the bot will run for that duration.

## Logging

The bot logs phase transitions and timing information:

```
Running Avellaneda market maker | Phase: normal | Time to expiry: 45.23 min
Running Avellaneda market maker | Phase: wind_down | Time to expiry: 12.45 min
Running Avellaneda market maker | Phase: aggressive_unwind | Time to expiry: 3.21 min
```

## Best Practices

1. **Test with longer phases first**: Start with conservative thresholds
2. **Monitor inventory unwinding**: Check logs to ensure positions are being reduced as expected
3. **Adjust spreads carefully**: Too wide = no fills, too tight = excessive risk
4. **Use inventory_target_ratio wisely**: Don't set to 0.0 too early, or you'll stop trading prematurely
5. **Consider market liquidity**: Less liquid markets may need tighter spreads in exit phases

## Time Zone Note

All times in `expiry_time` are assumed to be **UTC**. Make sure to convert from your local time zone when setting this value.

Example conversions:
- EST to UTC: Add 5 hours
- PST to UTC: Add 8 hours
- For 5 PM EST expiry: Set to "YYYY-MM-DD 22:00:00"
