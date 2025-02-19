from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.logger import logger

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def demo_task(self):
        """示例定时任务"""
        # logger.info("定时任务执行中...")

    def start(self):
        """启动所有定时任务"""
        # 添加定时任务，每秒执行一次
        self.scheduler.add_job(
            self.demo_task, 
            'interval', 
            seconds=1,
            id='demo_task'
        )
        
        # 启动调度器
        self.scheduler.start()
        logger.info("定时任务调度器已启动")

    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        logger.info("定时任务调度器已关闭") 