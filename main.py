#!/usr/bin/env python3
import asyncio
import sys

# Fix для Python 3.14 на Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from planner_bot import main

if __name__ == '__main__':
    main()