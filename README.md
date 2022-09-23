### 说明介绍
工具基于fofa.info的Api接口编写的一个交互工具，[API](https://fofa.info/api) 细节见官方.

版本的三个主要功能：核心搜索，统计聚合和主机聚合。

### 安装/卸载

```bash
pip install FofaCli
```
```bash
pip uninstall FofaCli
```

### 配置说明

第一次运行需要进行初始化操作

```bash
fofaCli --h
usage: fofaCli [-h] [--init email key]

Command-line interaction tools for fofa.info.

options:
  -h, --help        show this help message and exit
  --init email key  init processes first.

emmmm......
```

```bash
fofaCli --init <fofa_email> <fofa_key> # 第一次初始化
```

```bash
fofaCli # 初始化成功后再次运行进入 cli 控制台
```
#### 命令行交互控制台模式

```bash

cli search(fofa.info/api) > ?

 Global commands:
  show syntax                          搜索引擎支持的搜索语法#2. 快捷键: ctrl + \
  exit                                 退出程序.
  help                                 显示帮助页面.
  ?                                    显示帮助页面.

 re-init app command:
  re-init email <email> key <key>      re-init processes.

 Keyshot support:
  <c-\>                                show syntax, 快捷键命令.
  <c-l>                                last, 快捷键命令
  <c-k>                                sch set fields to normal, 快捷键命令
  <c-j>                                sch set fields to default, 快捷键命令
  <c-i>                                sch set size <num+50>, 快捷键命令,每按一次size加50
  <c-u>                                sch set page <num+1>, 快捷键命令,每按一次page加1
  <c-d>                                sch set size/page <100>/<1> , 快捷键命令,设置size/page为默认值
  <c-p>                                stats sch kw, 快捷键命令
  <c-y>                                sch <syntax...>, 快捷键命令.基于上一次的搜索语法再次搜索.

 Search Command:
  sch <syntax...>                      搜索相关数据,基于搜索语法搜索.(见支持的搜索语法#2)
  sch id <id> <ip==&&port||jarm!=...>  基于搜索结果id值获取值拼接搜索语法搜索(高级用法).
  sch set size <num>                   设置搜索单次结果数据返回的数量. 快捷键: ctrl + i
  sch set page <num>                   设置单页的页码数. 快捷键: ctrl + u
  sch set full <True/False>            设置搜索的数据的时间范围. (True:所有时间,False:最近一年).
  sch show fields                      搜索支持返回的字段值,默认设置返回当前用户支持设置的所有字段(不可修改), body,fid,structinfo除外.#1.
  sch show options                     查看当前设置搜索显示字段值.size, page, full, fileds的设置.

 Search res-related commands:
  sch export <"d:\files.csv">          导出搜索数据到本地文件. "d:\files.csv"
  sch set fields <ip,port,os...>       设置用于展示的数据字段(示例:ctrl + j/k , ctrl + l).见全局支持设置的字段#1 或https://fofa.info/api. 附录1
  sch set fields to normal             快速设置展示的数据字段(快捷键: ctrl + k).值：<ip,port,os,jarm,cert,banner,header,server,country,title,as_organization>.
  sch set fields to default            同上(快捷键: ctrl + j).值：<ip,port,protocol,host,domain,os,server,banner,header,title,city,country,longitude,latitude>.
  last                                 回查执行sch <syntax...> 最后一次搜索的记录. 快捷键: ctrl + l
  view <id>                            查看搜索记录中<id1,id2,id3...>值数据的详细信息.
  view <id> cert                       查看搜索记录中<id1,id2,id3...>值数据对应的<证书>数据详细信息.

 Host Aggs Command:
  host <host/ip>                       基于搜索语法搜索,搜索相关数据,生成聚合信息,获取基础信息和IP标签.
  host sch id <id_num>                 基于search命令返回结果id对于的ip搜索来查询生成聚合信息.
  host show options                    查看host主机的聚合信息设置选项.
  host get last                        获取最后一次搜索的主机聚合信息.

 Stats Aggs Command:
  stats <syntax...>                    基于搜索语法搜索,搜索相关数据,生成全球统计信息,获取统计每个字段的前5排名..见#2
  stats sch kw                         基于search 设置的搜索关键字语法聚合相关数据.快捷键: ctrl + p
  stats show fields                    支持设置聚合统计信息的字段值。#3.
  stats set fields <os,fid,icp...>     设置聚合统计信息的字段值,默认为支持设置的所有字段。见#3.
  stats set fields to all              设置聚合统计信息的字段值为支持设置的所有字段。见#3.
  stats show options                   查看当前设置聚合统计的所有的参数.
  stats get last                       查看聚合最后一次返回的结果.

 User Command:
  info                                 用户信息细节.
```

### Search 功能
[![1.png](https://i.postimg.cc/fWH7HVww/1.png)](https://postimg.cc/Lh1Z56Y7)

#### 指定显示的列

[![2.png](https://i.postimg.cc/Bn8G8Pvt/2.png)](https://postimg.cc/Mn8LNTV8)

#### 查看某些数据细节（多数据对比）

[![3.png](https://i.postimg.cc/MKLrcsNJ/3.png)](https://postimg.cc/BXxCkCJm)

### Stats 功能
支持基于search搜索的语法聚合相关数据，以及基于搜索语法搜索数据聚合
[![4.png](https://i.postimg.cc/fLjbH21V/4.png)](https://postimg.cc/PpJhJ4XH)

### Host 功能
支持基于search搜索的语法聚合主机相关端口数据，以及基于搜索语法搜索数据聚合
[![5.png](https://i.postimg.cc/s2JL25hk/5.png)](https://postimg.cc/VSdgGr4g)


### Search 高级用法
搜索基于搜索出来的某个id的值搜索

[![6.png](https://i.postimg.cc/J4VYLTyT/6.png)](https://postimg.cc/4nPQvQQt)

复杂的请求结构参考

[![7.png](https://i.postimg.cc/pXmWwLFQ/7.png)](https://postimg.cc/qzdHn0Qg)

支持搜索语法细节

[![8.png](https://i.postimg.cc/3xbbP32G/8.png)](https://postimg.cc/TKg9bM72)
### 结尾
程序写的比较匆忙,写的很粗糙，写这个工具主要也是为了快速交互查询一些数据.初衷是为了自动化验证一些POC过程,POC集成自动化和其他脚本框架耦合写的一个快速交互.
