import ctypes
import ctypes.util
import struct
from Cocoa import NSLog

# Load Carbon Framework
carbon_path = ctypes.util.find_library('Carbon')
carbon = ctypes.cdll.LoadLibrary(carbon_path)

# Constants
cmdKey = 256
shiftKey = 512
kEventClassKeyboard = 1801812322 # 'keyb'
kEventHotKeyPressed = 5
typeEventHotKeyID = 1751607669 # 'hkid'

# Types
EventHotKeyID = struct.Struct('II') # signature (UInt32), id (UInt32)
EventTargetRef = ctypes.c_void_p
EventHotKeyRef = ctypes.c_void_p
EventHandlerRef = ctypes.c_void_p
EventTypeSpec = struct.Struct('II') # eventClass (UInt32), eventKind (UInt32)
OSStatus = ctypes.c_int32

# Function Signatures
# RegisterEventHotKey
carbon.RegisterEventHotKey.argtypes = [
    ctypes.c_uint32, # keyCode
    ctypes.c_uint32, # modifiers
    ctypes.c_uint64, # id (struct passed by value? No, usually struct is small enough or pointer. Wait, check calling convention)
    # Actually EventHotKeyID is a struct { signature, id }. In C it is passed by value.
    # ctypes handles struct pass-by-value if we define it as a class.
    EventTargetRef,  # target
    ctypes.c_uint32, # options
    ctypes.POINTER(EventHotKeyRef) # outRef
]
carbon.RegisterEventHotKey.restype = OSStatus

# GetApplicationEventTarget
carbon.GetApplicationEventTarget.argtypes = []
carbon.GetApplicationEventTarget.restype = EventTargetRef

# EventHandlerProcPtr
EventHandlerProcPtr = ctypes.CFUNCTYPE(
    OSStatus,
    ctypes.c_void_p, # nextHandler
    ctypes.c_void_p, # theEvent
    ctypes.c_void_p  # userData
)

# InstallEventHandler
carbon.InstallEventHandler.argtypes = [
    EventTargetRef,
    EventHandlerProcPtr,
    ctypes.c_uint32, # numTypes
    ctypes.c_void_p, # typeList (pointer to specs)
    ctypes.c_void_p, # userData
    ctypes.POINTER(EventHandlerRef) # outRef
]
carbon.InstallEventHandler.restype = OSStatus

class HotKeyID_Struct(ctypes.Structure):
    _fields_ = [("signature", ctypes.c_uint32), ("id", ctypes.c_uint32)]

# Fix argtypes with correct struct
carbon.RegisterEventHotKey.argtypes = [
    ctypes.c_uint32, 
    ctypes.c_uint32, 
    HotKeyID_Struct, 
    EventTargetRef, 
    ctypes.c_uint32, 
    ctypes.POINTER(EventHotKeyRef)
]

class EventTypeSpec_Struct(ctypes.Structure):
    _fields_ = [("eventClass", ctypes.c_uint32), ("eventKind", ctypes.c_uint32)]


class HotKeyManager:
    def __init__(self, callback):
        self.callback = callback
        self.hot_key_ref = ctypes.c_void_p()
        self.handler_ref = ctypes.c_void_p()
        self._c_handler = None # Keep alive

    def register_hotkey(self):
        # 1. Get Target
        target = carbon.GetApplicationEventTarget()
        if not target:
            print("Zero: Failed to get Application Event Target")
            return
            
        # 2. Register Hotkey
        hk_id = HotKeyID_Struct()
        hk_id.signature = struct.unpack(">i", b"HKEY")[0]
        hk_id.id = 1
        
        key_code = 29 # '0'
        modifiers = cmdKey | shiftKey
        
        status = carbon.RegisterEventHotKey(
            key_code,
            modifiers,
            hk_id,
            target,
            0,
            ctypes.byref(self.hot_key_ref)
        )
        
        if status != 0:
            print(f"Zero: RegisterEventHotKey failed with status {status}")
            return
            
        # 3. Install Handler
        def handler_func(next_handler, event, user_data):
            try:
                self.callback()
            except Exception as e:
                print(f"Zero: Callback Error: {e}")
            return 0
            
        self._c_handler = EventHandlerProcPtr(handler_func)
        
        spec = EventTypeSpec_Struct()
        spec.eventClass = kEventClassKeyboard
        spec.eventKind = kEventHotKeyPressed
        
        status = carbon.InstallEventHandler(
            target,
            self._c_handler,
            1,
            ctypes.byref(spec),
            None,
            ctypes.byref(self.handler_ref)
        )
        
        if status != 0:
            print(f"Zero: InstallEventHandler failed with status {status}")

    def unregister(self):
        pass
