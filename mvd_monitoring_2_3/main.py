import logging
from services.mvd_monitor_service import MvdMonitorService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    monitor = MvdMonitorService()
    monitor.check_and_notify()