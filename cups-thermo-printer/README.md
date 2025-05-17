# Posiflex PP6800 cups filter

This package is fork of [futurelink](https://github.com/futurelink/cups-thermo-printer) `cups-thermo-printer` package.

## Installation

------------

### Install needed libraiiries

```bash
sudo apt-get update
sudo apt-get install libcups2-dev libcupsimage2-dev
```

### For different printers

You must provide needed printer data to compile ppd in a `.drv` file, you can take example of current `.drv` files.

you can test ppd compilation with

```bash
# replace `pos` by your drv file name
ppdc pos.drv
```

### Compile all and install

To globally install pddd and filter you can use `install` script.

```bash
# ensure script is executable
sudo chmod a+x ./install

# execute
sudo ./install
```

### (Re)create CUPS queue for PP6800

Go on installing printer with CUPS at [http://localhost:631/](http://localhost:631/) or:

```bash
# Remove existant PP6800
sudo lpadmin -x PP6800
# add new PP6800
sudo lpadmin -p PP6800 -E -v serial:/dev/ttyACM0?baud=115200,parity=N,8,1 -m pp6800.ppd
sudo cupsenable PP6800
sudo cupsaccept PP6800
```

## Writing own PPD

---------------

You may write own PPD file for your printer to use any media size you want. Just open
zj.drv file with any text editor and copy-paste printer section embraced with curly brackets.
Then change your printer model and correct media sizes at the end of section.

At most all chinese thermo printers has 203DPI resolution, so you need to recalculate media sizes
into points, i.e. 229points=80mm, 164points=58mm, etc.

Also you may change resolution value for your printer and recalculate all dimensions of your media.