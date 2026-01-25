# Apple Glass Effect Using Pygame

> 2025 by rgzz666

This is an experiment to implement Apple's new liquid glass effect, using the pygame module as a graphical interface of showing the final outcome.

Currently, only rectangles and rounded corner rectangles are supported, as the way of handling other shapes are beyond my ability.

Please always note that I am never a CG expert, but an ordinary grade 10 student.

**Contributions are always welcomed!** Please always make changes and open pull requests when you have new ideas.

## Known Issue(s)

### ~~Deflection Simulating Method~~

It is already known that the algorithm of the deflection offset is not fully correct (due to errors while calculations and derivation). One of the most efficient solutions is to use a simpler function to express the offset, and simulate the effect without considering any other physical facts. Just for confirmation, a comparison will be carried out between the two methods to see if they really look similar.

Until 2026-01-25, this problem has been solved by rewriting the deflection rendering part using a solution completely without Physics, since the older method was buggy and slow.

### Edge Diffusion

The edge diffusion effect is not completed until now.

This will be marked as non-planned as it is not that relevant to producing a similar effect with original Liquid Glass. Simulating the deflection effect is very enough. ~~While the most important reason is that, as my academic project, my deadline of a working version is near. :(~~

The edge diffusion effect may still have some improvements on the final outcome if it was implemented, so it **may** be planned in future versions (will not be included in the academic project).