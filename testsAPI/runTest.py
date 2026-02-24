#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Файл для обратной совместимости - запускает все тесты API
"""

import sys
import os

# Добавляем корневую директорию проекта в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from testsAPI.run_all_tests import run_all_tests

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)