def transform_location(chinese_city):
    # 中文到英文的城市名映射表
    city_dict = {
        '北京': 'Beijing',
        '上海': 'Shanghai',
        '广州': 'Guangzhou',
        '深圳': 'Shenzhen',
        '成都': 'Chengdu',
        '杭州': 'Hangzhou',
        '巴塞尔': 'Basel',
        '苏黎世': 'Zurich',
        # 添加更多的城市映射...
    }

    # 1. 尝试完全匹配
    if chinese_city in city_dict:
        return city_dict[chinese_city]
    
    # 2. 尝试子串匹配（例如"杭州西湖"中包含"杭州"）
    for key, value in city_dict.items():
        if key in chinese_city:
            return value
            
    # 3. 如果都匹配不到，直接返回原始值（由后端数据库或LLM兜底），不再返回错误提示字符串
    return chinese_city