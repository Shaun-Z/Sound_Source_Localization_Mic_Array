# -*- coding: utf-8 -*-
import sys
import os
import math
import time
import numpy as np

try:
    import usb.core
    import usb.util
except ImportError:
    print("Warning: pyusb not installed. Install with: pip install pyusb")

# Add parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

try:
    from tuning import Tuning
except ImportError:
    print("Warning: tuning module not found. Make sure tuning.py is in parent directory.")

class ThreeArrayLocalization3D:
    def __init__(self, array_distance=1.0):
        """
        3D localization using 3 microphone arrays positioned on orthogonal planes
        
        Array positioning:
        - Array 1: XY plane (horizontal plane, z=0)
        - Array 2: XZ plane (vertical plane facing forward, y=0) 
        - Array 3: YZ plane (vertical plane facing sideways, x=0)
        
        Each array provides one DOA angle in its respective plane
        """
        self.L = array_distance
        
        # Array positions (center of each array)
        self.array1_center = np.array([0.03, 0.08, 0])      # XY plane center
        self.array2_center = np.array([0.05, 0, 0.06])      # XZ plane center  
        self.array3_center = np.array([0, 0.03, 0.06])      # YZ plane center
        
    def triangulate_from_three_arrays(self, doa1_xy, doa2_xz, doa3_yz):
        """
        Triangulate 3D position from DOA readings of three orthogonal arrays
        
        Args:
            doa1_xy: Direction of arrival from Array 1 (in XY plane, degrees from +X axis)
            doa2_xz: Direction of arrival from Array 2 (in XZ plane, degrees from +X axis)  
            doa3_yz: Direction of arrival from Array 3 (in YZ plane, degrees from +Y axis)
            
        Returns:
            (x, y, z) position of sound source
        """
        
        # Convert DOA angles to radians
        doa1_rad = math.radians(doa1_xy)
        doa2_rad = math.radians(doa2_xz)
        doa3_rad = math.radians(doa3_yz)
        
        # Create direction vectors for each array
        # Array 1 (XY plane): direction in XY plane
        dir1 = np.array([math.cos(doa1_rad), math.sin(doa1_rad), 0])
        
        # Array 2 (XZ plane): direction in XZ plane
        dir2 = np.array([math.cos(doa2_rad), 0, math.sin(doa2_rad)])
        
        # Array 3 (YZ plane): direction in YZ plane
        dir3 = np.array([0, math.cos(doa3_rad), math.sin(doa3_rad)])
        
        # Solve for intersection point using least squares
        # Each ray: P = array_center + t * direction
        # We want to find P that minimizes distance to all three rays
        
        try:
            # Set up system of equations
            # For 3D intersection, we solve: A * P = b
            A = []
            b = []
            
            # For each ray, add constraint equations
            for center, direction in [(self.array1_center, dir1), 
                                    (self.array2_center, dir2), 
                                    (self.array3_center, dir3)]:
                
                # Constraint: (P - center) perpendicular to direction = 0
                # This gives us: direction^T * (P - center) = 0
                # But we want the point closest to the ray, so we use:
                # (I - direction*direction^T) * (P - center) = 0
                
                identity_matrix = np.eye(3)
                proj_matrix = identity_matrix - np.outer(direction, direction)
                
                A.append(proj_matrix)
                b.append(np.dot(proj_matrix, center))
            
            # Stack all equations
            A_stacked = np.vstack(A)
            b_stacked = np.hstack(b)
            
            # Solve least squares
            try:
                solution, residuals, rank, s = np.linalg.lstsq(A_stacked, b_stacked, rcond=None)
            except TypeError:
                # Fallback for older numpy versions
                solution, residuals, rank, s = np.linalg.lstsq(A_stacked, b_stacked)
            
            # Calculate confidence (lower residual = higher confidence)
            confidence = math.sqrt(residuals[0]) if residuals.size > 0 else 0.0
            
            return solution, confidence
            
        except Exception as e:
            print("Error in triangulation: {}".format(e))
            return np.array([0, 0, 0]), float('inf')
    
    def triangulate_geometric(self, doa1_xy, doa2_xz, doa3_yz):
        """
        Alternative geometric triangulation method
        More intuitive but less robust than least squares
        """
        
        doa1_rad = math.radians(doa1_xy)
        doa2_rad = math.radians(doa2_xz)
        doa3_rad = math.radians(doa3_yz)
        
        try:
            # From Array 1 (XY plane): we get the direction in XY
            # x/y = cos(doa1)/sin(doa1) = cot(doa1)
            # So: y = x * tan(doa1)
            
            # From Array 2 (XZ plane): we get the direction in XZ  
            # x/z = cos(doa2)/sin(doa2) = cot(doa2)
            # So: z = x * tan(doa2)
            
            # From Array 3 (YZ plane): we get the direction in YZ
            # y/z = cos(doa3)/sin(doa3) = cot(doa3)  
            # So: z = y * tan(doa3)
            
            # Solving the system:
            # y = x * tan(doa1)
            # z = x * tan(doa2)  
            # z = y * tan(doa3)
            
            # Substituting: x * tan(doa2) = (x * tan(doa1)) * tan(doa3)
            # This gives us a consistency check
            
            # For a unit distance solution, we can set:
            if abs(math.cos(doa1_rad)) > 1e-6:
                x = 1.0
                y = x * math.tan(doa1_rad)
                z = x * math.tan(doa2_rad)
                
                # Verify consistency with third constraint
                expected_z = y * math.tan(doa3_rad) if abs(math.cos(doa3_rad)) > 1e-6 else z
                error = abs(z - expected_z)
                
                return np.array([x, y, z]), error
            else:
                return np.array([0, 1, math.tan(doa3_rad)]), 0.0
                
        except Exception as e:
            print("Error in geometric triangulation: {}".format(e))
            return np.array([0, 0, 0]), float('inf')

