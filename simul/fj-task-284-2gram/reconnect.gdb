set pagination off
tui enable
target remote :1234
break CC_EXIT
continue
info threads
break ep.c:38
continue
info threads
quit
