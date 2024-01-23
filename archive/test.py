class CentrifugeBase:
    def __init__(self, process_name, density_key, prod_factor, waste_liquid_factor=None, recycle_factor=None):
        self.process_name = process_name
        self.density_key = density_key
        self.prod_factor = prod_factor
        self.waste_liquid_factor = waste_liquid_factor
        self.recycle_factor = recycle_factor

    def execute(self, prod, previous_process_output):
        # Default implementation uses the waste_liquid_factor if provided
        if self.waste_liquid_factor is not None:
            waste_centri = self.waste_liquid_factor * prod
        # Add more logic as necessary

        # Return some output, modify as needed for your actual implementation
        return {
            'centri_out': prod * self.prod_factor,
            'waste_centri': waste_centri,
            # ... other outputs
        }


class CentrifugeSpecial(CentrifugeBase) :
    def __init__(self, process_name, density_key, prod_factor, specific_waste_key) :
        # Initialize the base class without a waste_liquid_factor
        super().__init__(process_name, density_key, prod_factor)
        self.specific_waste_key = specific_waste_key

    def execute(self, prod, previous_process_output) :
        # Retrieve specific waste production value from previous_process_output using the provided key
        specific_waste = previous_process_output[self.specific_waste_key]

        # Use the retrieved specific waste for calculations
        waste_centri = specific_waste  # assuming waste is directly used from previous output
        elec_centri = specific_waste / 100  # assuming electric calculation as provided

