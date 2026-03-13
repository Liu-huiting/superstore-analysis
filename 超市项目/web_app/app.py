import streamlit as st
import os
from pathlib import Path
import pandas as pd
import base64

# 设置页面
st.set_page_config(
    page_title="超市数据分析平台",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 项目根路径
PROJECT_ROOT = Path(__file__).parent.parent
CODE_DIR = PROJECT_ROOT / "code"
IMAGE_DIR = PROJECT_ROOT / "images"
DOCS_DIR = PROJECT_ROOT / "docs"
DATA_DIR = PROJECT_ROOT / "data"

# 侧边栏导航菜单
st.sidebar.title("📁 项目导航")
menu_choice = st.sidebar.radio(
    "请选择要查看的内容",
    [
        "🏠 项目首页",
        "📊 分析图表", 
        "🐍 分析代码",
        "🗃️ 数据库脚本",
        "📄 项目文档",
        "📁 原始数据"
    ]
)

# 页眉
st.title("🛒 超市销售数据分析平台")
st.markdown("---")

# 1. 项目首页
if menu_choice == "🏠 项目首页":
    st.header("欢迎使用超市数据分析平台")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        ### 📁 项目结构
        本项目包含以下内容：
        
        - **`code/`** - Python分析代码与SQL脚本
        - **`images/`** - 数据分析结果图表
        - **`docs/`** - 项目相关文档
        - **`web_app/`** - 本交互式网站
        
        使用左侧菜单查看详细内容。
        """)
    
    with col2:
        st.success("""
        ### 🔍 快速开始
        
        1. **查看分析结果** → 点击「分析图表」
        2. **了解分析逻辑** → 点击「分析代码」
        3. **查看数据库设计** → 点击「数据库脚本」
        4. **阅读项目说明** → 点击「项目文档」
        """)

# 2. 分析图表页面（修复版）
elif menu_choice == "📊 分析图表":
    st.header("📈 数据分析结果图表")
    
    if not IMAGE_DIR.exists():
        st.error("❌ 找不到图片目录")
    else:
        # 获取所有图片文件
        image_files = []
        for ext in ['.png', '.jpg', '.jpeg']:
            image_files.extend([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(ext)])
        image_files = sorted(image_files)
        
        if not image_files:
            st.warning("⚠️ 未找到图片文件")
        else:
            # 创建标签页
            tab1, tab2 = st.tabs(["📸 选择查看", "🖼️ 全部图表"])
            
            with tab1:
                # 下拉菜单选择图片
                selected_image = st.selectbox("请选择要查看的图表", image_files, key="select_image")
                
                if selected_image:
                    img_path = IMAGE_DIR / selected_image
                    
                    if img_path.exists():
                        # 显示图片标题
                        st.subheader(selected_image.replace('.png', '').replace('_', ' '))
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # 尝试显示图片
                            try:
                                # 使用 base64 编码图片，避免路径问题
                                with open(img_path, "rb") as f:
                                    img_data = f.read()
                                
                                # 获取文件扩展名
                                ext = img_path.suffix.lower()
                                if ext == '.png':
                                    mime_type = 'image/png'
                                elif ext in ['.jpg', '.jpeg']:
                                    mime_type = 'image/jpeg'
                                else:
                                    mime_type = 'image/png'
                                
                                # 显示图片
                                st.image(img_data, caption=selected_image, use_column_width=True)
                                
                            except Exception as e:
                                st.error(f"无法显示图片: {str(e)}")
                                st.info("请下载后查看")
                        
                        with col2:
                            # 文件信息
                            file_size = os.path.getsize(img_path) / 1024
                            st.metric("文件大小", f"{file_size:.1f} KB")
                            
                            # 下载按钮（带唯一key）
                            with open(img_path, "rb") as f:
                                st.download_button(
                                    label="📥 下载",
                                    data=f,
                                    file_name=selected_image,
                                    mime="image/png",
                                    key=f"download_single_{selected_image}"
                                )
                    else:
                        st.error("文件不存在")
            
            with tab2:
                # 显示所有图片（两列布局）
                cols = st.columns(2)
                for i, img_file in enumerate(image_files):
                    img_path = IMAGE_DIR / img_file
                    with cols[i % 2]:
                        # 使用文件名前20个字符作为标题
                        display_name = img_file.replace('.png', '').replace('_', ' ')
                        if len(display_name) > 20:
                            display_name = display_name[:20] + "..."
                        st.subheader(display_name)
                        
                        # 显示图片
                        try:
                            with open(img_path, "rb") as f:
                                img_data = f.read()
                            st.image(img_data, caption=img_file, use_column_width=True)
                        except:
                            st.info("图片预览不可用")
                        
                        # 下载按钮（带唯一key）
                        with open(img_path, "rb") as f:
                            st.download_button(
                                label="📥 下载",
                                data=f,
                                file_name=img_file,
                                mime="image/png",
                                key=f"download_all_{img_file}_{i}"
                            )
                        
                        st.markdown("---")

# 3. 分析代码页面
elif menu_choice == "🐍 分析代码":
    st.header("🐍 Python 分析代码")
    
    if not CODE_DIR.exists():
        st.error("❌ 找不到代码目录")
    else:
        py_files = [f for f in os.listdir(CODE_DIR) if f.endswith('.py')]
        
        if not py_files:
            st.warning("⚠️ 未找到Python文件")
        else:
            selected_file = st.selectbox("选择要查看的Python文件", py_files, key="select_py")
            file_path = CODE_DIR / selected_file
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
                
                st.subheader(f"📄 {selected_file}")
                st.code(code_content, language='python')
                
                with open(file_path, "r", encoding='utf-8') as f:
                    st.download_button(
                        label="📥 下载源码",
                        data=f.read(),
                        file_name=selected_file,
                        mime="text/plain",
                        key=f"download_py_{selected_file}"
                    )
                    
            except Exception as e:
                st.error(f"读取文件时出错: {str(e)}")

# 4. 数据库脚本页面
elif menu_choice == "🗃️ 数据库脚本":
    st.header("🗃️ SQL 数据库脚本")
    
    if not CODE_DIR.exists():
        st.error("❌ 找不到代码目录")
    else:
        sql_files = [f for f in os.listdir(CODE_DIR) if f.endswith('.sql')]
        
        if not sql_files:
            st.warning("⚠️ 未找到SQL文件")
        else:
            selected_file = st.selectbox("选择要查看的SQL文件", sql_files, key="select_sql")
            file_path = CODE_DIR / selected_file
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                st.subheader(f"📄 {selected_file}")
                st.code(sql_content, language='sql')
                
                with open(file_path, "r", encoding='utf-8') as f:
                    st.download_button(
                        label="📥 下载SQL",
                        data=f.read(),
                        file_name=selected_file,
                        mime="text/plain",
                        key=f"download_sql_{selected_file}"
                    )
                    
            except Exception as e:
                st.error(f"读取文件时出错: {str(e)}")

# 5. 项目文档页面
elif menu_choice == "📄 项目文档":
    st.header("📄 项目文档")
    
    if not DOCS_DIR.exists():
        st.warning("⚠️ 文档目录不存在")
    else:
        # 获取文档文件，排除临时文件
        doc_files = [f for f in os.listdir(DOCS_DIR) 
                    if f.endswith('.docx') and not f.startswith('~$')]
        
        if not doc_files:
            st.info("暂无文档")
        else:
            for i, doc_file in enumerate(doc_files):
                file_path = DOCS_DIR / doc_file
                
                st.subheader(f"📄 {doc_file}")
                
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="📥 下载文档",
                        data=f,
                        file_name=doc_file,
                        mime="application/octet-stream",
                        key=f"download_doc_{doc_file}_{i}"
                    )
                
                st.markdown("---")

# 6. 原始数据页面
elif menu_choice == "📁 原始数据":
    st.header("📁 原始数据文件")
    
    if not DATA_DIR.exists():
        st.warning("⚠️ 数据目录不存在")
    else:
        data_files = [f for f in os.listdir(DATA_DIR) if not f.startswith('.')]
        
        if not data_files:
            st.info("数据目录为空")
        else:
            for i, data_file in enumerate(data_files):
                file_path = DATA_DIR / data_file
                
                st.subheader(f"📁 {data_file}")
                
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="📥 下载数据",
                            data=f,
                            file_name=data_file,
                            mime="application/octet-stream",
                            key=f"download_data_{data_file}_{i}"
                        )
                else:
                    st.info("这是一个文件夹")
                
                st.markdown("---")

# 页脚
st.markdown("---")
st.caption("© 2024 超市数据分析平台 | 基于Python + Streamlit构建")