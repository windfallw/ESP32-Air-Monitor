# This file is executed on every boot (including wake-boot from deepsleep)
import micropython
import machine
import webrepl
import esp
import gc

micropython.alloc_emergency_exception_buf(100)  # 设置紧急情况下的（栈溢出，普通RAM不足等）保险RAM分配，使在紧急情况下仍有RAM可用。
# micropython.mem_info()
machine.freq(240000000)
webrepl.start()
esp.osdebug(None)
gc.enable()

print(machine.freq())
print("flash_size: {0}, flash_user_start: {1}.".format(esp.flash_size(),esp.flash_user_start()))
