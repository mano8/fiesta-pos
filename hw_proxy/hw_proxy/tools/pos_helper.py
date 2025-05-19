"""
escpos helper for hw_proxy module
"""
import base64
from typing import Optional
from escpos.printer import Usb, Network, Serial, Dummy
from io import BytesIO
from PIL import Image
from hw_proxy.device_helper import DeviceHelper
from hw_proxy.core.exceptions import HwDeviceError, HwPrinterError
from hw_proxy.hw_proxy.core.schemas import DeviceConfigSchemas, NetworkDeviceSchemas, PrinteImageConfSchemas, SerialDeviceSchemas, UsbDeviceSchemas
from hw_proxy.supported_devices import DevicePortType, DeviceType, device_list

class EscPosHelper(DeviceHelper):
    """
    escpos helper for hw_proxy module
    """
    def __init__(self, device_key: str):
        DeviceHelper.__init__(self, device_key)
        self.device = self.select_device(device_key)

    def get_printer(self, printer_key: Optional[str] = None):
        """Get escpos printer object from printer configuration."""
        self.select_device(printer_key)

        if self.has_printer_conf() is False:
            raise HwDeviceError(
                "Fatal Error: Invalid device configuration. "
                "Your device must be present in supported_list items."
            )
        
        if self.device.type != DeviceType.PRINTER:
            raise HwDeviceError(
                "Fatal Error: Invalid device type. "
                "EscPosHelper is dedicated to escpos printers. "
                "Please choose a printer device."
            )

        try:
            ptype = self.device.port_type
            if ptype == DevicePortType.USB:
                return Usb(
                    self.device.vendor,
                    self.device.product,
                    in_ep=self.device.conf.in_ep,
                    out_ep=self.device.conf.out_ep
                )
            elif ptype == DevicePortType.NETWORK:
                return Network(
                    host=self.device.conf.host,
                    port=self.device.conf.port
                )
            elif ptype == DevicePortType.SERIAL:
                return Serial(
                    devfile=self.device.conf.devfile,
                    baudrate=self.device.conf.baudrate,
                    bytesize=self.device.conf.bytesize,
                    parity=self.device.conf.parity,
                    stopbits=self.device.conf.stopbits,
                    timeout=self.device.conf.timeout,
                    dsrdtr=self.device.conf.dsrdtr,
                    profile=self.device.conf.profile
                )
            else:
                raise HwPrinterError(
                    f"Unsupported printer port type: {ptype.value}"
                )
        except Exception as e:
            raise HwPrinterError(
                f"Fatal Error: Printer connection error: {e}"
            ) from e

    @staticmethod
    def set_device_port_schema(
        port_type: DevicePortType,
        config: dict
    ) -> Image:
        """Set Device Port Schema model"""
        if isinstance(config, dict):
            if port_type == DevicePortType.USB:
                return UsbDeviceSchemas(**config)
            
            if port_type == DevicePortType.NETWORK:
                return NetworkDeviceSchemas(**config)
            
            if port_type == DevicePortType.SERIAL:
                return SerialDeviceSchemas(**config)
        return None

    @staticmethod
    def format_base64_to_image(
        b64string: str
    ) -> Image:
        """
        Transform base64 string in Pillow Image object.
        1. Decodifica Base64 -> bytes
        2. Abre con Pillow -> Image
        3. printer.image() usa internamente Pillow para ESC/POS
        4. Opcional: corte y apertura de cajón
        """
        try:
            # 1. Quitar prefijos si existen y decodificar
            if "," in b64string:
                b64string = b64string.split(",", 1)[1]
            raw = base64.b64decode(b64string)

            # 2. Abrir imagen en memoria
            return Image.open(BytesIO(raw)).convert("RGB")
        except Exception as e:
            raise HwPrinterError(
                "Error: Unable to convert "
                "base64 string to Pilow Image Object. \n"
                f"error: {e}"
            ) from e
    
    @staticmethod
    def save_image(
        img: Image.Image,
        filename: str = "ticket.png"
    ) -> Image:
        """
        Guarda la imagen en el directorio actual con el nombre dado.
        El formato se deduce de la extensión (.png, .jpg, etc.).
        """
        try:
            path = f"/tmp/{filename}"
            img.save(f"/tmp/{filename}")
            print(f"[DEBUG] Imagen guardada en: {filename}")
        except Exception as e:
            raise HwPrinterError(
                "Error: Unable to save image on file. "
                "- File name: {filename} \n"
                f"error: {e}"
            ) from e