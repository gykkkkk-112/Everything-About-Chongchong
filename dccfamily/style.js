/**
 * ==========================================================================
 * 1. 模拟本地历史档案数据库 (Mock Local Data)
 * ==========================================================================
 */
const mockFamilyDatabase = {
    "1": {
        name: "顾长风",
        role: "祖父 / 寻路者",
        years: "1912 — 1988",
        photo: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?q=80&w=600",
        bio: "生于江南水乡，后于动荡年代北上。留下一本写满航海日志与家书的旧牛皮纸本。他一生的大部分时间都在地图与海浪之间度过，把最后的安宁留在了这座北方小城。"
    },
    "2": {
        name: "苏曼华",
        role: "祖母 / 守护者",
        years: "1918 — 2005",
        photo: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=600",
        bio: "精通刺绣与诗书，在战火与数次搬迁中，紧紧保存了家族最后的照相簿与十六封珍贵书信。她是整个家族记忆不曾断绝的坚韧纽带。"
    }
};

/**
 * ==========================================================================
 * 2. 核心DOM节点获取
 * ==========================================================================
 */
const enterBtn = document.getElementById('enterBtn');
const heroSection = document.getElementById('hero');
const mainArchive = document.getElementById('mainArchive');

const memberCards = document.querySelectorAll('.member-card');
const archiveDrawer = document.getElementById('archiveDrawer');
const drawerOverlay = document.getElementById('drawerOverlay');
const closeBtn = document.getElementById('closeBtn');
const drawerBody = document.getElementById('drawerBody');

/**
 * ==========================================================================
 * 3. 交互逻辑事件监听
 * ==========================================================================
 */

// 动画切场：从落页淡入档案展厅
enterBtn.addEventListener('click', () => {
    heroSection.style.transition = 'opacity 1.2s ease';
    heroSection.style.opacity = '0';
    
    setTimeout(() => {
        heroSection.classList.add('hidden');
        mainArchive.classList.remove('hidden');
        // 自动滚动到展厅顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 1200);
});

// 展开人物详细档案 (利用事件中的 data-member 属性联动假数据)
memberCards.forEach(card => {
    card.addEventListener('click', () => {
        const memberId = card.getAttribute('data-member');
        const data = mockFamilyDatabase[memberId];
        
        if (data) {
            // 动态构建 HTML 内部解耦注入
            drawerBody.innerHTML = `
                <div class="drawer-data-photo">
                    <img src="${data.photo}" alt="${data.name}">
                </div>
                <h2>${data.name}</h2>
                <div class="drawer-subtitle">${data.role} (${data.years})</div>
                <p class="drawer-bio">${data.bio}</p>
            `;
            // 激活侧边抽屉样式
            archiveDrawer.classList.add('active');
        }
    });
});

// 关闭个人档案卡函数
function closeDrawer() {
    archiveDrawer.classList.remove('active');
}

closeBtn.addEventListener('click', closeDrawer);
drawerOverlay.addEventListener('click', closeDrawer);