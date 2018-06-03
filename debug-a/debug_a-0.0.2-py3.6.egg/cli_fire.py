# -*- coding: utf-8 -*-

import fire

"""
宪法、生与死
===========================================================================
"""
def print_rules(explain=False):
    """rules | 打印股市交易纪律"""
    from debug_a import print_constitutions
    print_constitutions(explain)




def sm_price_section_monitor(code, low, high):
    """sm_price_section_monitor | 监控单只股票的价格区间"""
    from debug_a.monitor.single_monitor import price_section_monitor
    price_section_monitor(str(code), float(low), float(high), max_nums=3)


def env_status():
    """env_status | 获取当前的市场涨跌情况"""
    from debug_a.monitor.env_monitor import get_env_status
    get_env_status()


def main():
    cli = {
        "rules": print_rules,
        "psc": sm_price_section_monitor,
        "env": env_status,
    }
    fire.Fire(cli)

if __name__ == "__main__":
    main()

