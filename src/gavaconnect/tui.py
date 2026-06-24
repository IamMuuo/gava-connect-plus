# src/gavaconnect/tui.py
from datetime import datetime
import os
import sys
from blessed import Terminal

from gavaconnect.sync_client import GavaConnectSync
from gavaconnect.exceptions import GavaConnectError

term = Terminal()


def get_credentials(service: str) -> dict:
    """Read service keys on-the-fly from the host terminal session."""
    key = os.getenv(f"KRA_{service.upper()}_KEY")
    secret = os.getenv(f"KRA_{service.upper()}_SECRET")
    if not key or not secret:
        raise ValueError(f"Missing environment variables: KRA_{service.upper()}_KEY / _SECRET")
    return {"consumer_key": key, "consumer_secret": secret}


def draw_box_menu(options: list[str], selected_index: int, env: str):
    """Render a rounded box menu layout with a highlighted selector bar."""
    print(term.clear)
    
    # Header Accent Banner
    header_text = f" GAVACONNECT CONTROLLER [{env.upper()}] "
    print(term.center(term.cyan_bold(header_text)))
    print()

    # Layout Calculations
    box_width = 56
    padding_x = (term.width - box_width) // 2
    
    # Border Elements (Rounded Box Art)
    top_border = "╭" + "─" * (box_width - 2) + "╮"
    bottom_border = "╰" + "─" * (box_width - 2) + "╯"

    # Print Top Box Boundary
    print(term.move_x(padding_x) + term.white(top_border))

    # Print Menu Lines
    for idx, opt in enumerate(options):
        # Calculate trailing spaces to keep box lines straight
        inner_space = box_width - 6 - len(opt)
        space_filler = " " * inner_space

        if idx == selected_index:
            # Active selector bar highlight row
            selector_line = f"│  {term.black_on_cyan(f' ➜ {opt} ')}{space_filler} │"
        else:
            # Standard row
            selector_line = f"│    {opt}{space_filler}   │"

        print(term.move_x(padding_x) + selector_line)

    # Print Bottom Box Boundary
    print(term.move_x(padding_x) + term.white(bottom_border))
    
    # Footer Instructions Overlay
    print("\n" + term.center(term.gray("Navigation: [↑/↓] or [k/j] • Select: [Enter] • Exit: [Ctrl+C]")))


def run_pin_check(env: str):
    """Interactive target runner for PIN Checker."""
    print(term.normal)
    try:
        creds = get_credentials("pin")
        print(term.cyan("\n📝 Enter KRA PIN to verify: "), end="", flush=True)
        pin = sys.stdin.readline().strip()
        if not pin: return

        print(term.yellow("🔄 Querying identity record layer..."))
        with GavaConnectSync(environment=env, pin=creds) as client:
            res = client.pin.check(pin)
            print(term.green_bold("\n🟢 TAXPAYER RECORD FOUND:"))
            print(f"   Name:   {res.taxpayer_name}")
            print(f"   Type:   {res.taxpayer_type}")
            print(f"   Status: {res.status_of_pin}")
    except Exception as e:
        print(term.red_bold(f"\n🔴 ERROR: {str(e)}"))


def run_station_check(env: str):
    """Interactive target runner for Tax Station Office."""
    print(term.normal)
    try:
        creds = get_credentials("station")
        print(term.cyan("\n📝 Enter KRA PIN for Tax Office lookup: "), end="", flush=True)
        pin = sys.stdin.readline().strip()
        if not pin: return

        print(term.yellow("🔄 Resolving revenue desk location map..."))
        with GavaConnectSync(environment=env, station=creds) as client:
            res = client.station.get(pin)
            print(term.green_bold("\n🟢 STATION DETAILS MATCHED:"))
            print(f"   Tax Office / Station: {res.station_name}")
    except Exception as e:
        print(term.red_bold(f"\n🔴 ERROR: {str(e)}"))


def run_invoice_check(env: str):
    """Interactive target runner for Invoice Retrieval."""
    print(term.normal)
    try:
        creds = get_credentials("invoice")
        print(term.cyan("\n📝 Enter eTIMS Invoice Number: "), end="", flush=True)
        inv_num = sys.stdin.readline().strip()
        print(term.cyan("📝 Enter Invoice Date (YYYY-MM-DD): "), end="", flush=True)
        inv_date_str = sys.stdin.readline().strip()
        
        if not inv_num or not inv_date_str: return
        inv_date = datetime.strptime(inv_date_str, "%Y-%m-%d").date()

        print(term.yellow("🔄 Auditing eTIMS repository records..."))
        with GavaConnectSync(environment=env, invoice=creds) as client:
            res = client.invoice.get(inv_num, inv_date)
            print(term.green_bold("\n🟢 INVOICE AUDIT SUCCESSFUL:"))
            print(f"   Supplier:      {res.supplier_name} ({res.supplier_pin})")
            print(f"   Total Gross:   KES {res.total_invoice_amount:,.2f}")
            print(f"   Tax Value:     KES {res.total_tax_amount:,.2f}")
            print(f"   Total Items:   {res.total_item_count}")
    except Exception as e:
        print(term.red_bold(f"\n🔴 ERROR: {str(e)}"))


def run_tui():
    """Main keyboard orchestration system featuring a dynamic item pointer wheel."""
    env = "sandbox"
    
    options = [
        "Check Taxpayer Status (PIN)",
        "Query Assigned Tax Station",
        "Check eTIMS Invoice Details",
        "Toggle Gateway Environment",
        "Exit Interface Dashboard"
    ]
    selected_index = 0

    try:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            while True:
                # Continuous layout drawing sequence
                draw_box_menu(options, selected_index, env)

                # Capture non-blocking hardware interface strokes
                key = term.inkey()

                # Handle up-navigation transitions (Arrow Up or 'k')
                if key.name == "KEY_UP" or key.lower() == "k":
                    selected_index = (selected_index - 1) % len(options)
                
                # Handle down-navigation transitions (Arrow Down or 'j')
                elif key.name == "KEY_DOWN" or key.lower() == "j":
                    selected_index = (selected_index + 1) % len(options)
                
                # Handle trigger processing confirmation inputs (Enter / Return keys)
                elif key.name == "KEY_ENTER" or key == "\n" or key == "\r":
                    if selected_index == 0:
                        run_pin_check(env)
                    elif selected_index == 1:
                        run_station_check(env)
                    elif selected_index == 2:
                        run_invoice_check(env)
                    elif selected_index == 3:
                        env = "production" if env == "sandbox" else "sandbox"
                        continue
                    elif selected_index == 4:
                        break
                    
                    print(term.gray("\nPress any key to drop back to menu board..."))
                    term.inkey()

    except KeyboardInterrupt:
        pass
    finally:
        print(term.normal + term.clear + "\n👋 Exiting safely. Goodbye!\n")


if __name__ == "__main__":
    run_tui()
