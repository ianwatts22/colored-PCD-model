# colored-PCD-model

First off, s/o ChatGPT Code Interpreter for doing most of this code. Was an honor working with you. 

This library is for creating a colored, evenly-spaced-grid 3D point cloud (.pcd) from a point cloud (.pcd) and top-down image of a model.

Created for use case of Google Earth derived 3D assets, which didn't provide the desired result as they were tile-y and unevenly dotted..

3D geometry PCD files need to be ASCII (usually come in binary), output file will be in ASCII

- [How to convert PCD between binary and ASCII](https://chat.openai.com/share/a913515b-7a02-4dc9-9915-40e3aeeae443)

PCD files need to be Y up.
Adjust `grid_width` to adjust resolution
Adjust `y_multiple` to adjust the mutliplier on y-values, to make topography more or less drastic.
Writes output files to `assets/writing` in format of `PCD_full_{grid width}_{y multiple}`.

Right now only supports grids made up of squares, though working on an equilateral triangle grid.