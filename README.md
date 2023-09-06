# marccd  
![Build](https://github.com/Hekstra-Lab/marccd/workflows/Build/badge.svg)
[![codecov](https://codecov.io/gh/Hekstra-Lab/marccd/branch/master/graph/badge.svg)](https://codecov.io/gh/Hekstra-Lab/marccd)
[![apm](https://img.shields.io/apm/l/vim-mode.svg)](https://github.com/Hekstra-Lab/marccd/blob/master/LICENSE)


Read, write, and manipulate diffraction images that use the MarCCD format

This Python library provides:
- A `MarCCD` class for representing diffraction images and their header information
- IO methods that support reading and writing MarCCD format diffraction images

## Installation

I have not yet made this package available on PyPI. However, you can still install it with `pip`:
```
pip install git+https://github.com/Hekstra-Lab/marccd.git
```

## Quick Start

Here is a short example of reading and plotting a diffraction image:

```python
import matplotlib.pyplot as plt
from marccd import MarCCD

# Read image
mccd = MarCCD("tests/data/e074a_off1_011.mccd")

# Plot image and mark beam center
plt.imshow(mccd.image, cmap="gray_r", vmin=10, vmax=50)
plt.plot(*mccd.center, 'rx')
plt.axis("off")
```
<img src="https://github.com/Hekstra-Lab/marccd/blob/master/tests/data/image.png" width="800" class="center">
