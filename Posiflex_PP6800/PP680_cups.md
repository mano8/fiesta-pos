# Install Posiflex PP6800 printer

## Install Cups

### Start cups

```bash
sudo systemctl enable cups
sudo systemctl start cups
```

Cups is now accessible at [http://localhost:631](http://localhost:631)

### Cups troubleshooting

- Confirm the serial backend is executable:

  ```bash
  ls -l /usr/lib/cups/backend/serial
  ```

- Increase CUPS logging:

  ```bash
  sudo cupsctl --debug-logging
  ```

## Install printer

### Get printer port

List available devices

```bash
lpinfo -v
# Or to view Specific posiflex
lpinfo -v | grep -i posiflex
```

### Add printer to Cups 

#### Using raw driver (no filtering)

**Warning**: Using raw Driver is Deprecated.

```bash
sudo lpadmin -p PP6800 -E -v serial:/dev/ttyACM0?baud=115200,parity=N,8,1 -m raw
sudo cupsenable PP6800
sudo cupsaccept PP6800
```

> - `-m raw` tells CUPS to send data unchanged (ESC/POS commands intact).
> - The URI `serial:/dev/ttyACM0?baud=115200` uses the CUPS serial backend.

#### Using compiled Driver

> **Warning**:
> Printer drivers are deprecated and will stop working in a future version of CUPS.

Use `cups_thermo_printer` package to compile and install driver.

> See [README.md](https://github.com/mano8/fiesta-pos/blob/bbe7f31ef24fa0c327741b732e6fb61711b04518/cups-thermo-printer/README.md) file for procedure.

When driver compiled and installed, we can add printer

```bash
# Remove existant PP6800
sudo lpadmin -x PP6800
# add new PP6800
sudo lpadmin -p PP6800 -E -v serial:/dev/ttyACM0?baud=115200,parity=N,8,1 -m pp6800.ppd
sudo cupsenable PP6800
sudo cupsaccept PP6800
```

**Optional**: Set PP6800 as the default printer

```bash
sudo lpoptions -d PP6800
```

### Set Serial config

- To work printer must have correct serial parameters.

  ```bash
  sudo stty -F /dev/ttyACM0 115200 cs8 -cstopb -parenb -crtscts -echo
  ```

- Verrify with:

  ```bash
  sudo stty -F /dev/ttyACM0
  ```

- Some serial adapters default to hardware flow control, which the PP-6800 doesn’t use:

  ```bash
  sudo stty -F /dev/ttyACM0 -crtscts
  ```

## Update security rules

### Open the cupsd profile in an editor

```bash
sudo nano /etc/apparmor.d/usr.sbin.cupsd
# sudo aa-complain /usr/sbin/cupsd
```

### Find the section near the top that lists file rules, and add

Add this line if not present to ensure cups can control ttyACM ports.
This grants read/write access to that device node.

```text
  /dev/ttyACM* rw,
```

### Reload the updated profile

```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.cupsd
```

### Restart Cups

```bash
 sudo systemctl restart cups
```

## Verify and Test

### Check AppArmor logs for denials

```bash
 sudo journalctl -k | grep apparmor | grep cups
```

### Submit a raw print again

Manual printer test

```bash
 sudo tee /dev/ttyACM0 < receipt.txt > /dev/null
```

Or

```bash
 sudo lp -d PP6800 -o raw ~/receipt.txt
```

### View latest cups Log errors

```bash
 sudo tail -n50 /var/log/cups/error_log
```

## Share printers to use PPT links

```bash
 sudo cupsctl --share-printers
```
