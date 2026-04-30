#!/usr/bin/env python3
"""
SPI Connection Test Script for Tinker Robot
Проверяет доступность и работоспособность SPI-соединения
"""

#cd hardware_task/scripts/
#pip install -r requirements.txt
#sudo python3 test_spi.py
import os
import sys
import time
import struct
import spidev  # pip install spidev

def check_spi_device(device_path="/dev/spidev0.0"):
    """Проверяет существование SPI устройства"""
    if not os.path.exists(device_path):
        print(f" SPI устройство не найдено: {device_path}")
        return False
    print(f" SPI устройство найдено: {device_path}")
    return True

def check_spi_in_use(device_path="/dev/spidev0.0"):
    """Проверяет, не используется ли SPI устройство другим процессом"""
    import fcntl
    try:
        fd = os.open(device_path, os.O_RDWR)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        return False
    except BlockingIOError:
        print(f"  SPI устройство занято другим процессом (возможно hardware_task)")
        return True

def test_spi_communication(bus=0, device=0, speed_hz=20000000):
    """Тестирует базовую SPI коммуникацию"""
    try:
        spi = spidev.SpiDev()
        spi.open(bus, device)
        spi.max_speed_hz = speed_hz
        spi.mode = 0  # SPI mode 0
        
        # Тестовые данные (простой паттерн)
        test_data = [0xAA, 0x55, 0x01, 0x02, 0x03, 0x04]
        
        print(f" Отправка тестовых данных: {[hex(x) for x in test_data]}")
        response = spi.xfer2(test_data)
        print(f" Получен ответ: {[hex(x) for x in response]}")
        
        spi.close()
        
        # Простая проверка - если все байты 0xFF или 0x00, возможно проблема
        if all(x == 0xFF for x in response) or all(x == 0x00 for x in response):
            print("  Предупреждение: получен однородный ответ, возможны проблемы с соединением")
            return False
            
        print(" SPI коммуникация работает")
        return True
        
    except Exception as e:
        print(f" Ошибка SPI коммуникации: {e}")
        return False

def main():
    print(" Проверка SPI соединения Tinker Robot")
    print("=" * 40)
    
    # Проверка наличия устройства
    if not check_spi_device():
        sys.exit(1)
    
    # Проверка прав доступа
    if os.geteuid() != 0:
        print("  Внимание: скрипт должен запускаться с правами root (sudo)")
    
    # Тест коммуникации
    print("\n Тестирование SPI коммуникации...")
    success = test_spi_communication()
    
    print("\n" + "=" * 40)
    if success:
        print(" SPI соединение работает корректно!")
    else:
        print(" Обнаружены проблемы с SPI соединением")
        print("   Проверьте:")
        print("   1. Подключение проводов SPI")
        print("   2. Наличие питания у STM32")
        print("   3. Загружена ли прошивка на STM32")
        print("   4. Правильность настроек в hardware_task")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())