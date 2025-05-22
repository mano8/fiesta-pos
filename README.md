# 🎉 Fiesta POS: Reutilización de un Terminal NCR RealPOS 20 para Eventos Comunitarios

## 📝 Descripción del Proyecto

Una asociación de vecinos dispone de un terminal `NCR RealPOS 20` y una impresora de tickets `Posiflex PP6800`. El objetivo es reutilizar este hardware para gestionar la venta de tapas y bebidas durante eventos periódicos, implementando un sistema de punto de venta (TPV) económico, fiable y fácil de usar.

---

## 🧰 Hardware Disponible

### 🖥️ Terminal TPV NCR RealPOS 20

- **Sistema Operativo Original**: Windows 7
- **Procesador**: [Intel Celeron M 320](https://www.cpu-upgrade.com/CPUs/Intel/Celeron_M/320_(Socket_479).html)
- **Memoria RAM**: 2 GB DDR1 PC320
- **Almacenamiento**: Disco duro de 75 GB
- **Pantalla Táctil**: Conectada mediante 4 cables directamente a la placa base utilizando el protocolo serial RS-232
- **Controlador Táctil**: Fabricado por Elo Touch Technologies, con drivers disponibles para sistemas operativos de 32 bits, incluyendo Linux

> ℹ️ **Nota**: La conexión RS-232 de la pantalla táctil no es común en equipos modernos, lo que dificulta su uso con otros PC sin adaptadores específicos.

### 🖨️ Impresora de Tickets Posiflex PP6800

- **Interfaz**: USB/Serial
- **Problemas Detectados en Windows 7**:
  - El controlador no es completamente estable
  - No detecta cambios de puerto al conectarse a diferentes puertos USB
  - No es reconocida como impresora estándar por Windows
  - Frecuentes fallos en su funcionamiento
- **Compatibilidad con Linux**: No se han encontrado drivers oficiales disponibles

### 💵 Caja Registradora

- **Conexión**: Se conecta a la impresora mediante un conector RJ-12

---

## 🎯 Requisitos del Sistema

- 💰 **Económico**: Aprovechar el hardware existente para minimizar costos
- 🧠 **Fácil de Usar**: Interfaz sencilla para los usuarios
- 🔒 **Fiable**: Funcionamiento estable durante los eventos
- 🧾 **Impresión Flexible**: Capacidad para imprimir tickets globales y por artículo
- 📊 **Contabilidad Básica**: Registro y seguimiento de ventas

---

## ⚠️ Desafíos Identificados

- **Sistema Operativo Obsoleto**: Windows 7 ha sido descontinuado y no recibe soporte oficial
- **Hardware Antiguo**: El terminal y sus componentes tienen casi 20 años
- **Procesador sin PAE**: La mayoría de los sistemas operativos modernos requieren soporte PAE, que este procesador no ofrece
- **Memoria RAM Limitada**: 2 GB de RAM DDR1 es insuficiente para muchas aplicaciones actuales
- **Conectividad de la Pantalla Táctil**: La conexión RS-232 dificulta su uso con otros sistemas sin adaptadores específicos

---

## 🐧 Solución: Bodhi Linux Legacy

Dado que la mayoría de los sistemas operativos actuales no son compatibles con CPUs sin PAE, se optó por **Bodhi Linux Legacy**, una distribución ligera compatible con arquitecturas de 32 bits y sin PAE.

- **Ventajas**:
  - Ligero y adecuado para hardware antiguo
  - Compatible con CPUs sin PAE
  - Drivers disponibles para la pantalla táctil en sistemas Linux de 32 bits

> ⚙️ **Nota Técnica**: Por defecto, Bodhi Linux solo habilita cuatro puertos UART (`ttyS0` a `ttyS3`). Sin embargo, en Windows 7, la pantalla táctil utiliza el puerto COM5, que corresponde a `ttyS4` en Linux. Para habilitar este puerto adicional, es necesario modificar la configuración del kernel a través de GRUB durante el arranque.

Para una guía detallada sobre la instalación manual del driver EloSerial en Bodhi Linux, consulta [este el documento](https://github.com/mano8/fiesta-pos/blob/1c8800351c1dac261c852ef76b5954c7dfa22c82/NCR_RealPos20/README.md).

---

## 🌐 Configuración del Navegador

El navegador preinstalado en Bodhi Linux puede presentar problemas de compatibilidad. Por ello, se instala **Mozilla Firefox** como navegador predeterminado.

Un script de inicio se encarga de abrir Firefox en modo de pantalla completa, accediendo directamente a la aplicación TPV de Odoo alojada en el servidor.

---

## 🖥️ Servidor TPV con Odoo Community Edition

Se utiliza **Odoo Community Edition** como solución TPV moderna, de código abierto y adaptable, que cumple con todos los requisitos establecidos.

- **Requisitos del Sistema para Uso Intensivo**:
  - **Procesador**: Mínimo de 2 núcleos
  - **RAM**: Mínimo de 4 GB
  - **Almacenamiento**: Entre 50 y 100 GB en SSD
  - **Base de Datos**: PostgreSQL

> 📡 **Recomendación**: Para mitigar posibles fallos del terminal, se sugiere que el servidor sea accesible vía Wi-Fi, permitiendo el uso de dispositivos móviles como alternativa al terminal NCR.

---

## 📄 Documentación Adicional

- [Instalacion de drivers Elo Touch](https://github.com/mano8/fiesta-pos/blob/1c8800351c1dac261c852ef76b5954c7dfa22c82/NCR_RealPos20/README.md): Instrucciones detalladas para la instalación del driver de la pantalla táctil Elo en Bodhi Linux.

- [Instalacion del servidor Odoo](https://github.com/mano8/fiesta-pos/blob/c7f27d4463e575e7b4b7a6d805755289f3e0710d/ODOO_SERVER.md): Instrucciones detalladas para la instalación del servidor Odoo.
---

## 🧑‍💻 Contribuciones

¡Las contribuciones son bienvenidas! Si deseas mejorar este proyecto, por favor, realiza un fork del repositorio y envía tus pull requests.

---

## 📜 Licencia

Este proyecto está licenciado bajo la [Licencia Apache 2](LICENSE).

