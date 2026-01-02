# Apple Glass Effect Using Pygame

> 2025 by rgzz666

This is an experiment to implement Apple's new liquid glass effect, using the pygame module as a graphical interface of showing the final outcome.

Currently, only rectangles and rounded corner rectangles are supported, as the way of handling other shapes are beyond my ability.

Please always note that I am never a CG expert, but an ordinary grade 10 student.

**Contributions are always welcomed!** Please always make changes and open pull requests when you have new ideas.

## Known Issue(s)

It is already known that the algorithm of the deflection offset is not fully correct (due to errors while calculations and derivation). One of the most efficient solutions is to use a simpler function to express the offset, and simulate the effect without considering any other physical facts. Just for confirmation, a comparison will be carried out between the two methods to see if they really look similar.

Also, beyond the basic blur and deflection effect, the edge diffusion effect is not completed until now. It will be completed once the project is decided to be continued. 

## Is The Project Discontinued?

**It was, but not anymore.** I am now back to this project. Instead, the `totowang-hhh/AppleGlassEffectWeb` will be given up.