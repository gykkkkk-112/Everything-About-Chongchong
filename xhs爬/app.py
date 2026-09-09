import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import jieba
import re
import os
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from openai import OpenAI

# ==================== AI 客户端配置 ====================
# 推荐使用 DeepSeek，性价比高且对中文分类、总结极其智能化
AI_API_KEY = "YOUR_AI_API_KEY" 
AI_BASE_URL = "https://api.deepseek.com/v1" # 或其他大模型通道
AI_MODEL = "deepseek-chat"

def get_ai_client():
    if AI_API_KEY == "YOUR_AI_API_KEY":
        return None
    return OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)
# =======================================================

st.set_page_config(page_title="博物馆小红书爆款选题数字分析大屏", layout="wide", initial_sidebar_state="expanded")

# CSS 现代美化样式
st.markdown("""
<style>
    .reportview-container { background: #f5f7f9; }
    .metric-card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; }
    .metric-val { font-size: 28px; font-weight: bold; color: #ff2442; }
    .metric-lbl { font-size: 14px; color: #666; }
</style>
""", unsafe_allow_html=True)

# 固定的分类定义
CATEGORIES = ["展览宣传", "展览攻略", "艺术家介绍", "人物采访", "建筑知识", "艺术知识", "活动信息", "招聘", "双年展", "馆藏介绍", "教育活动", "公告", "其他"]

# 数据载入与缓存
@st.cache_data
def load_data():
    if os.path.exists("raw_data.csv"):
        df = pd.read_csv("raw_data.csv")
        if "AI分类" not in df.columns:
            df["AI分类"] = "未分类"
        return df
    return None

df = load_data()

st.title("🏛️ 博物馆小红书选题规律分析与爆款预测系统")
st.caption("基于文本特征挖掘、行为经济加权模型及大语言模型语义分类")

if df is None:
    st.warning("⚠️ 暂未检测到本地历史数据，请先运行 `data_fetcher.py` 抓取数据，或在当前文件夹下准备 `raw_data.csv`。")
