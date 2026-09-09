const defaultTargets = ["GRE备考", "看电影", "健身", "写公众号", "做作品集", "学习Max", "玩游戏"];
let currentTargets = [...defaultTargets];

document.addEventListener("DOMContentLoaded", () => {
    // 初始化DOM
    const form = document.getElementById("planner-form");
    const targetInput = document.getElementById("target-input");
    const addTagBtn = document.getElementById("add-tag-btn");
    const tagsContainer = document.getElementById("tags-container");
    
    const outputPlaceholder = document.getElementById("output-placeholder");
    const outputLoading = document.getElementById("output-loading");
    const outputContent = document.getElementById("output-content");
    const anxietyAlert = document.getElementById("anxiety-alert");
    
    const statTotalDays = document.getElementById("stat-total-days");
    const statFreeTime = document.getElementById("stat-free-time");
    const priorityList = document.getElementById("priority-analysis-list");
    const mainTracksContainer = document.getElementById("main-tracks-container");
    const weeklySuggestionsList = document.getElementById("weekly-suggestions-list");
    const achievementContainer = document.getElementById("achievement-system-container");
    
    const btnCopy = document.getElementById("btn-copy");
    const btnClear = document.getElementById("btn-clear");
    const submitBtn = document.getElementById("submit-btn");

    initDates();
    loadFromLocalStorage();
    renderTags();

    targetInput.addEventListener("keypress", (e) => { if (e.key === "Enter") { e.preventDefault(); addTag(); } });
    addTagBtn.addEventListener("click", addTag);

    // 表单提交：发起真 AI 规划
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const apiKey = document.getElementById("api-key").value.trim();
        if (!apiKey) {
            alert("请先在左侧下方输入有效的 Gemini API Key 才能开始真正的 AI 规划。");
            return;
        }

        // 保存当前输入
        saveInputsToLocalStorage();

        // 切换到 Loading 状态
        outputPlaceholder.style.display = "none";
        outputContent.style.display = "none";
        outputLoading.style.display = "block";
        submitBtn.disabled = true;
        submitBtn.innerText = "Gemini 正在量子推演中...";

        // 收集参数
        const startDate = document.getElementById("start-date").value;
        const endDate = document.getElementById("end-date").value;
        const fixedEvents = document.getElementById("fixed-events").value;
        const timeInvestment = document.getElementById("time-investment").options[document.getElementById("time-investment").selectedIndex].text;
        const selfEval = document.getElementById("self-eval").options[document.getElementById("self-eval").selectedIndex].text;

        // 计算基础数据
        const days = Math.ceil(Math.abs(new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24)) + 1;

        // 组装高级 Prompt
        const prompt = `
你是一个专门帮助大学生、自由职业者和严重拖延症患者对抗焦虑、温和推进目标的心理学假期规划专家。
你的核心理念不是“高强度自律”，而是“帮助用户在有限精力下持续推进真正重要的事情”。

请结合以下用户输入，为他定制一个【极其温柔、低摩擦、充满电影手账质感】的假期规划：
- 假期时间：从 ${startDate} 到 ${endDate} (共计 ${days} 天)
- 已经被固定占用的事项：${fixedEvents}
- 假期想要推进的目标池：${currentTargets.join("、")}
- 用户每周愿意投入的时间预算档位：${timeInvestment}
- 用户的自我评价与现状：${selfEval}

请严格遵守你的核心理念。不要提供精细到每天、每小时的死板日程表。请根据用户想完成的具体目标，发挥你强大的知识库，对这些目标进行真正的解构和重新组织（比如，如果你发现用户写了“学习Max”，你应该知道这是3D或音频软件，并针对性地解构它的最低/标准/超额完成版）。

请严格按照以下 JSON Schema 要求的格式返回数据，不要包含任何 markdown 标记（如 \`\`\`json）：
{
  "anxietyAlert": "字符串。如果目标明显过多或者精力过低，用极其温柔的语气提供一句心理按摩和防内耗提醒。如果目标数量合理，请返回空字符串",
  "energyModel": "字符串。简短描述他的精力预算模型，比如：'每周约 10 小时 × 4周 (轻量微光模式)'",
  "priorities": ["数组。包含 2-3 条对目前目标池的优先级深度洞察，指出哪个是核心锚点，哪个可以作为低摩擦起步，语气要像电影日记般优雅"],
  "mainTracks": [
    { "title": "主线A的名称", "desc": "对主线A的浪漫化、内耗极低的解释" },
    { "title": "主线B的名称", "desc": "对主线B的浪漫化、内耗极低的解释" },
    { "title": "主线C的名称", "desc": "对主线C的浪漫化、内耗极低的解释" }
  ],
  "weeklySuggestions": ["数组。包含 3-5 条本周内的弹性行动建议，使用模糊定量，如：'看1-2部电影'、'翻开GRE词汇哪怕只看5分钟'，而非指定具体日子"],
  "achievements": [
    {
      "targetName": "解构的目标名称(挑出最核心的2-3个目标进行解构)",
      "low": "最低完成版：摸到就算赢的超低门槛（如：写下一行标题、拉伸3分钟）",
      "std": "标准完成版：正常状态下的推进成果",
      "max": "超额完成版：心流爆发、状态极佳时的天花板成果"
    }
  ]
}
`;

        try {
            // 调用官方 Gemini API 端点 (使用 gemmini-2.5-flash 模型，速度最快、性价比最高)
            const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    contents: [{ parts: [{ text: prompt }] }],
                    generationConfig: {
                        responseMimeType: "application/json" // 强迫 Gemini 吐出纯 JSON
                    }
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error?.message || "请求失败");
            }

            const resData = await response.json();
            const aiRawText = resData.candidates[0].content.parts[0].text;
            const plan = JSON.parse(aiRawText); // 解析 AI 返回的优雅 JSON

            // --- 渲染 AI 的真正智慧到前端 ---
            statTotalDays.innerText = days;
            statFreeTime.innerText = plan.energyModel;

            // 防焦虑提醒
            if (plan.anxietyAlert) {
                anxietyAlert.innerHTML = `⚠️ <strong>防焦虑诊断</strong>：${plan.anxietyAlert}`;
                anxietyAlert.style.display = "block";
            } else {
                anxietyAlert.style.display = "none";
            }

            // 优先级列表
            priorityList.innerHTML = plan.priorities.map(p => `<li>${p}</li>`).join("");

            // 三条主线
            mainTracksContainer.innerHTML = plan.mainTracks.map(t => `
                <div class="track-card">
                    <div class="track-title">${t.title}</div>
                    <div class="track-desc">${t.desc}</div>
                </div>
            `).join("");

            // 每周建议
            weeklySuggestionsList.innerHTML = plan.weeklySuggestions.map(s => `<li>${s}</li>`).join("");

            // 成就矩阵拆解
            achievementContainer.innerHTML = plan.achievements.map(a => `
                <div class="achieve-card">
                    <div class="achieve-target-name">🎯 ${a.targetName}</div>
                    <div class="level-row level-low"><strong>[最低版]:</strong> ${a.low}</div>
                    <div class="level-row level-std"><strong>[标准版]:</strong> ${a.std}</div>
                    <div class="level-row level-max"><strong>[超额版]:</strong> ${a.max}</div>
                </div>
            `).join("");

            // 切换状态显示
            outputLoading.style.display = "none";
            outputContent.style.display = "block";
            btnCopy.style.display = "inline-block";

        } catch (error) {
            console.error(error);
            alert("AI 生成失败，请检查你的 Gemini API Key 是否输入正确，或网络是否可以畅通连接到 Google 节点。错误信息：" + error.message);
            outputLoading.style.display = "none";
            outputPlaceholder.style.display = "block";
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerText = "让 Gemini 帮我解构计划...";
        }
    });

    // --- 基础辅助函数 ---
    function initDates() {
        const today = new Date();
        const nextMonth = new Date();
        nextMonth.setMonth(today.getMonth() + 1);
        document.getElementById("start-date").value = today.toISOString().split('T')[0];
        document.getElementById("end-date").value = nextMonth.toISOString().split('T')[0];
    }

    function addTag() {
        const value = targetInput.value.trim();
        if (value && !currentTargets.includes(value)) {
            currentTargets.push(value);
            renderTags();
            targetInput.value = "";
            saveInputsToLocalStorage();
        }
    }

    window.removeTag = function(index) {
        currentTargets.splice(index, 1);
        renderTags();
        saveInputsToLocalStorage();
    }

    function renderTags() {
        tagsContainer.innerHTML = "";
        currentTargets.forEach((target, index) => {
            const tagEl = document.createElement("span");
            tagEl.className = "tag";
            tagEl.innerHTML = `${target} <span class="remove-tag" onclick="removeTag(${index})">&times;</span>`;
            tagsContainer.appendChild(tagEl);
        });
    }

    function saveInputsToLocalStorage() {
        const data = {
            startDate: document.getElementById("start-date").value,
            endDate: document.getElementById("end-date").value,
            fixedEvents: document.getElementById("fixed-events").value,
            timeInvestment: document.getElementById("time-investment").value,
            selfEval: document.getElementById("self-eval").value,
            targets: currentTargets,
            apiKey: document.getElementById("api-key").value.trim() // API key 留存在用户本地
        };
        localStorage.setItem("vibe_planner_inputs", JSON.stringify(data));
    }

    function loadFromLocalStorage() {
        const saved = localStorage.getItem("vibe_planner_inputs");
        if (saved) {
            const data = JSON.parse(saved);
            document.getElementById("start-date").value = data.startDate;
            document.getElementById("end-date").value = data.endDate;
            document.getElementById("fixed-events").value = data.fixedEvents || "";
            document.getElementById("time-investment").value = data.timeInvestment;
            document.getElementById("self-eval").value = data.selfEval;
            if (data.targets) currentTargets = data.targets;
            if (data.apiKey) document.getElementById("api-key").value = data.apiKey;
        }
    }

    // 复制文本功能
    btnCopy.addEventListener("click", () => {
        const text = document.getElementById("output-content").innerText;
        navigator.clipboard.writeText(text).then(() => {
            alert("高颜值文本计划已复制到剪贴板！");
        });
    });
});