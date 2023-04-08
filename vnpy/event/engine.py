"""
Event-driven framework of VeighNa framework.
"""

from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from time import sleep
from typing import Any, Callable, List

# 表示eTimer类型的事件
EVENT_TIMER = "eTimer"


class Event:
    """
    Event object consists of a type string which is used
    by event engine for distributing event, and a data
    object which contains the real data.
    事件对象由事件引擎用于分发事件的类型字符串和包含真实数据的数据对象组成。
    """

    def __init__(self, type: str, data: Any = None) -> None:
        """"""
        self.type: str = type
        self.data: Any = data


# Defines handler function to be used in event engine.
# 定义要在事件引擎中使用的处理程序函数。
# callable表示一个可调用对象
# 接收Event对象返回None
HandlerType: callable = Callable[[Event], None]


class EventEngine:
    """
    Event engine distributes event object based on its type
    to those handlers registered.

    It also generates timer event by every interval seconds,
    which can be used for timing purpose.
    事件引擎根据事件对象的类型将其分发给那些注册的处理程序。它还按每间隔秒生成计时器事件，可用于计时。
    """

    def __init__(self, interval: int = 1) -> None:
        """
        Timer event is generated every 1 second by default, if
        interval not specified.
        如果未指定时间间隔，则默认情况下每隔1秒生成一次计时器事件。

        :param interval: 时间间隔， 默认为1
        """
        self._interval: int = interval  # 时间间隔， 下划线前缀'_'表示该变量是类内部使用
        self._queue: Queue = Queue()  # Queue是Python标准库中的一个线程安全队列，可以用于实现多线程间的数据传输
        self._active: bool = False  # 活动参数, 默认false
        self._thread: Thread = Thread(target=self._run)  # 用多线程执行self._run
        self._timer: Thread = Thread(target=self._run_timer)  # 用多线程执行self._run_timer
        self._handlers: defaultdict = defaultdict(list)  # 当_handlers字典中的键不存在时，会自动创建一个空列表，并将其作为默认值
        self._general_handlers: List = []  # 全体事件处理函数

    def _run(self) -> None:
        """
        Get event from queue and then process it.
        从队列中获取事件，然后进行处理。
        """
        while self._active:
            try:
                # 尝试等待事件发生, 方法是阻塞, 最多等待1秒钟, 超过抛出Empty异常
                # event变量将包含队列中的一个事件
                event: Event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event: Event) -> None:
        """
        First distribute event to those handlers registered listening
        to this type.

        Then distribute event to those general handlers which listens
        to all types.

        首先将事件分发给那些注册侦听此类型的处理程序。
        然后将事件分发给那些侦听所有类型的通用处理程序。
        """
        # 检查event对象的type属性是否在self._handlers字典中
        if event.type in self._handlers:
            [handler(event) for handler in self._handlers[event.type]]

        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def _run_timer(self) -> None:
        """
        Sleep by interval second(s) and then generate a timer event.
        按间隔秒休眠，然后生成计时器事件
        """
        while self._active:
            sleep(self._interval)
            # 创建eTimer类型的事件对象给event
            event: Event = Event(EVENT_TIMER)
            # 调用put方法加入处理队列
            self.put(event)

    def start(self) -> None:
        """
        Start event engine to process events and generate timer events.
        启动事件引擎以处理事件并生成计时器事件
        """
        self._active = True  # 启用标志
        self._thread.start()  # 开启多线程执行self._run
        self._timer.start()  # 开启多线程执行self._run_timer

    def stop(self) -> None:
        """
        Stop event engine.
        停止事件引擎
        """
        self._active = False  # 停用标志
        self._timer.join()  # join()会阻塞等待self._timer线程完成,确保在程序退出之前，所有的计时器事件都已被正确处理或停止
        self._thread.join()

    def put(self, event: Event) -> None:
        """
        Put an event object into event queue.
        将事件对象放入事件队列
        """
        self._queue.put(event)

    def register(self, type: str, handler: HandlerType) -> None:
        """
        Register a new handler function for a specific event type.
        Every function can only be registered once for each event type.

        为特定的事件类型注册一个新的处理程序函数
        对于每个事件类型，每个函数只能注册一次

        字典self._handlers数据结构：
        {
            'type':[handler1, handler2, ...],
            ...
        }
        """
        handler_list: list = self._handlers[type]  # 获取处理type类型事件的函数列表
        if handler not in handler_list:
            handler_list.append(handler)  # 添加handler处理函数(对象)

    def unregister(self, type: str, handler: HandlerType) -> None:
        """
        Unregister an existing handler function from event engine.

        从事件引擎中注销现有的处理程序函数


        """
        handler_list: list = self._handlers[type]  # 获取处理type类型事件的函数列表

        if handler in handler_list:
            handler_list.remove(handler)  # 删除handler_list列表handler类型的处理函数

        if not handler_list:
            self._handlers.pop(type)  # 删除_handlers字典的键为type的处理函数列表

    def register_general(self, handler: HandlerType) -> None:
        """
        Register a new handler function for all event types.
        Every function can only be registered once for each event type.

        从事件引擎中注销现有的处理程序函数
        对于每个事件类型，每个函数只能注册一次
        """
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)  # 添加处理函数进全体处理函数列表

    def unregister_general(self, handler: HandlerType) -> None:
        """
        Unregister an existing general handler function.

        注销现有的常规处理程序函数
        """
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)  # 删除处理函数进全体处理函数列表
