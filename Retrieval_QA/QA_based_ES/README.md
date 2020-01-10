# ES_based_QA
基于ES构建的一个简单的检索式问答系统，主要用来学习下python相关的ES操作

## 环境依赖：
* Python3.6+<br>
* java1.8+<br>
* elasticsearch2.4.4-win（这个是在windows上的安装包版本，可根据这个[教程](https://www.cnblogs.com/ljhdo/p/4887557.html)进行安装）<br>
* elasticsearch5.5.3<br>

## 数据来源
共20多万问答对，数据来源于华律网（一个法务咨询的专用网站）。

## Run
当以上依赖都安装好后，即可根据以下步骤体验到ES检索式问答的乐趣。<br>

### Step1：将知识库导入ES数据库
```Python
python build_qa_database.py
```

### Step2：问答检索
```Python
python law_qa.py
```
运行效果如下图：<br>
![运行效果](https://github.com/Vincent131499/ES_based_QA/raw/master/imgs/model_predict_demo.jpg)

Note:在law_qa.py文件中的search_specific()函数实现的query_body，可直接根据下图在线生成：<br>
![query_json_generate](https://github.com/Vincent131499/ES_based_QA/raw/master/imgs/query_json.jpg)

## 参考资料
[1] https://www.cnblogs.com/shaosks/p/7592229.html<br>
[2] https://www.cnblogs.com/ljhdo/p/4887557.html<br>