else:
    # ==================== 侧边栏及核心控制 ====================
    st.sidebar.header("⚙️ 运营控制台")
    
    # 规则+AI 自动分类触发器
    if st.sidebar.button("🤖 运行 AI 自动分类"):
        client = get_ai_client()
        if not client:
            st.sidebar.error("请先在代码中配置您的 AI_API_KEY")
        else:
            with st.spinner("AI 正在对历史内容进行智能语义分类..."):
                for idx, row in df.iterrows():
                    title = str(row["笔记标题"])
                    desc = str(row["正文内容"])[:200]
                    
                    # 优先进行简易规则判断快速分类
                    assigned_cat = "其他"
                    if "招聘" in title or "加入我们" in title: assigned_cat = "招聘"
                    elif "公告" in title or "闭馆" in title or "开馆" in title: assigned_cat = "公告"
                    elif "攻略" in title or "门票" in title or "预约" in title: assigned_cat = "展览攻略"
                    else:
                        # 规则未命中，调用大模型精准划分类别
                        try:
                            prompt = f"请将下面的小红书笔记标题和正文摘要分类到以下指定类别中的一个，只能输出类别名字，不要任何解释。\n可选类别：{', '.join(CATEGORIES)}\n\n标题：{title}\n正文摘要：{desc}\n类别："
                            response = client.chat.completions.create(
                                model=AI_MODEL,
                                messages=[{"role": "user", "content": prompt}],
                                temperature=0.0,
                                max_tokens=10
                            )
                            res_cat = response.choices[0].message.content.strip()
                            if res_cat in CATEGORIES:
                                assigned_cat = res_cat
                        except:
                            assigned_cat = "其他"
                    df.at[idx, "AI分类"] = assigned_cat
            # 保存分类后的结果
            df.to_csv("raw_data.csv", index=False, encoding="utf-8-sig")
            st.cache_data.clear()
            st.rerun()

    # ==================== 功能二：基础数据统计 ====================
    total_notes = len(df)
    avg_score = round(df["综合热度值"].mean(), 1)
    median_score = round(df["综合热度值"].median(), 1)
    
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="metric-card"><div class="metric-val">{total_notes}</div><div class="metric-lbl">总笔记数量</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_score}</div><div class="metric-lbl">平均综合热度</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><div class="metric-val">{median_score}</div><div class="metric-lbl">中位数热度</div></div>', unsafe_allow_html=True)
    
    st.write("---")
    
    # 标签页分流布局
    tab_stats, tab_ai_cat, tab_title, tab_kv, tab_report = st.tabs(["📊 数据排行与基础统计", "🏷️ 内容AI分类与分析", "✍️ 标题特征规律", "🔑 关键词与词云", "🧠 AI 运营诊断报告"])
    
    # Tab 1: 基础统计与大盘排行榜
    with tab_stats:
        col_rank1, col_rank2 = st.columns(2)
        with col_rank1:
            st.subheader("🏆 综合热度最高 Top 10")
            st.dataframe(df.sort_values(by="综合热度值", ascending=False)[["笔记标题", "点赞数", "收藏数", "评论数", "综合热度值"]].head(10), use_container_width=True)
        with col_rank2:
            st.subheader("📉 综合热度最低 Top 10")
            st.dataframe(df.sort_values(by="综合热度值", ascending=True)[["笔记标题", "点赞数", "收藏数", "评论数", "综合热度值"]].head(10), use_container_width=True)
            
        st.subheader("🔥 完整数据全局排序与检索（支持交互排序）")
        st.dataframe(df[["笔记标题", "点赞数", "收藏数", "评论数", "综合热度值", "AI分类", "链接"]].sort_values(by="综合热度值", ascending=False), use_container_width=True)

    # Tab 2: 功能三 & 功能四：分类统计与人工修正
    with tab_ai_cat:
        st.subheader("🎯 各内容分类流量漏斗与效益分析")
        
        # 计算分类统计指标
        cat_stats = df.groupby("AI分类").agg(
            数量=("综合热度值", "count"),
            平均热度=("综合热度值", "mean"),
            最大热度=("综合热度值", "max"),
            最小热度=("综合热度值", "min")
        ).reset_index()
        
        # 确保所有预设分类都在表格中，没有数据的补0
        for c in CATEGORIES:
            if c not in cat_stats["AI分类"].values:
                cat_stats = pd.concat([cat_stats, pd.DataFrame([{"AI分类": c, "数量": 0, "平均热度": 0, "最大热度": 0, "最小热度": 0}])], ignore_index=True)
        
        cat_stats["平均热度"] = cat_stats["平均热度"].round(1)
        st.dataframe(cat_stats, use_container_width=True)
        # 功能九：数据可视化（饼图 & 柱状图）
        c_vis1, c_vis2 = st.columns(2)
        with c_vis1:
            fig_bar = px.bar(cat_stats, x="AI分类", y="平均热度", text_auto=True, title="📊 不同选题分类的【平均热度】对比（寻找高回报选题）", color="平均热度", color_continuous_scale="Reds")
            st.plotly_chart(fig_bar, use_container_width=True)
        with c_vis2:
            fig_pie = px.pie(cat_stats[cat_stats["数量"]>0], values="数量", names="AI分类", title="🍕 历史发布内容【分类占比】结构", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # 热度分布直方图
        fig_hist = px.histogram(df, x="综合热度值", nbins=30, title="📈 整体账号笔记热度分布直方图（长尾效应VS爆款长相）", color_discrete_sequence=["#ff2442"])
        st.plotly_chart(fig_hist, use_container_width=True)

        # 人工微调修改分类功能
        st.write("---")
        st.subheader("✏️ 人工修正 AI 分类结果")
        st.caption("如果认为 AI 分类不够精准，可在下方手动调整类别：")
        edit_df = df.copy()
        selected_note_title = st.selectbox("选择需要修改分类的笔记：", edit_df["笔记标题"].values)
        current_row = edit_df[edit_df["笔记标题"] == selected_note_title].iloc[0]
        st.info(f"当前分类为：`{current_row['AI分类']}`")
        new_cat = st.selectbox("请选择修正后的分类：", CATEGORIES, index=CATEGORIES.index(current_row['AI分类']) if current_row['AI分类'] in CATEGORIES else 0)
        if st.button("💾 确认保存修改"):
            df.loc[df["笔记标题"] == selected_note_title, "AI分类"] = new_cat
            df.to_csv("raw_data.csv", index=False, encoding="utf-8-sig")
            st.cache_data.clear()
            st.success("分类更新成功！正在刷新大屏数据...")
            st.rerun()

    # ==================== 功能五：标题特征分析 ====================
    with tab_title:
        st.subheader("✍️ 标题文案工程特征解构")
        
        # 特征工程计算
        df["标题长度"] = df["笔记标题"].apply(lambda x: len(str(x)))
        df["含数字"] = df["笔记标题"].apply(lambda x: 1 if re.search(r'\d+', str(x)) else 0)
        df["含问号"] = df["笔记标题"].apply(lambda x: 1 if '?' in str(x) or '？' in str(x) else 0)
        df["含感叹号"] = df["笔记标题"].apply(lambda x: 1 if '!' in str(x) or '！' in str(x) else 0)
        # 简单判定表情符号（Emoji范围广泛，此处用通用正则或长度映射判定）
        df["含emoji"] = df["笔记标题"].apply(lambda x: 1 if re.search(r'[\u2600-\u27BF]|[\u1F300-\u1F64F]|[\u1F680-\u1F6FF]', str(x)) else 0)
        
        # 统计分布
        st.markdown(f"**💡 标题平均长度**：`{round(df['标题长度'].mean(), 1)}` 个字")
        
        def get_feature_comparison(col_name):
            has_feat = df[df[col_name] == 1]["综合热度值"].mean()
            no_feat = df[df[col_name] == 0]["综合热度值"].mean()
            return {
                "特征": col_name,
                "包含该特征的平均热度": round(has_feat, 1) if not np.isnan(has_feat) else 0,
                "不包含该特征的平均热度": round(no_feat, 1) if not np.isnan(no_feat) else 0
            }
            
        feat_data = [get_feature_comparison("含数字"), get_feature_comparison("含问号"), get_feature_comparison("含感叹号"), get_feature_comparison("含emoji")]
        feat_df = pd.DataFrame(feat_data)
        st.dataframe(feat_df, use_container_width=True)
        
        # 可视化特征对比
        fig_feat = go.Figure()
        fig_feat.add_trace(go.Bar(x=feat_df["特征"], y=feat_df["包含该特征的平均热度"], name="包含该特征", marker_color='#ff2442'))
        fig_feat.add_trace(go.Bar(x=feat_df["特征"], y=feat_df["不包含该特征的平均热度"], name="不包含该特征", marker_color='#333333'))
        fig_feat.update_layout(title="🚀 各类文案特征对内容热度的引流效益对比（爆款标题预测指标）", barmode='group')
        st.plotly_chart(fig_feat, use_container_width=True)

    # ==================== 功能六：关键词及词云 ====================
    with tab_kv:
        st.subheader("🔑 标题高频词云与文案词频挖掘")
        
        # 中文分词
        stop_words = ["什么", "可以", "怎么", "如何", "我们", "一封", "关于", "一个", "没有"]
        all_titles_text = " ".join(df["笔记标题"].astype(str).tolist())
        words_list = [w for w in jieba.lcut(all_titles_text) if len(w) > 1 and w not in stop_words]
        
        word_counts = Counter(words_list)
        
        k_col1, k_col2 = st.columns([1, 2])
        with k_col1:
            top_n = st.radio("选择统计范围：", [20, 50])
            kv_df = pd.DataFrame(word_counts.most_common(top_n), columns=["关键词", "词频"])
            st.dataframe(kv_df, use_container_width=True)
        
        with k_col2:
            # 渲染标准词云图并将其注入流式容器中
            if words_list:
                wc = WordCloud(font_path="msyh.ttc" if os.name == 'nt' else "Arial Unicode.ttf", 
                               background_color="white", width=800, height=450, max_words=top_n,
                               colormap="Reds").generate_from_frequencies(word_counts)
                fig, ax = plt.subplots(figsize=(8, 4.5))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.info("数据量过少，无法渲染词云。")

    # ==================== 功能七 & 功能八：热门笔记链接与 AI 总结报告 ====================
    with tab_report:
        st.subheader("🔗 Top 30 热门内容速查（支持直接点击跳转）")
        top_30 = df.sort_values(by="综合热度值", ascending=False).head(30)
        
        # 以超链接Markdown列表美化展示
        for idx, row in top_30.iterrows():
            st.markdown(f"🏆 **[{row['综合热度值']}分]** [{row['笔记标题']}]({row['链接']}) (赞: {row['点赞数']} | 藏: {row['收藏数']} | 评: {row['评论数']}) — *分类: {row['AI分类']}*")
            
        st.write("---")
        st.subheader("🧠 大语言模型大局观：账号运营规律一键自动化诊断")
        
        if st.button("🔥 点击：分析内容规律并发射诊断报告"):
            client = get_ai_client()
            if not client:
                st.error("请先在代码中配置您的 AI_API_KEY")
            else:
                with st.spinner("大模型正在深度联动历史矩阵、加权热度与特征工程，正在生成深度报告..."):
                    # 抽取数据核心摘要喂给大模型
                    summary_data = {
                        "大盘总数": total_notes,
                        "大盘平均热度": avg_score,
                        "分类分布与均分": cat_stats.to_dict(orient="records"),
                        "热门前五标题": df.sort_values(by="综合热度值", ascending=False)["笔记标题"].head(5).tolist(),
                        "文案特征引流排行": feat_df.to_dict(orient="records")
                    }
                    
                    system_prompt = "你是一位资深新媒体战略专家、小红书百万操盘手，擅长文化艺术与博物馆垂直赛道的内容审计与规律挖掘。"
                    user_prompt = f"""
                    请根据以下博物馆小红书账号的真实清洗数据，撰写一篇 500~1000 字的深度分析报告。
                    
                    【清洗核心数据】：
                    {str(summary_data)}
                    
                    【报告必须严密包含以下黄金结构】：
                    1. 核心流量黑马：哪类内容（分类）最容易在小红书斩获超级高热度？其背后的用户心理机制是什么？
                    2. 产能分布矩阵：哪类内容目前数量最多？是否存在“高产量、低回报”的自嗨型选题？
                    3. 潜能红利发现：哪些选题分类虽然目前“数量极少”，但平均表现（热度）异常出色，值得在未来疯狂加码？
                    4. 避坑避雷指南：哪些内容表现极其拉胯或转化极差，应该被战略性缩减？
                    5. 爆款标题文案法则：根据数字、问号、感叹号、emoji 等特征对应的平均热度，总结出该博物馆的爆款标题公式。
                    6. 针对未来的像素级运营改进建议（至少提出 3 条具体可落地的实操建议）。
                    
                    请以专业、一针见血、充满数据说服力的口吻输出。
                    """
                    
                    try:
                        response = client.chat.completions.create(
                            model=AI_MODEL,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.3
                        )
                        report_text = response.choices[0].message.content
                        st.markdown("### 📋 深度运营规律与爆款预测大局报告")
                        st.write(report_text)
                    except Exception as e:
                        st.error(f"报告生成失败，AI接口响应异常：{str(e)}")