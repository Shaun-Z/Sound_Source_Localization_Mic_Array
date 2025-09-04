# 3 Microphone Arrays - Orthogonal Setup Guide

## Your Configuration: 3 Arrays on Orthogonal Planes

Since you already have 3 microphone arrays that can provide DOA readings, here's how to set them up for 3D localization:

### Physical Arrangement

```
Array 1 (XY Plane - Horizontal):
- Position: Horizontal plane, facing up
- Provides: Azimuth angle in horizontal plane (0° = +X direction)
- Measures: Left/Right and Front/Back direction of sound

Array 2 (XZ Plane - Vertical Front):  
- Position: Vertical plane, facing forward
- Provides: Elevation angle in front-facing plane (0° = +X direction)
- Measures: Front/Back and Up/Down direction of sound

Array 3 (YZ Plane - Vertical Side):
- Position: Vertical plane, facing sideways  
- Provides: Elevation angle in side-facing plane (0° = +Y direction)
- Measures: Left/Right and Up/Down direction of sound
```

### Coordinate System
```
       Z (Up)
       |
       |
       +------- Y (Right)
      /
     /
    X (Forward)
```

### Physical Setup Steps

1. **Array 1 (Horizontal)**: 
   - Place flat on table/surface
   - Microphones point upward
   - 0° should point toward your "forward" direction (+X)

2. **Array 2 (Vertical Front)**:
   - Mount vertically facing forward
   - Can be on a stand or wall mount
   - 0° should point forward (+X), 90° points up (+Z)

3. **Array 3 (Vertical Side)**:
   - Mount vertically facing sideways
   - Perpendicular to Array 2
   - 0° should point right (+Y), 90° points up (+Z)

### Software Usage

```bash
# Run the 3-array orthogonal localization
python location_3arrays_orthogonal.py
```

### Understanding the Output

The script will show:
- **DOA angles**: XY=angle1° XZ=angle2° YZ=angle3°
- **3D Position**: (x, y, z) coordinates of sound source
- **Confidence**: Lower values = more accurate positioning

### Example Output
```
DOA: XY=45.0° XZ=30.0° YZ=60.0° | 3D_LS: (1.00,1.00,0.58) conf=0.023 | 3D_Geom: (1.00,1.00,0.58) err=0.001
```

This means:
- Sound is 45° from +X in horizontal plane (northeast direction)
- Sound is 30° elevation in front-facing plane
- Sound is 60° from +Y in side-facing plane
- Calculated 3D position: slightly forward, right, and up

### Calibration Tips

1. **Test with Known Source**: Place speaker at known location, verify calculated position
2. **Adjust Array Orientation**: Fine-tune physical positioning for best accuracy
3. **Check Consistency**: Both methods (LS and Geom) should give similar results
4. **Distance Scaling**: The output gives relative position - scale by your array spacing

### Troubleshooting

- **High Confidence Values**: Arrays may not be properly orthogonal
- **Inconsistent Results**: Check USB connections and array orientations  
- **Zero Coordinates**: One or more arrays may not be detecting sound
- **Geometric vs LS Differences**: Normal small differences, large differences indicate setup issues
