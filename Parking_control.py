import os
import sys
import traci
import traci.constants as tc
import random

if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))

sumo_config_file = r"C:\Users\pucso\Desktop\Traffic_Sim_Project\sumo_config_file.sumocfg"

class ParkingSimulation:

    def __init__(self, sumo_config_file):
        self.sumo_config_file = sumo_config_file
        self.parked_vehicles = set()
        self.used_parking_spots = {}
        self.MAX_ITERATIONS = 10
        self.iteration_count = {}
        

    def start_simulation(self):
        sumoCmd = ["sumo-gui", "-c", self.sumo_config_file, "--start"]
        traci.start(sumoCmd)

    def get_available_parking_spots(self, vehicle_position, search_radius=30):
        parking_spots = traci.parkingarea.getIDList()
        available_spots = []

        for spotID in parking_spots:
            vehicle_position_x, vehicle_position_y = vehicle_position
            spot_position_x = traci.parkingarea.getStartPos(spotID)
            spot_position_y = traci.parkingarea.getEndPos(spotID)

            distance = traci.simulation.getDistance2D(vehicle_position_x, vehicle_position_y, spot_position_x, spot_position_y)
            occupied = traci.simulation.getParameter(spotID, "parkingArea.occupancy")

            if distance <= search_radius and occupied != 1:
                available_spots.append(spotID)
        
        return available_spots

    def choose_random_parking_spot(self, available_spots, vehicle_route):
        if not available_spots:
            print("No available parking spots")
            return None 
        
        pointer = True

        while pointer:
            random_spot = random.choice(available_spots)

            laneID = traci.parkingarea.getLaneID(random_spot)
            edgeID = traci.lane.getEdgeID(laneID)

            if edgeID in vehicle_route:
                pointer = False
                print(f"The chosen parking spot is: {random_spot}")
                return random_spot

    def parking_simulation(self): 
        
        while traci.simulation.getMinExpectedNumber() > 0:
            try:
                for _ in range(200):
                    veh_id_list = list(traci.vehicle.getIDList())

                    for veh_id in veh_id_list:
                        
                        if veh_id not in self.parked_vehicles:
                            
                            if veh_id in self.iteration_count:
                                self.iteration_count[veh_id] += 1
                            else:
                                self.iteration_count[veh_id] = 1
                            
                            if self.iteration_count[veh_id] > self.MAX_ITERATIONS:
                                continue
                            
                            veh_pos = traci.vehicle.getPosition(veh_id)
                            veh_route = traci.vehicle.getRoute(veh_id)

                            available_parking_spots = self.get_available_parking_spots(veh_pos)
                            choosed_spot = self.choose_random_parking_spot(available_parking_spots, veh_route)

                            if choosed_spot not in self.used_parking_spots:

                                if choosed_spot:
                                    print(f"ID {veh_id} vehicle booked to {choosed_spot}")
                                    traci.vehicle.setParkingAreaStop(veh_id, choosed_spot, duration="30")
                                    self.parked_vehicles.add(veh_id)
                                    self.used_parking_spots.add(choosed_spot)
                                    
                    traci.simulationStep()

            except Exception as e:
                print("An error occurred:", e)
                continue

        print("End of Simulation")

if __name__ == "__main__":
    parking_sim = ParkingSimulation(sumo_config_file)
    parking_sim.start_simulation()
    parking_sim.parking_simulation()