def main():
    # Initialize the 3D localization system
    localizer = ThreeArrayLocalization3D(array_distance=1.0)
    
    # Find USB devices (assuming you have 3 arrays, each represented by one device)
    devices = usb.core.find(find_all=True, idVendor=0x2886, idProduct=0x0018)
    devices_list = list(devices)
    
    print("Found \033[92m{} devices\033[0m".format(len(devices_list)))
    print("3D Localization with 3 Orthogonal Arrays")
    print("Array 1 (XY plane) - Device 0")
    print("Array 2 (XZ plane) - Device 1") 
    print("Array 3 (YZ plane) - Device 2")
    print()
    
    if len(devices_list) < 3:
        print("Error: Need exactly 3 microphone arrays for orthogonal 3D localization")
        print("Each array should provide one DOA reading")
        return
    
    try:
        while True:
            # Get DOA from each array
            try:
                # Array 1: XY plane (horizontal)
                array1_tuning = Tuning(devices_list[0])
                doa1_xy = array1_tuning.direction  # DOA in XY plane
                
                # Array 2: XZ plane (vertical, front-facing)
                array2_tuning = Tuning(devices_list[1]) 
                doa2_xz = array2_tuning.direction  # DOA in XZ plane
                
                # Array 3: YZ plane (vertical, side-facing)
                array3_tuning = Tuning(devices_list[2])
                doa3_yz = array3_tuning.direction  # DOA in YZ plane
                
                # Perform 3D triangulation using least squares method
                position_ls, confidence_ls = localizer.triangulate_from_three_arrays(
                    doa1_xy, doa2_xz, doa3_yz
                )
                
                # Also try geometric method for comparison
                position_geom, error_geom = localizer.triangulate_geometric(
                    doa1_xy, doa2_xz, doa3_yz
                )
                
                # Display results
                sys.stdout.write(
                    "DOA: XY={:.1f}° XZ={:.1f}° YZ={:.1f}° | "
                    "3D_LS: ({:.2f},{:.2f},{:.2f}) conf={:.3f} | "
                    "3D_Geom: ({:.2f},{:.2f},{:.2f}) err={:.3f}\n".format(
                        doa1_xy, doa2_xz, doa3_yz,
                        position_ls[0], position_ls[1], position_ls[2], confidence_ls,
                        position_geom[0], position_geom[1], position_geom[2], error_geom
                    )
                )
                sys.stdout.flush()
                
            except Exception as e:
                print("Error reading from arrays: {}".format(e))
                
            time.sleep(0.1)  # Small delay
            
    except KeyboardInterrupt:
        print("\nExiting 3D localization...")

if __name__ == "__main__":
    main()
