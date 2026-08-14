# Stage 5 source fragments

The 14 ordered `part_*.pyfrag` files concatenate with no separator to the exact tested Stage 5 Python program. The fragmentation is a transport detail only. Before compilation and execution, `scripts/run_stage5_model_suite.py` verifies the fragment names, assembled byte count, and assembled SHA-256 against `config/stage5_source_contract.json`.
