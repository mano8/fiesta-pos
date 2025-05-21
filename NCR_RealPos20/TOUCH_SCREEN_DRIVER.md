# Install touch screen driver

The NCR RealPOS 7443’s resistive touchscreen is driven by Elo’s AccuTouch® CTR-2210 controller. While Elo also offers variants like CTR-2216 and CTR-2218 for different five-wire resistive technologies, the original 7443 employs the CTR-2210 module for its 4-wire AccuTouch® panel.

## Install driver

### 1. Install required libmotif

```bash
sudo apt update
sudo apt upgrade
sudo apt install libinput-tools
# install required  libmotif
sudo apt install libxm4 libuil4 libmrm4 libmotif-common libusb-1.0-0 build-essential
sudo modprobe uinput
```

### 2. Download and extract files

```bash
wget https://assets.ctfassets.net/of6pv6scuh5x/2IBLPYeET8UWF1ypYIepFb/2f6907f3cd8f83aad4da5eef0d386605/SW603106_Elo_Linux_Serial_Driver_v3.7.2_i686.tgz
tar xf ~/Downloads/SW603106_Elo_Linux_Serial_Driver_v3.7.2_i686.tgz
```

### 3. Copy the driver files to /etc/opt/elo-ser folder location

```bash
sudo cp -r ~/Downloads/bin-serial/  /etc/opt/elo-ser
```

### 3. Set full permissions for all the users

```bash
cd /etc/opt/elo-ser
sudo chmod -R 777 *
sudo chmod -R 444 *.txt
```

### 4. Check for active systemd init process

```bash
sudo ps -eaf | grep [s]ystemd
sudo ps -eaf | grep init
sudo ls -l /sbin/init
```

If systemd init system is active, copy and enable the elo.service systemd
script to load the elo driver at startup. Proceed to Step IV of the installation.

```bash
sudo cp /etc/opt/elo-ser/eloser.service /etc/systemd/system/
sudo systemctl enable eloser.service
sudo systemctl status eloser.service
```

### 5. Set correct port name in eloser config

Because Windows shows your Elo controller on COM5 but Linux only exposes ttyS0–ttyS3 (COM1–COM4), your serial port isn’t being created by the kernel.
Linux’s default 8250 UART driver only registers four UARTs. To get a /dev/ttyS4 (COM5) you must explicitly tell the kernel to expose more ports by setting the 8250.nr_uarts parameter to at least 5.

#### On boot

Because the `8250 PCI` serial driver is built into the kernel, you cannot change its `nr_uarts` setting at runtime via `modprobe`; you must pass the `8250.nr_uarts=5` (or equivalently `8250_core.nr_uarts=5`) as a kernel boot parameter so that at startup the driver allocates `/dev/ttyS0–ttyS4`. Below are the precise steps to do this on Bodhi Linux (Ubuntu-based), after which `/dev/ttyS4` (`COM5`) will exist, allowing your `Elo CTR-2500S` serial touchscreen to function under Linux without needing a `USB-to-RS-232` adapter.

> Edit `/etc/default/grub`
> Append `8250.nr_uarts=5` to the `GRUB_CMDLINE_LINUX_DEFAULT` line.

```bash
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/&8250.nr_uarts=5 /' /etc/default/grub
```

Update GRUB’s config and reboot

```bash
sudo update-grub
sudo reboot
```

Verify that /dev/ttyS4 now exists:

```bash
ls -l /dev/ttyS{0..4}
```

#### Set correct port to `eloser` config

```bash
sudo sed -i -E 's|(/etc/opt/elo-ser/eloser).*$|\1 --handshake --stdigitizer ttyS4|' /etc/opt/elo-ser/loadEloSerial.sh
# or manually
sudo nano /etc/opt/elo-ser/loadEloSerial.sh
# Example (set 'ttyS4'):
# /etc/opt/elo-ser/eloser ttyS4
```

### 5. Install a script to invoke Elo drivers at system startup.

Find `rc.local` :

```bash
sudo find /etc -name rc.local
> /etc/bodhibuilder/isofiles/rc.local
# For X essential commands, put them into iso_boot_script.sh
sudo nano /etc/bodhibuilder/isofiles/iso_boot_script.sh
```

Add the following two lines at the end of daemon configuration script

```bash
/etc/opt/elo-ser/setup/loadelo
/etc/opt/elo-ser/eloser --handshake --stdigitizer ttyS4
```

### 6. Reboot the system to complete the driver installation process

```bash
sudo reboot now
```

## List devices

```bash
sudo libinput list-devices | grep -A4 -i touch
```

with eloser tools

```bash
DISPLAY=:0 /etc/opt/elo-ser/elova ---viewdevices
```

Ensure elo-ser is present 

```bash
ls -l /dev/elo-ser
```

## Calibrate touch screen

In screen apears calibration targets to tap for calibrating.
Repeat operation to ensure at most 3 calibration points are set.

> From SSH

```bash
DISPLAY=:0 sudo ./elovaLite --nvram
```

> From Host Machine

```bash
sudo ./elovaLite --nvram
```

## Extra Tips

### Reload elo deamon

Reload elo demon without reboot

```bash
# 1. Stop any running Elo serial daemon
sudo systemctl stop eloser.service
sudo pkill eloser

# 3. Start & enable the systemd service
sudo systemctl daemon-reload
sudo systemctl enable eloser.service
sudo systemctl start eloser.service

# 4. Restart the display manager so X sees the new input device
sudo systemctl restart lightdm   # or gdm, sddm, etc.

# 5. Verify the touchscreen appears
libinput list-devices | grep -A4 -i touch
```

### Other ways to Set correct port name in eloser config

> **Not possible here**

#### Direct (if work)

Check current UART count:

```bash
sysctl dev.serial.nr_uarts
```

> If not set, the default is 4.

Increase `nr_uarts` on-the-fly:

```bash
sudo sh -c 'echo 5 > /sys/module/8250_pci/parameters/nr_uarts'
```

This tells the `8250_pci` driver to create five UART lines `(ttyS0–ttyS4)` without rebooting.

Verify the new device appears:

```bash
ls /dev/ttyS[0-4]
```

You should now see `/dev/ttyS4`.

#### With modeprobe

Pass the parameter directly to the 8250_pci module instead of via sysctl.

Unload the PCI UART driver:

```bash
sudo modprobe -r 8250_pci
```

Reload it with 5 UARTs:

```bash
sudo modprobe 8250_pci nr_uarts=5
```

Verify that /dev/ttyS4 now exists:

```bash
ls -l /dev/ttyS{0..4}
```
