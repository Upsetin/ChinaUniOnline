# 第三方内容开发文档

## 样式

所有内容都是文本型字符串，大部分是Qt Style Sheet字符串并将在启动GUI时加载到对应部件。关键词如下：  

### 样式关键词

1. `avatar` 用户信息的QSS样式
2. `bootstrap` 生成题库按钮的QSS样式
3. `control_close` 关闭按钮的QSS样式
4. `control_max` 最大化按钮的QSS样式
5. `control_min` 最小化按钮的QSS样式
6. `icon` 图标位置，相对于脚本文件夹
7. `logger` 日志输出框的QSS样式
8. `logging_datefmt` logging的日期格式
9. `logging_fmt` logging的日志格式
10. `main` 保留关键字
11. `name` 样式名称
12. `opacity` 程序GUI透明度
13. `qr` 用于二维码显示的QLabel的QSS样式
14. `qr_title` 用于二维码显示的标题QLabel的QSS样式
15. `setting` 设置界面部件的样式
    1. `check_box` 单选框的QSS样式
    2. `combo_box` 下拉框的QSS样式
    3. `control_close` 关闭按钮的QSS样式
    4. `group_box` 分组框的QSS样式
    5. `label` 标签的QSS样式
    6. `line_edit` 输入框的QSS样式
    7. `title` 设置界面标题的QSS样式
16. `setting_button` 设置按钮的QSS样式
17. `setting_window` 设置窗口的QSS样式
18. `size` 窗口大小，分别为宽度和高度
19. `start_button` 开始按钮的QSS样式
20. `title` 主界面标题的QSS样式
21. `tray` 托盘图标位置，相对于脚本文件夹
22. `tray_exit_icon` 托盘退出菜单的图标位置，相对于脚本文件夹
23. `tray_menu` 托盘菜单的QSS样式
24. `tray_show_icon` 托盘显示主界面菜单的图标位置，相对于脚本文件夹
25. `extra_data` 额外的数据，键名为文件名，键值为base64编码的文件内容，导入样式时这部分将自动还原为文件并放置在样式文件夹

### 样式示例

参考程序生成的默认样式

## 模块

模块是json文档，执行答题处理器时将自行加载。文件名即模块id，加载顺序按文件名字母顺序排序。目前已开放的功能如下：

### 模块关键词

1. `name` 模块的名称
2. `author` 模块的作者
3. `type` 模块的类型，现支持远程通知发送模块，类型为`notifier`
4. `enabled` 模块是否启用
5. `token` 模块api的认证信息
6. `method` 请求方法，支持requests支持的全部方法，一般为`GET`或者`POST`
7. `params` URL参数，可选
8. `data` POST请求的表单数据，可选
9. `json` POST请求的payload数据，可选
10. `{msg}` 指代发送的消息内容
11. `{token}` 指代token
12. `api` 请求的api地址
13. `id` 模块的ID，要求不能重复，可选，不填写会以文件名为ID

### 模块示例

```json
{
    "enabled": true,
    "token": "",
    "method": "POST",
    "api": "https://qmsg.zendee.cn/send/{token}",
    "name": "Qmsg酱通知模块",
    "params": {
        "qq": "",
        "msg": "{msg}"
    },
    "type": "notifier",
    "author": "ChinaUniOnlineGUI"
}
```

将正确的Token和QQ信息填入后保存为json文件即可实现完成后通过Qmsg酱发送完成通知到设置的QQ号

**警告**：使用第三方内容可能存在难以预知的安全或者稳定性方面的问题，如果在使用过程中碰到问题，请向内容作者反馈。我们只能保证这个文档提到的示例模块是可以正常使用的。
