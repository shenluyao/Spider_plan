import time
import os
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .colors import print_info, print_success, print_error, print_warning
from .pdf import save_as_pdf


def get_training_plans_via_js_api(driver, config):
    """
    通过浏览器的JavaScript fetch API获取培养方案数据
    这样可以自���处理VPN代理和cookies
    """
    print_info("Getting training plans via JavaScript fetch API...")
    
    # 确保在iframe中
    driver.switch_to.default_content()
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        driver.switch_to.frame(iframes[0])
    
    try:
        # 使用JavaScript执行fetch请求获取数据
        js_code = f"""
        return fetch('/jwglxt/pyfagl/pyfaxxcx_cxPyfaxscxIndex.html?doType=query&gnmkdm=N153020', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            }},
            body: new URLSearchParams({{
                'nj': '{config.get("year", "2025")}',
                'doType': 'query',
                'queryModel.showCount': '500',
                'queryModel.currentPage': '1'
            }}).toString()
        }})
        .then(response => response.json())
        .then(data => JSON.stringify(data))
        .catch(error => JSON.stringify({{error: error.toString()}}));
        """
        
        # 使用async script执行
        result = driver.execute_script(f"return (async () => {{ {js_code} }})()")
        
        if result:
            data = json.loads(result)
            if "error" not in data and "items" in data:
                print_success(f"Successfully retrieved {len(data['items'])} training plans via JS API")
                return data.get("items", [])
            else:
                print_warning(f"API returned error or no items: {data}")
        
    except Exception as e:
        print_error(f"JavaScript fetch failed: {e}")
    
    return None


def navigate_to_training_plan_page(driver):
    """
    通过JavaScript直接调用网站的导航函数来跳转到培养方案页面
    """
    print_info("Attempting to navigate to Training Plan page via JS function...")
    
    # 首先确保在主文档中
    driver.switch_to.default_content()
    
    # 检查是否有iframe，如果有则进入
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print_info(f"Found {len(iframes)} iframe(s), switching to first one...")
        driver.switch_to.frame(iframes[0])
    
    try:
        # 直接调用网站的onClickMenu函数
        driver.execute_script("onClickMenu('/pyfagl/pyfaxxcx_cxPyfaxscxIndex.html','N153020');")
        print_success("Called onClickMenu function successfully!")
        time.sleep(3)
        return True
    except Exception as e:
        print_warning(f"onClickMenu call failed: {e}")
    
    # 如果JS函数调用失败，尝试点击元素
    try:
        element = driver.find_element(By.XPATH, "//div[@title='培养方案-培养方案查询']")
        driver.execute_script("arguments[0].click();", element)
        print_success("Clicked training plan button via element click!")
        time.sleep(3)
        return True
    except Exception as e:
        print_warning(f"Element click failed: {e}")
    
    return False


def wait_for_table_and_get_plans(driver, config):
    """
    等待表格加载并获取培养方案列表
    """
    print_info("Waiting for training plan table to load...")
    
    # 重新进入iframe
    driver.switch_to.default_content()
    time.sleep(2)
    
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        driver.switch_to.frame(iframes[0])
    
    try:
        # 等待表格出现
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "tabGrid"))
        )
        print_success("Training plan table loaded!")
        
        # 获取所有预览按钮
        preview_buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn-preview")
        
        if not preview_buttons:
            preview_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '预览')]")
        
        if preview_buttons:
            print_info(f"Found {len(preview_buttons)} training plans")
            
            # 收集row_ids
            row_ids = []
            for btn in preview_buttons:
                row_id = btn.get_attribute("data-rowid")
                if row_id:
                    row_ids.append(row_id)
            
            return row_ids
        else:
            print_warning("No preview buttons found")
            return []
            
    except Exception as e:
        print_error(f"Error waiting for table: {e}")
        return []


def save_plan_as_pdf(driver, config, row_id, original_window):
    """
    点击预览按钮并保存为PDF
    """
    print_info(f"Processing plan: {row_id}")
    
    # 确保在正确的iframe中
    driver.switch_to.default_content()
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        driver.switch_to.frame(iframes[0])
    
    try:
        # 找到并点击预览按钮
        btn = driver.find_element(By.CSS_SELECTOR, f"button.btn-preview[data-rowid='{row_id}']")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(3)
        
        # 检查是否打开了新窗口
        if len(driver.window_handles) > 1:
            # 切换到新窗口
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    break
            
            print_info("Switched to preview window")
            time.sleep(2)
            
            # 保存为PDF
            output_dir = config.get("output_dir", "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            pdf_path = os.path.join(output_dir, f"TrainingPlan_{row_id}.pdf")
            save_as_pdf(driver, pdf_path)
            
            # 关闭预览窗口并切回
            driver.close()
            driver.switch_to.window(original_window)
            print_success(f"Saved: {pdf_path}")
            return True
        else:
            print_warning("Preview did not open in new window")
            return False
            
    except Exception as e:
        print_error(f"Error processing plan {row_id}: {e}")
        return False


def fetch_training_plans(driver, config):
    """
    主函数：获取培养方案并保存为PDF
    """
    print_info("Starting to fetch training plans...")
    
    original_window = driver.current_window_handle
    
    # 方法1: 尝试通过JavaScript直接导航
    if navigate_to_training_plan_page(driver):
        print_info("Navigation successful, waiting for content...")
        time.sleep(3)
        
        # 方法1a: 先尝试通过API获取数据
        plans_data = get_training_plans_via_js_api(driver, config)
        
        if plans_data:
            print_success(f"Got {len(plans_data)} plans via API")
            # 保存为JSON作为备份
            output_dir = config.get("output_dir", "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            json_path = os.path.join(output_dir, "training_plans.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(plans_data, f, ensure_ascii=False, indent=2)
            print_success(f"Saved plans data to {json_path}")
        
        # 方法1b: 再尝试等待表格并逐个保存PDF
        row_ids = wait_for_table_and_get_plans(driver, config)
        
        if row_ids:
            print_info(f"Will process {len(row_ids)} training plans...")
            
            # 限制处理数量
            max_plans = config.get("max_plans", 3)
            row_ids_to_process = row_ids[:max_plans]
            
            print_info(f"Processing first {len(row_ids_to_process)} plans...")
            
            for i, row_id in enumerate(row_ids_to_process):
                print_info(f"Processing {i+1}/{len(row_ids_to_process)}: {row_id}")
                save_plan_as_pdf(driver, config, row_id, original_window)
                time.sleep(1)
            
            print_success(f"Completed processing {len(row_ids_to_process)} training plans")
        else:
            print_warning("No training plans found in table")
    else:
        print_error("Failed to navigate to training plan page")

