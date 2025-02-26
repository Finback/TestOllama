import csv
import requests
from tqdm import tqdm
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def process_single_url(original_url, lock, pbar):
    # 拼接API路径
    target_url = original_url.rstrip('/') + '/api/tags'
    status_code = 'ERROR'
    result = ""
    
    try:
        response = requests.get(target_url, timeout=5)
        status_code = response.status_code
        result = response.text[:500]
    except RequestException as e:
        result = f"请求失败: {str(e)}"
    except Exception as e:
        result = f"未知错误: {str(e)}"
    
    # 线程安全的数据写入
    with lock:
        with open('b1.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                original_url,
                target_url,
                status_code,
                result.replace('\n', ' ')
            ])
    
    # 更新进度条
    pbar.update(1)
    pbar.set_postfix_str(f"当前处理: {original_url[:20]}...")
    return original_url

def process_urls(input_file='a1.txt', max_workers=20):
    # 初始化线程锁和进度条
    lock = threading.Lock()
    
    # 读取URL列表
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    # 创建CSV文件并写入表头
    with open('b1.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['原始URL', '处理后的URL', '响应状态码', '响应内容'])
    
    # 创建进度条
    with tqdm(total=len(urls), desc="处理进度", unit="URL") as pbar:
        # 使用线程池
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_single_url, url, lock, pbar): url for url in urls}
            
            # 等待所有任务完成
            for future in as_completed(futures):
                future.result()

if __name__ == "__main__":
    process_urls()