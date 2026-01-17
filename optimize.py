import openmdao.api as om

from util import calculate_data

## AI ## rewrite later - for testing purposes !!!



class IDSEvaluator(om.ExplicitComponent):
    def setup(self):
        # Design Variables
        self.add_input('e', val=1.0)
        self.add_input('w1', val=0.5)  # Weight (0 to 1)
        self.add_input('l', val=50.0)  # Window Length (Integer-like)
        self.add_input('fl', val=5.0)  # Frame Length (Integer-like)

        # Objectives
        self.add_output('ttd', val=0.0)
        self.add_output('fa', val=0.0)
        self.add_output('md', val=0.0)

    def compute(self, inputs, outputs):
        result = calculate_data(
            file = './data/attack/DoS-4-a.csv',
            e = inputs['e'][0],
            w1 = inputs['w1'][0],
            l = inputs['l'][0],
            fl = inputs['fl'][0],
            simple=True,
            cache=False
        )

        outputs['ttd'] = result['ttd']
        outputs['fa'] = result['fa']
        outputs['md'] = result['md']


# -------------------------------------------------------------------------
# 2. Optimization Helper Function (Genetic Algorithm)
# -------------------------------------------------------------------------

def run_optimization_phase(phase_name, obj_name, constraints, guess_values):
    print(f"\n=== Running {phase_name} (Minimize {obj_name}) ===")

    prob = om.Problem()
    prob.model.add_subsystem('ids', IDSEvaluator(), promotes=['*'])

    # Use Genetic Algorithm (Robust to mixed float/int variables)
    prob.driver = om.SimpleGADriver()
    prob.driver.options['max_gen'] = 50  # Increase for better accuracy
    prob.driver.options['pop_size'] = 25
    prob.driver.options['bits'] = {'e': 10, 'w1': 10, 'l': 8, 'fl': 6}  # Resolution bits

    # --- DESIGN VARIABLES ---
    # Continuous variables
    prob.model.add_design_var('e', lower=0.1, upper=10.0)
    prob.model.add_design_var('w1', lower=0.0, upper=1.0)  # Corrected Range

    # Discrete/Integer variables
    # (GA treats them as floats, calculate_data casts them to int)
    prob.model.add_design_var('l', lower=10.0, upper=200.0)
    prob.model.add_design_var('fl', lower=1.0, upper=20.0)

    # Add Objective
    prob.model.add_objective(obj_name)

    # Add Constraints (Epsilon constraints)
    for con in constraints:
        prob.model.add_constraint(con['name'], upper=con['upper'])

    prob.setup()

    # Set initial guess
    for var, val in guess_values.items():
        prob.set_val(var, val)

    prob.run_driver()

    # Extract results
    results = {
        'e': prob.get_val('e')[0],
        'w1': prob.get_val('w1')[0],
        'l': prob.get_val('l')[0],
        'fl': prob.get_val('fl')[0],
        'fa': prob.get_val('fa')[0],
        'ttd': prob.get_val('ttd')[0],
        'md': prob.get_val('md')[0],
    }

    return results


# -------------------------------------------------------------------------
# 3. Main Execution: Epsilon Constraint Method
# -------------------------------------------------------------------------

def runoptimizer():
    # Relaxations: How much we allow a priority to "worsen"
    # to help the next priority in line.
    EPS_FA = 0.5  # Allow +0.5 False Alarms to help TTD
    EPS_TTD = 1.0  # Allow +1.0 Frames of delay to help MD

    # Initial Guesses
    current_guess = {'e': 2.7, 'w1': 0.8, 'l': 50.0, 'fl': 8.0}

    # === PHASE 1: Minimize False Alarm (Highest Priority) ===
    # Result: We find the absolute best FA possible.
    res1 = run_optimization_phase("Phase 1", "fa", [], current_guess)

    # Setup for Phase 2: Protect the FA score we just found
    fa_limit = res1['fa'] + EPS_FA
    current_guess.update(res1)

    # === PHASE 2: Minimize TTD (Medium Priority) ===
    # Constraint: Keep FA within the limit found in Phase 1
    res2 = run_optimization_phase("Phase 2", "ttd",
                                  [{'name': 'fa', 'upper': fa_limit}],
                                  current_guess)

    # Setup for Phase 3: Protect the TTD score we just found
    ttd_limit = res2['ttd'] + EPS_TTD
    current_guess.update(res2)

    # === PHASE 3: Minimize Missed Detection (Lowest Priority) ===
    # Constraints: Keep FA and TTD within their established limits
    res3 = run_optimization_phase("Phase 3", "md",
                                  [{'name': 'fa', 'upper': fa_limit},
                                   {'name': 'ttd', 'upper': ttd_limit}],
                                  current_guess)



    # -------------------------------------------------------------------------
    # Final Report
    # -------------------------------------------------------------------------
    print("\n" + "=" * 40)
    print("FINAL OPTIMAL CONFIGURATION")
    print("=" * 40)
    print(f"Inputs:")
    print(f"  e  (Threshold) : {res3['e']:.4f}")
    print(f"  w1 (Weight)    : {res3['w1']:.4f}  (w2 = {1.0 - res3['w1']:.4f})")
    print(f"  l  (Window)    : {int(res3['l'])}")
    print(f"  fl (Frame Len) : {int(res3['fl'])}")
    print("-" * 20)
    print(f"Outputs:")
    print(f"  False Alarms   : {res3['fa']:.4f} (Limit: {fa_limit:.4f})")
    print(f"  Time to Detect : {res3['ttd']:.4f} (Limit: {ttd_limit:.4f})")
    print(f"  Missed Detect  : {res3['md']:.4f} (Minimized)")
    return res3