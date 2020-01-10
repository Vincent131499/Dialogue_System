---
layout:     post
title:      NLP中的对话系统
subtitle:   针对各个细领域及相关技术进行介绍
date:       2020-01-10
author:     MeteorMan
header-img: img/jarvis_system.jpg
catalog: true
tags:
    - Natural Language Processing
    - Dialogue System
    - Personal Assistant



---

>For you always, sir.

​		每次与公司同事和实验室组员谈及对话系统这个话题，我的内心都非常激动，因为太爱这个领域，或许是受到了钢铁侠管家“贾维斯”的影响，毕竟我最爱的漫威英雄是Iron Man。在研究和工作的业余时间，我也在继续研究这个领域，在知识图谱、自然语言理解、自然语言生成、闲聊系统都有所涉猎。本文主要是对Dialogue System及及相关技术进行介绍。

# 1.对话系统概述

​		根据应用领域类型可将对话系统划分为两种类型：开放域对话系统与限定域对话系统，其中开放域对话系统大多谈及的是闲聊系统，限定域对话系统大多谈及的是针对专业领域的问答系统，如KBQA、KGQA。

​		根据任务类型可将对话系统划分为以下类型：

- Retrieval_QA/检索式问答
- KBQA/基于知识库的问答
- KGQA/知识图谱问答
- MRC/机器阅读理解
- Chat_System/闲聊系统		

​		在技术方面，一个完美的对话系统应该如下图所示，包括NLU（自然语言理解）模型、DST（对话状态追踪）模块、DPL（对话策略学习）模块以及NLG（自然语言生成）模块。然而目前大多数对话系统仅采用了NLU模块，对于其它三个模块并未深入涉及。