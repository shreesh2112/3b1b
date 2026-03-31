import numpy as np
from scipy.integrate import dblquad

def calculate_pc_and_assess(miss_distance, combined_radius, sigma_x, sigma_y):
    """
    1. CALCULATE Pc:
    Integrates the probability density function (PDF) over the 
    circular area of the Hard Body Radius (HBR).
    """
    
    # 2D Gaussian PDF (The 'Uncertainty Cloud')
    def pdf(y, x):
        # We center the distribution at (miss_distance, 0) on the encounter plane
        exponent = -0.5 * ((x - miss_distance)**2 / sigma_x**2 + y**2 / sigma_y**2)
        return (1.0 / (2 * np.pi * sigma_x * sigma_y)) * np.exp(exponent)

    # Double Integration over the area of the combined objects (x^2 + y^2 <= R^2)
    pc, _ = dblquad(
        pdf, 
        -combined_radius, combined_radius,
        lambda x: -np.sqrt(combined_radius**2 - x**2),
        lambda x: np.sqrt(combined_radius**2 - x**2)
    )

    """
    2. ASSESS RISK:
    Maps the float probability to industry-standard action tiers.
    """
    if pc < 1e-7:
        level, color, action = "LOW", "Green", "Monitor"
    elif 1e-7 <= pc < 1e-5:
        level, color, action = "MEDIUM", "Yellow", "Increase Tracking"
    elif 1e-5 <= pc < 1e-4:
        level, color, action = "HIGH", "Orange", "Plan Maneuver"
    else: # pc >= 1e-4
        level, color, action = "CRITICAL", "Red", "EXECUTE EVASION"

    return {
        "probability": pc,
        "risk_level": level,
        "ui_color": color,
        "recommended_action": action
    }

# --- EXAMPLE TEST CASE FOR THE TEAM ---
# Miss distance: 250 meters
# Combined Radius: 10 meters (Two large satellites)
# Uncertainty: 500m (Along-track), 100m (Cross-track)

result = calculate_pc_and_assess(250, 10, 500, 100)

print(f"--- COLLISION REPORT ---")
print(f"Calculated Pc: {result['probability']:.2e}")
print(f"Risk Level:    [{result['risk_level']}]")
print(f"Action:        {result['recommended_action']}")