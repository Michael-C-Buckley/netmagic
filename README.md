# Netmagic

Network Automation Toolset.

## IOS-XR Interface Statistics

IOS-XR interface counters and configured load-interval traffic rates are available
through NETCONF, with a CLI fallback that returns the same normalized models.

```python
from netmagic.devices import CiscoIOSXRRouter
from netmagic.sessions import NETCONFSession

session = NETCONFSession(
    host="router.example.net",
    username="automation",
    password="secret",
)
router = CiscoIOSXRRouter(session)
response = router.get_interface_statistics("GigabitEthernet0/0/0/0")
statistics = response.fsm_output["GigabitEthernet0/0/0/0"]
```

Pass both a `NETCONFSession` and `TerminalSession` to prefer NETCONF automatically;
pass the terminal session to `get_interface_statistics(session=...)` to select CLI
explicitly. The reported `load_interval_seconds` identifies whether rates represent
the usual five-minute interval or another interval configured on the interface.
