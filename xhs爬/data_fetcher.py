import os
import time
import random
import pandas as pd
from playwright.sync_api import sync_playwright

# ==================== 配置区域 ====================
# 想要分析的小红书博主主页链接（已更新为您提供的链接）
TARGET_USER_URL = "https://www.xiaohongshu.com/user/profile/5e44d72e0000000001005022?xsec_token=ABLFYqwM5cfC2LmFUjrAYlVNeFv_vNobSvs_TFUTO39cw%3D&xsec_source=pc_search" 
# 模拟向下滚动的次数（次数越多，抓取的历史笔记越多。建议设置为10次以上以拉取更丰富的历史规律）
SCROLL_COUNT = 12 
# ==================================================

# 全局变量，用于存放拦截到的笔记数据
all_notes = []

def handle_response(response):
    """
    核心外挂：拦截小红书向后台请求的笔记列表接口
    直接从小红书服务器返回的 JSON 中拿数据，100% 准确且包含收藏、评论数
    """
    if "api/sns/web/v1/user_posted" in response.url:
        try:
            json_data = response.json()
            notes = json_data.get("data", {}).get("notes", [])
            for note in notes:
                note_id = note.get("note_id")
                title = note.get("display_title", "").strip() or "无标题"
                desc = note.get("desc", "").strip() or ""  # ✨ 核心升级：抓取正文摘要，供AI分类高精度识别
                
                # 提取互动数据
                interact_info = note.get("interact_info", {})
                liked = int(interact_info.get("liked_count", 0))     # 点赞
                collected = int(interact_info.get("collected_count", 0)) # 收藏
                comment = int(interact_info.get("comment_count", 0))   # 评论
                
                # 计算选题潜力得分 (权重：1收藏=2赞，1评论=3赞)
                topic_score = liked * 1 + collected * 2 + comment * 3
                
                note_item = {
                    "笔记ID": note_id,
                    "笔记标题": title,
                    "正文内容": desc,  # ✨ 核心升级：保存正文，无缝对接后续的AI分类看板
                    "点赞数": liked,
                    "收藏数": collected,
                    "评论数": comment,
                    "综合热度值": topic_score,
                    "链接": f"https://www.xiaohongshu.com/explore/{note_id}"
                }
                
                # 去重保存
                if note_item["笔记ID"] not in [x["笔记ID"] for x in all_notes]:
                    all_notes.append(note_item)
                    print(f"🔥 成功捕获数据 -> 【{title[:12]}...】| 赞:{liked} | 藏:{collected} | 评:{comment}")
        except Exception as e:
            # 偶尔有无效请求报错，直接跳过
            pass

def main():
    global all_notes
    user_data_dir = os.path.abspath("./xhs_user_session")
    stealth_js_path = os.path.abspath("./stealth.min.js")

    with sync_playwright() as p:
        print("🤖 正在启动隐身浏览器...")
        # 建立持久化上下文，保存 Cookie 状态
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False, # 设为 False 让你能看见浏览器，方便真人操作和扫码
            args=[
                "--disable-blink-features=AutomationControlled", # 抹除基本特征
                "--no-sandbox"
            ]
        )
        
        page = context.new_page()
        
        # 注入金钟罩 JS，防止小红书风控检测
        if os.path.exists(stealth_js_path):
            page.add_init_script(path=stealth_js_path)
            
        # 注册网络拦截监听器
        page.on("response", handle_response)
        
        # 1. 引导登录
        print("🌐 正在访问小红书，请检查登录状态...")
        page.goto("https://www.xiaohongshu.com")
        page.wait_for_timeout(3000)
        
        # 判断是否需要登录（如果右上角有“登录”按钮或者页面有登录弹窗）
        if "登录" in page.content() or page.locator(".login-container").is_visible():
            print("\n🚨 【重要提示】发现你尚未登录！")
            print("🚨 请在弹出的浏览器窗口中完成【扫码登录】。")
            print("🚨 登录成功并进入首页后，请回到 VS Code 终端按【回车键】继续...")
            input()
        else:
            print("✅ 检测到已登录，正在自动跳过登录环节...")

        # 2. 前往目标博主主页
        print(f"\n🚀 正在前往目标博主主页: {TARGET_USER_URL}")
        page.goto(TARGET_USER_URL)
        page.wait_for_timeout(3000)
        
        # 3. 模拟人类行为向下滚动，触发数据加载
        print(f"🔄 开始模拟真人浏览行为，预计滚动 {SCROLL_COUNT} 次...")
        for i in range(SCROLL_COUNT):
            # 随机滚动距离，模拟人手用滚轮的随机性
            scroll_pixels = random.randint(700, 1100)
            page.evaluate(f"window.scrollBy(0, {scroll_pixels})")
            
            # 极度重要：随机等待 2~4 秒，打破机器人的固定频率，防止被封
            sleep_time = random.uniform(2.0, 4.2)
            print(f"   [第 {i+1}/{SCROLL_COUNT} 次滚动] 歇 {sleep_time:.2f} 秒...")
            page.wait_for_timeout(int(sleep_time * 1000))

        # 关闭浏览器
        context.close()
        
    # 4. 数据分析与导出
    if all_notes:
        print(f"\n📊 抓取结束！共收集到 {len(all_notes)} 篇笔记数据。开始整合基础大盘...")
        df = pd.DataFrame(all_notes)
        
        # 按照综合热度值从高到低排序，直接找出爆款选题
        df = df.sort_values(by="综合热度值", ascending=False)
        
        # ✨ 核心升级：导出为统一的 CSV 格式，编码采用 utf-8-sig，完美兼容 Excel 且无缝对接后续的现代大屏系统
        output_file = "raw_data.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        
        print("-" * 50)
        print(f"🎉 基础数据就绪！已保存在当前文件夹下: {output_file}")
        print("💡 下一步行动：")
        print("   现在您可以直接去运行配置好的高级可视化面板（app.py）了！")
        print("   在终端输入：streamlit run app.py")
        print("-" * 50)
    else:
        print("\n❌ 糟糕，未捕获到有效数据。可能是链接填错，或者滚动时被滑块拦截了，请重试。")

if __name__ == "__main__":
    main()