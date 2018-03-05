#### 确定串口名称

在连接和不连接串口设备时使用两次

```
 lsusb
```


找到变化的项目，并记录vendor和product，使用


```
modprobe usbserial vendor=0x067b product=0x2303
```


数值根据记录自己确定


```
dmesg | grep "ttyUSB"
```
dmesg | grep "ttyUSB"

显示的结果就是串口名称，我现在所用的串口名为/dev/ttyUSB0

#### 获取串口的权限


```
sudo chmod 777 /dev/ttyUSB0
```
