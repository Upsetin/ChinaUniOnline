# GUI模式的使用  

## 依赖  

需要的依赖都放在`requirements.txt`文件里面，可以直接使用`pip install -r requirements.txt`安装。下载速度缓慢可以加入参数`-i https://pypi.tuna.tsinghua.edu.cn/simple`以使用清华的镜像加速  

## 用法

没有提供可执行程序，安装完成依赖后执行`python main-gui.py`即可。在Python 3.9.2版本上实验通过，可以运行。纯GUI程序，Linux下运行需要正常的桌面环境。

## 关闭网页登陆后的处理方法

1. 手机上安装并配置抓包程序，个人使用平行空间+HttpCanary，接下来的步骤均以此为例  
2. 将微信安装至平行空间
3. 打开HttpCanary,设置目标程序为平行空间和平行空间的64位运行环境，没有使用64位微信的可以不用设置目标程序为64位运行环境，开启抓包
4. 启动平行空间内的微信，在微信上正常登陆小程序并进入小程序的用户页面
5. 回到抓包程序，这时应该有相当多的连接请求记录
6. 在记录里面从上往下寻找一条目标地址为 <https://ssxx.univs.cn/cgi-bin/authorize/token/> 的GET请求记录，带有URL参数 t,uid,avatar,activity_id ,查看响应预览
7. 预览应该为一个JSON文档，其中token和refresh_token为所需数据，填入程序设置界面对应位置即可。后面将想办法实现这一过程的自动化

## UID获取方法

方法1：在上面第 6 步的请求参数中uid参数的值就是所需的UID。有UID的情况下优先使用UID获取Token完成登陆  
方法2：找到 <https://ssxx.univs.cn/cgi-bin/portal/user/> 的GET记录，带有参数t，响应预览的data下的id的值也是UID  
上面的方法选择一个即可

## 注意

刷题程序登陆时不要在另外的地方登陆（比如微信什么的），要不然脚本会被服务器踢掉
