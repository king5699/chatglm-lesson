# chatglm-lesson  

此项目利用CogView和CharGLM，开发一个能够进行图像生成和文字聊天的情感陪聊助手，探讨其在心理健康和社交互动中的潜力。

项目分为4个部分  
1. 类型标注介绍与数据类型定义  
2. CogView和CharacterGLM API  
3. 开发图像生成  
4. 角色扮演的聊天机器人  

运行环境：python>=3.8  

依赖库：  
pyjwt  
requests  
streamlit  
zhipuai  
python-dotenv  

[streamlit](https://streamlit.io/) 是一个开源Python库，可以轻松创建和共享用于机器学习和数据科学的漂亮的自定义web应用程序。即使开发者不擅长前端开发，也能快速的构建一个比较漂亮的页面。

characterglm_api_demo_streamlit.py展示了一个具备图像生成和角色扮演能力的聊天机器人。它用streamlit构建了界面，调用CogView API实现文生图，调用CharacterGLM API实现角色扮演。执行下列命令可启动demo，其中--server.address 127.0.0.1是可选参数。

``streamlit run --server.address 127.0.0.1 characterglm_api_demo_streamlit.py``