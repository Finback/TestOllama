import csv
import requests
from tqdm import tqdm
from zoomeye.sdk import ZoomEye
import os
import sys
from requests.exceptions import RequestException

def zoomeye_search(api_key, query='app="Ollama"', max_page=5):
    """ZoomEye API查询功能[3](@ref)"""
    print("\n=== 正在通过ZoomEye API收集Ollama资产 ===")
    
    # 初始化ZoomEye SDK[3](@ref)
    zm = ZoomEye(api_key=api_key)
    results = []
    
    try:
        # 分页获取数据并显示进度[3](@ref)
        with tqdm(total=max_page, desc="ZoomEye搜索进度", unit="页") as pbar:
            for page in range(1, max_page+1):
                resp = zm.dork_search(query, page=page)
                if not resp:
                    break
                
                # 提取关键字段[3,4](@ref)
                for item in resp:
                    result = {
                        'ip': item.get('ip', ''),
                        'port': item.get('port', ''),
                        'service': item.get('service', ''),
                        'url': f"http://{item['ip']}:{item['port']}",
                        'timestamp': item.get('timestamp', '')
                    }
                    results.append(result)
                
                pbar.update(1)
                pbar.set_postfix_str(f"已获取{len(results)}条记录")
                
        return results
    except Exception as e:
        print(f"ZoomEye查询失败: {str(e)}")
        return []

def save_to_csv(data, filename='a.csv'):
    """保存ZoomEye结果到CSV"""
    if not data:
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"CSV保存失败: {str(e)}")
        return False

def main():
    # 配置ZoomEye API-KEY（建议通过环境变量设置）
    ZOOMEYE_API_KEY = os.getenv('ZOOMEYE_API_KEY') or input("请输入ZoomEye API KEY: ")
    
    # 执行ZoomEye查询
    ollama_assets = zoomeye_search(ZOOMEYE_API_KEY)
    
    if save_to_csv(ollama_assets):
        print(f"\n成功保存{len(ollama_assets)}条记录到a.csv")
    else:
        print("\n资产保存失败，请检查权限或磁盘空间")
        return
    
    # 等待用户确认
    input("\n任务完成，按任意键开始检测...\n")
    
    # 执行原有检测流程
    process_urls(input_file='a.csv', output_file='b.csv')

if __name__ == "__main__":
    main()