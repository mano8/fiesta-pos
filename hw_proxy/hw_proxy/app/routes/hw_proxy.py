"""
Api routes for hw_proxy module
"""
import asyncio
import base64
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from escpos.printer import Dummy
from hw_proxy.pos_helper import EscPosHelper
from hw_proxy.hw_proxy.core.schemas import PrintRequest


router = APIRouter(prefix="/hw_proxy", tags=["hw_proxy"])

IOT_BOX_SECRET = None
PRINTER_KEY = "PP6800"
# --- Constantes ESC/POS legibles ---
CMD_CUT = b"\x1D\x56\x01"        # Corte completo
CMD_CASHDRAWER = b"\x1B\x70\x00\x19\xFA"  # Apertura de cajón


# --- Security Dependency ---
# , dependencies=[Depends(verify_secret)]
async def verify_secret(x_iot_box_secret: str = Header(..., alias="X-IOT-BOX-SECRET")):
    if x_iot_box_secret != IOT_BOX_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden: invalid IoT Box secret")
    return True


@router.get("/hello")
async def hello():
    """Emulates IoT Box hello endpoint"""
    return {"result": "hello", "version": "1.0"}


@router.post("/handshake")
async def handshake(body: dict):
    """Emula el handshake JSON-RPC del IoT Box"""
    req_id = body.get("id")
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "supports": {
                "print": True,
                "cut": True,
                "cashdrawer": True
            },
            "version": "1.0"
        }
    }

@router.post("/customer_facing_display")
async def customer_facing_display(req: Request):
    body = await req.json()
    req_id = body.get("id")
    params = body.get("params", {})
    # Fake action: log or process display data
    print("[DISPLAY]", params)
    return {"jsonrpc": "2.0", "id": req_id, "result": {"success": True}}


@router.post("/status_json")
async def status_json(req: Request):
    body = await req.json()
    req_id = body.get("id")
    
    def _query_status():
        try:
            pos = EscPosHelper(PRINTER_KEY)
            printer = pos.get_printer()
            is_online = printer.is_online()
            paper_status_code = printer.paper_status()
            paper_status_map = {
                2: "ok",
                1: "near_end",
                0: "no_paper"
            }
            paper_status = paper_status_map.get(paper_status_code, "unknown")
            return {
                "is_online": is_online,
                "paper_status": paper_status
            }
        except Exception as e:
            return {
                "is_online": False,
                "paper_status": "unknown",
                "error": str(e)
            }
    status = await asyncio.to_thread(_query_status)
    return JSONResponse({"jsonrpc": "2.0", "id": req_id, "params": status})


@router.post("/default_printer_action")
async def default_printer_action(req: Request):
    """Handle generic default_printer_action calls from Odoo POS"""
    print("Get data...")
    body = await req.json()
    req_id = body.get("id")
    params = body.get("params", {})
    data = params.get("data", {})
    action = data.get("action")
    receipt = data.get("receipt")
    def _job():
        pos = EscPosHelper(PRINTER_KEY)
        printer = pos.get_printer()
        # Choose action
        if action == "print_receipt":
            if receipt is not None:
                print("Convert to Image...")
                img = pos.format_base64_to_image(receipt)
                d = Dummy()
                # debug_save_image(img)
                #eimg = EscposImage(img_source=f"/tmp/ticket.png")
                #raster = eimg.to_raster_format()
                d.image(img, impl="bitImageColumn")
                d.cut(feed=True)
                printer._raw(d.output)
                print("Ticket imprimido...")
        elif action == "cut":
            printer._raw(CMD_CUT)
        elif action in ("cashbox", "cashdrawer"):  # Odoo may use 'cashbox'
            printer._raw(CMD_CASHDRAWER)
        else:
            # unknown action, ignore or log
            print(f"[WARNING] Unknown default_printer_action: {action}")
        printer.close()
    # asyncio.create_task(asyncio.to_thread(_job))
    print("Start job...")
    _job()
    return {"jsonrpc": "2.0", "id": req_id, "result": {"success": True}}


@router.post("/print")
async def print_ticket(req: PrintRequest):
    """Print a ticket with optional cut and cashdrawer."""
    try:
        data_bytes = base64.b64decode(req.data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 data: {e}")

    async def _job():
        pos = EscPosHelper(PRINTER_KEY)
        printer = pos.get_printer()
        await asyncio.to_thread(printer._raw, data_bytes)
        if req.cut:
            await asyncio.to_thread(printer._raw, CMD_CUT)
        if req.cashdrawer:
            await asyncio.to_thread(printer._raw, CMD_CASHDRAWER)

    asyncio.create_task(_job())
    return {"success": True}

@router.post("/open_cashdrawer")
async def open_cashdrawer(printer_name: str):
    """Open cash drawer without printing."""
    async def _job():
        pos = EscPosHelper(PRINTER_KEY)
        printer = pos.get_printer()
        await asyncio.to_thread(printer._raw, CMD_CASHDRAWER)
    asyncio.create_task(_job())
    return {"success": True}

@router.post("/cut")
async def cut_paper(printer_name: str):
    """Cut paper without printing."""
    async def _job():
        pos = EscPosHelper(PRINTER_KEY)
        printer = pos.get_printer()
        await asyncio.to_thread(printer._raw, CMD_CUT)
    asyncio.create_task(_job())
    return {"success": True}
