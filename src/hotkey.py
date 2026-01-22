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
typeEventHotKeyID = 1751869796 # 'hkid'
kEventParamDirectObject = 757935405 # '----'

# Types
EventHotKeyID = struct.Struct('II') # signature (UInt32), id (UInt32)
EventTargetRef = ctypes.c_void_p
EventHotKeyRef = ctypes.c_void_p
EventHandlerRef = ctypes.c_void_p
EventTypeSpec = struct.Struct('II') # eventClass (UInt32), eventKind (UInt32)
OSStatus = ctypes.c_int32
EventRef = ctypes.c_void_p

# Function Signatures

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

# RegisterEventHotKey
carbon.RegisterEventHotKey.argtypes = [
    ctypes.c_uint32, 
    ctypes.c_uint32, 
    HotKeyID_Struct, 
    EventTargetRef, 
    ctypes.c_uint32, 
    ctypes.POINTER(EventHotKeyRef)
]
carbon.RegisterEventHotKey.restype = OSStatus

# GetEventParameter
carbon.GetEventParameter.argtypes = [
    EventRef,
    ctypes.c_uint32, # name
    ctypes.c_uint32, # type
    ctypes.c_void_p, # outType
    ctypes.c_uint32, # inBufferSize
    ctypes.c_void_p, # outBufferSize
    ctypes.c_void_p  # outBuffer
]
carbon.GetEventParameter.restype = OSStatus

class EventTypeSpec_Struct(ctypes.Structure):
    _fields_ = [("eventClass", ctypes.c_uint32), ("eventKind", ctypes.c_uint32)]


class HotKeyManager:
    def __init__(self):
        self.callbacks = {} # id -> callback
        self.hot_key_refs = []
        self.handler_ref = ctypes.c_void_p()
        self._c_handler = None # Keep alive
        self.signature = struct.unpack(">i", b"HKEY")[0]

    def register_hotkey(self, key_code, modifiers, callback, hk_id_val):
        # 1. Store Callback
        self.callbacks[hk_id_val] = callback

        # 2. Get Target
        target = carbon.GetApplicationEventTarget()
        if not target:
            print("Zero: Failed to get Application Event Target")
            return
            
        # 3. Register Hotkey
        hk_id = HotKeyID_Struct()
        hk_id.signature = self.signature
        hk_id.id = hk_id_val
        
        ref = ctypes.c_void_p()
        
        status = carbon.RegisterEventHotKey(
            key_code,
            modifiers,
            hk_id,
            target,
            0,
            ctypes.byref(ref)
        )
        
        if status != 0:
            print(f"Zero: RegisterEventHotKey failed with status {status}")
            return
            
        self.hot_key_refs.append(ref)

        # 4. Install Handler (only once)
        if not self._c_handler:
            self._install_handler(target)

    def _install_handler(self, target):
        def handler_func(next_handler, event, user_data):
            try:
                hk_id = HotKeyID_Struct()
                
                status = carbon.GetEventParameter(
                    event,
                    kEventParamDirectObject,
                    typeEventHotKeyID,
                    None,
                    ctypes.sizeof(hk_id),
                    None,
                    ctypes.byref(hk_id)
                )

                if status == 0:
                    if hk_id.id in self.callbacks:
                        self.callbacks[hk_id.id]()
                    else:
                        print(f"Zero: Unknown hotkey ID {hk_id.id}")
                else:
                    print(f"Zero: GetEventParameter failed {status}")

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

